from __future__ import annotations

import abc
import asyncio
import datetime
from typing import TYPE_CHECKING, Awaitable, Callable, Literal

from typing_extensions import Self

from easynats.core import Msg, MsgImpl, SubscriptionHandler

from ..models.api.common._parser import encode_nanoseconds_timedelta, parse_utc_rfc3339
from ..models.api.common.consumer_configuration import ConsumerConfig
from ..models.api.common.consumer_info import ConsumerInfo
from ..models.api.common.consumer_state import ConsumerState
from ..models.api.consumer_create import ConsumerCreateResponse
from ..models.api.consumer_info import ConsumerInfoResponse

if TYPE_CHECKING:
    from ..api import JetStreamClient


class PendingMessage(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def subject(self) -> str:
        ...

    @abc.abstractmethod
    def data(self) -> bytes:
        ...

    @abc.abstractmethod
    def stream_sequence(self) -> int:
        ...

    @abc.abstractmethod
    def consumer_sequence(self) -> int:
        ...

    @abc.abstractmethod
    def timestamp(self) -> datetime.datetime:
        ...

    @abc.abstractmethod
    async def ack(self) -> None:
        ...

    @abc.abstractmethod
    async def nak(self, delay: float | None = None) -> None:
        ...

    @abc.abstractmethod
    async def term(self) -> None:
        ...

    @abc.abstractmethod
    async def in_progress(self) -> None:
        ...


class PendingMessageImpl(PendingMessage):
    def __init__(self, msg: MsgImpl) -> None:
        self.msg = msg

    def subject(self) -> str:
        return self.msg.nats_msg.subject

    def data(self) -> bytes:
        return self.msg.nats_msg.data

    def stream_sequence(self) -> int:
        return self.msg.nats_msg.metadata.sequence.stream

    def consumer_sequence(self) -> int:
        return self.msg.nats_msg.metadata.sequence.consumer

    def timestamp(self) -> datetime.datetime:
        return self.msg.nats_msg.metadata.timestamp

    async def ack(self) -> None:
        await self.msg.nats_msg.ack()

    async def nak(self, delay: float | None = None) -> None:
        await self.msg.nats_msg.nak(delay=delay)

    async def term(self) -> None:
        await self.msg.nats_msg.term()

    async def in_progress(self) -> None:
        await self.msg.nats_msg.in_progress()


class Consumer:
    def __init__(
        self,
        client: JetStreamClient,
        stream_name: str,
        consumer_name: str,
        consumer_config: ConsumerConfig,
        created_timestamp: datetime.datetime,
    ) -> None:
        self.client = client
        self.steam_name = stream_name
        self.name = consumer_name
        self.config = consumer_config
        self.created_timestamp = created_timestamp

    def __validate__(self) -> None:
        pass

    def is_push(self) -> bool:
        """Returns True if the consumer is a push consumer."""
        return self.config.deliver_subject is not None

    def is_pull(self) -> bool:
        """Returns True if the consumer is a pull consumer."""
        return not self.is_push()

    def is_ephemeral(self) -> bool:
        """Returns True if the consumer is an ephemeral consumer."""
        return self.config.durable_name is None

    def is_durable(self) -> bool:
        """Returns True if the consumer is a durable consumer."""
        return not self.is_ephemeral()

    async def state(self) -> ConsumerState:
        """Returns the state of the consumer."""
        infos = await self.client.get_consumer_info(self.steam_name, self.name)
        return ConsumerState(
            delivered=infos.delivered,
            ack_floor=infos.ack_floor,
            num_ack_pending=infos.num_ack_pending,
            num_redelivered=infos.num_redelivered,
            num_waiting=infos.num_waiting,
            num_pending=infos.num_pending,
            cluster=infos.cluster,
            push_bound=infos.push_bound,
        )

    @classmethod
    def from_consumer_info(
        cls,
        client: JetStreamClient,
        consumer_info: ConsumerInfo | ConsumerCreateResponse | ConsumerInfoResponse,
    ) -> (
        DurablePullConsumer
        | DurablePushConsumer
        | EphemeralPullConsumer
        | EphemeralPushConsumer
    ):
        con = cls(
            client=client,
            stream_name=consumer_info.stream_name,
            consumer_name=consumer_info.name,
            consumer_config=consumer_info.config,
            created_timestamp=parse_utc_rfc3339(consumer_info.created),
        )
        if con.is_ephemeral():
            if con.is_push():
                return EphemeralPushConsumer.__from_consumer__(con)
            else:
                return EphemeralPullConsumer.__from_consumer__(con)
        else:
            if con.is_push():
                return DurablePushConsumer.__from_consumer__(con)
            else:
                return DurablePullConsumer.__from_consumer__(con)

    @classmethod
    def __from_consumer__(cls, con: "Consumer") -> Self:
        return cls(
            client=con.client,
            stream_name=con.steam_name,
            consumer_name=con.name,
            consumer_config=con.config,
            created_timestamp=con.created_timestamp,
        )


class PullConsumerQueue:
    def __init__(
        self,
        consumer: EphemeralPullConsumer | DurablePullConsumer,
    ) -> None:
        self.consumer = consumer
        self._inbox = consumer.client.typed.connection.client.new_inbox()
        self._pending: asyncio.Future[PendingMessage] | None = None
        self._subscription_handler: SubscriptionHandler | None = None

    async def next(self) -> PendingMessage:
        if not self._subscription_handler:
            raise RuntimeError("Queue not initialized")
        # If there is a pending future, simply await it
        if self._pending and not self._pending.done():
            return await self._pending
        # Reset the pending future
        self._pending = asyncio.Future()
        # Enter a loop to request messages until we get one
        while True:
            # Request a message
            await self.consumer.client.request_next_message_for_consumer(
                reply_subject=self._inbox,
                stream_name=self.consumer.steam_name,
                consumer_name=self.consumer.name,
                batch=1,
                expires=encode_nanoseconds_timedelta(datetime.timedelta(seconds=5)),
            )
            # Wait for a message to arrive until the expiration
            try:
                await asyncio.wait([self._pending], timeout=5)
            except BaseException:
                self._pending.cancel()
                raise
            # If the pending future is done, we got a message
            if self._pending.done():
                return await self._pending
            # Otherwise, we timed out and need to try again
            continue

    async def open(self) -> None:
        self._subscription_handler = (
            self.consumer.client.typed.connection.create_subscription_handler(
                self._inbox,
                callback=self._process_message,
            )
        )
        await self._subscription_handler.start()

    async def close(self) -> None:
        if self._subscription_handler:
            await self._subscription_handler.drain()

    async def __aenter__(self) -> Self:
        await self.open()
        return self

    async def __aexit__(self, *args: object, **kwargs: object) -> None:
        await self.close()

    async def _process_message(self, msg: Msg) -> None:
        if not isinstance(msg, MsgImpl):
            raise RuntimeError("Unexpected message type")
        if self._pending:
            self._pending.set_result(PendingMessageImpl(msg))


class PushConsumerQueue:
    def __init__(
        self,
        consumer: EphemeralPushConsumer | DurablePushConsumer,
    ) -> None:
        self.consumer = consumer
        self._queue: asyncio.Queue[PendingMessage] | None = None
        self._subscription_handler: SubscriptionHandler | None = None

    async def next(self) -> PendingMessage:
        if not self._queue:
            raise RuntimeError("Queue not initialized")
        try:
            return await self._queue.get()
        finally:
            self._queue.task_done()

    async def __aenter__(self) -> Self:
        self._queue = asyncio.Queue()
        self._subscription_handler = (
            self.consumer.client.typed.connection.create_subscription_handler(
                self.consumer.deliver_subject,
                callback=self._process_message,
            )
        )
        await self._subscription_handler.start()
        return self

    async def __aexit__(self, *args: object, **kwargs: object) -> None:
        if self._subscription_handler:
            await self._subscription_handler.drain()

    async def _process_message(self, msg: Msg) -> None:
        if not isinstance(msg, MsgImpl):
            raise RuntimeError("Unexpected message type")
        if self._queue:
            await self._queue.put(PendingMessageImpl(msg))


class PushConsumerQueueWorker:
    def __init__(
        self,
        consumer: EphemeralPushConsumer | DurablePushConsumer,
        callback: Callable[[PendingMessage], Awaitable[None]],
    ) -> None:
        self.consumer = consumer
        self._callback = callback
        self._subcription_handler: SubscriptionHandler | None = None

    async def __aenter__(self) -> Self:
        self._subcription_handler = (
            self.consumer.client.typed.connection.create_subscription_handler(
                self.consumer.deliver_subject,
                callback=self._process_message,
            )
        )
        await self._subcription_handler.start()
        return self

    async def __aexit__(self, *args: object, **kwargs: object) -> None:
        if self._subcription_handler:
            await self._subcription_handler.drain()

    async def _process_message(self, msg: Msg) -> None:
        if not isinstance(msg, MsgImpl):
            raise RuntimeError("Unexpected message type")
        await self._callback(
            PendingMessageImpl(msg),
        )


class EphemeralPullConsumer(Consumer):
    def __validate__(self) -> None:
        if not super().is_ephemeral():
            raise ValueError("Consumer is not ephemeral")
        if not super().is_pull():
            raise ValueError("Consumer is not a pull consumer")

    def is_ephemeral(self) -> Literal[True]:
        return True

    def is_durable(self) -> Literal[False]:
        return False

    def is_pull(self) -> Literal[True]:
        return True

    def is_push(self) -> Literal[False]:
        return False

    def messages(self) -> PullConsumerQueue:
        return PullConsumerQueue(self)


class DurablePullConsumer(Consumer):
    def __validate__(self) -> None:
        if not super().is_durable():
            raise ValueError("Consumer is not durable")
        if not super().is_pull():
            raise ValueError("Consumer is not a pull consumer")

    def is_ephemeral(self) -> Literal[False]:
        return False

    def is_durable(self) -> Literal[True]:
        return True

    def is_pull(self) -> Literal[True]:
        return True

    def is_push(self) -> Literal[False]:
        return False

    def messages(self) -> PullConsumerQueue:
        return PullConsumerQueue(self)


class EphemeralPushConsumer(Consumer):
    def __validate__(self) -> None:
        if not super().is_ephemeral():
            raise ValueError("Consumer is not ephemeral")
        if not super().is_push():
            raise ValueError("Consumer is not a push consumer")

    @property
    def deliver_subject(self) -> str:
        if not self.config.deliver_subject:
            raise RuntimeError(
                "Push consumers must have a deliver subject but no deliver subject was set in config"
            )
        return self.config.deliver_subject

    def is_ephemeral(self) -> Literal[True]:
        return True

    def is_durable(self) -> Literal[False]:
        return False

    def is_pull(self) -> Literal[False]:
        return False

    def is_push(self) -> Literal[True]:
        return True

    def messages(self) -> PushConsumerQueue:
        return PushConsumerQueue(self)

    def worker(
        self,
        callback: Callable[[PendingMessage], Awaitable[None]],
    ) -> PushConsumerQueueWorker:
        return PushConsumerQueueWorker(self, callback)


class DurablePushConsumer(Consumer):
    def __validate__(self) -> None:
        if not super().is_durable():
            raise ValueError("Consumer is not durable")
        if not super().is_push():
            raise ValueError("Consumer is not a push consumer")

    @property
    def deliver_subject(self) -> str:
        if not self.config.deliver_subject:
            raise RuntimeError(
                "Push consumers must have a deliver subject but no deliver subject was set in config"
            )
        return self.config.deliver_subject

    def is_ephemeral(self) -> Literal[False]:
        return False

    def is_durable(self) -> Literal[True]:
        return True

    def is_pull(self) -> Literal[False]:
        return False

    def is_push(self) -> Literal[True]:
        return True

    def messages(self) -> PushConsumerQueue:
        return PushConsumerQueue(self)

    def worker(
        self,
        callback: Callable[[PendingMessage], Awaitable[None]],
    ) -> PushConsumerQueueWorker:
        return PushConsumerQueueWorker(self, callback)
