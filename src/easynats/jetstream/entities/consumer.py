from __future__ import annotations

import abc
import asyncio
import datetime
from typing import TYPE_CHECKING, Awaitable, Callable, Literal

from typing_extensions import Self

from easynats.core import Msg, MsgImpl, SubscriptionHandler
from easynats.jetstream.api import JetStreamAPIException

from ..models.api.api_error import Error
from ..models.api.common._parser import encode_nanoseconds_timedelta, parse_utc_rfc3339
from ..models.api.common.consumer_configuration import ConsumerConfig
from ..models.api.common.consumer_info import ConsumerInfo
from ..models.api.common.consumer_state import ConsumerState
from ..models.api.consumer_create import ConsumerCreateResponse
from ..models.api.consumer_info import ConsumerInfoResponse

if TYPE_CHECKING:
    from ..api import JetStreamClient


class PendingMessage(metaclass=abc.ABCMeta):
    """A pending message is delivered to consumers.

    If consumer ack policy is not none, message must
    be acknowledged in order not to be redelivered in
    the future.
    """

    @abc.abstractmethod
    def subject(self) -> str:
        """Get the message subject.

        Returns:
            The message subject as a string.
        """
        ...

    @abc.abstractmethod
    def data(self) -> bytes:
        """Get the message data.

        Retuns:
            The message data as bytes.
        """
        ...

    @abc.abstractmethod
    def headers(self) -> dict[str, str]:
        """Get the message headers.

        Returns:
            The message headers as a dict.
        """
        ...

    @abc.abstractmethod
    def stream_sequence(self) -> int:
        """Get the sequence this message is stored at within the stream.

        Returns:
            The sequence the message is stored at within the stream.
        """
        ...

    @abc.abstractmethod
    def consumer_sequence(self) -> int:
        """Get the consumer sequence associated with this message.

        A consumer sequence may differ from a stream sequence as message
        may be redelivered.

        Returns:
            The consumer sequence associated with this message.
        """
        ...

    @abc.abstractmethod
    def timestamp(self) -> datetime.datetime:
        """Get the timestamp at which message was stored within the stream.

        Returns:
            The timestamp at which message was stored within the stream.
        """
        ...

    @abc.abstractmethod
    def num_pending(self) -> int:
        """Get the remaining number of pending messages for the consumer who received this message.

        Returns:
            The remaining number of pending messages for the message consumer.
        """
        ...

    @abc.abstractmethod
    def num_delivered(self) -> int:
        """Get the number of time this message has been delivered.

        This value is equal to 1 the first time message is delivered, and
        is incremented by one each time message is redelivered.

        Returns:
            The number of time this message has been delivered.
        """
        return ...

    @abc.abstractmethod
    async def ack(self) -> None:
        """Acknowledge the message.

        Returns:
            None. It's possible that the server never received the acknowledgement.
        """
        ...

    @abc.abstractmethod
    async def nak(self, delay: float | None = None) -> None:
        """Non-acknowledge the message. This will ask the NATS server to redeliver
        the message is the message has not been redelivered more than the maximum
        number of redelivery allowed in consumer configuration.

        Returns:
            None. It's possible that the server never received the non-acknowledgement.
        """
        ...

    @abc.abstractmethod
    async def term(self) -> None:
        """Terminate the message. This will indicate to the NATS server that message
        should no longer be redelivered, even if processing failed for some reason.

        Returns:
            None. It's possible that the server never received the term-acknowledgement.
        """
        ...

    @abc.abstractmethod
    async def in_progress(self) -> None:
        """Indicate that message processing is still in-progress.

        This is useful when the `ack_wait` consumer configuration is low,
        and some message takes more time than usual to be processed but should
        not be redelivered yet.

        Returns:
            None. It's possible that the server never received the in-progress-acknowlegement.
        """
        ...


class PendingMessageImpl(PendingMessage):
    def __init__(self, msg: MsgImpl) -> None:
        self.msg = msg

    def subject(self) -> str:
        return self.msg.nats_msg.subject

    def data(self) -> bytes:
        return self.msg.nats_msg.data

    def headers(self) -> dict[str, str]:
        return self.msg.nats_msg.headers or {}

    def stream_sequence(self) -> int:
        return self.msg.nats_msg.metadata.sequence.stream

    def consumer_sequence(self) -> int:
        return self.msg.nats_msg.metadata.sequence.consumer

    def num_pending(self) -> int:
        return self.msg.nats_msg.metadata.num_pending

    def num_delivered(self) -> int:
        return self.msg.nats_msg.metadata.num_delivered

    def timestamp(self) -> datetime.datetime:
        return self.msg.nats_msg.metadata.timestamp

    async def ack(self) -> None:
        await self.msg.nats_msg.ack()
        await self.msg.nats_msg._client.flush()  # pyright: ignore[reportPrivateUsage]

    async def nak(self, delay: float | None = None) -> None:
        await self.msg.nats_msg.nak(delay=delay)
        await self.msg.nats_msg._client.flush()  # pyright: ignore[reportPrivateUsage]

    async def term(self) -> None:
        await self.msg.nats_msg.term()
        await self.msg.nats_msg._client.flush()  # pyright: ignore[reportPrivateUsage]

    async def in_progress(self) -> None:
        await self.msg.nats_msg.in_progress()
        await self.msg.nats_msg._client.flush()  # pyright: ignore[reportPrivateUsage]


class Consumer:
    """Base class for all consumer implementations."""

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
        """Returns True if the consumer is a push consumer else False."""
        return self.config.deliver_subject is not None

    def is_pull(self) -> bool:
        """Returns True if the consumer is a pull consumer else False."""
        return not self.is_push()

    def is_ephemeral(self) -> bool:
        """Returns True if the consumer is an ephemeral consumer else False."""
        return self.config.durable_name is None

    def is_durable(self) -> bool:
        """Returns True if the consumer is a durable consumer else False."""
        return not self.is_ephemeral()

    async def state(self) -> ConsumerState:
        """Returns the state of the consumer fetched from the server.

        Returns:
            A view of the consumer state fetched from the NATS server.
        """
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

    async def destroy(self) -> None:
        """Destroy the consumer."""
        await self.client.delete_consumer(self.steam_name, self.name)

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
    """An asynchronous context manager which can be used to
    iterate over pull consumer messages."""

    def __init__(
        self,
        consumer: EphemeralPullConsumer | DurablePullConsumer,
    ) -> None:
        self.consumer = consumer
        self._inbox = consumer.client.typed.connection.client.new_inbox()
        self._pending: asyncio.Future[PendingMessage] | None = None
        self._subscription_handler: SubscriptionHandler | None = None

    async def peek(self) -> PendingMessage | None:
        """Get the next message available from the pull consumer or returns None.

        If no message is available, None is returned.

        Returns:
            None when no message is available, else the pending message.
        """
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
                no_wait=True,
            )
            # Wait for a message to arrive until the expiration
            try:
                await asyncio.wait([self._pending], timeout=5)
            except BaseException:
                self._pending.cancel()
                raise
            # If the future is not done, cancel it, and return None
            if not self._pending.done():
                self._pending.cancel()
                return None
            # If an exception was raised
            if exc := self._pending.exception():
                if isinstance(exc, JetStreamAPIException):
                    # Handle timeout errors
                    if exc.error.code == 408:
                        return None
                    # Handle no message error
                    if exc.error.code == 404:
                        return None
                raise exc
            # Happy path
            pending_message = self._pending.result()
            self._pending = None
            return pending_message

    async def next(self) -> PendingMessage:
        """Wait for the next message available from the pull consumer.

        This function will not return until a message is available or
        consumer is deleted on server side.

        Returns:
            The next pending message available.
        """
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
            # If the future is not done, cancel it, and create a new one
            if not self._pending.done():
                self._pending.cancel()
                self._pending = asyncio.Future()
                continue
            # If an exception was raised
            if exc := self._pending.exception():
                if isinstance(exc, JetStreamAPIException):
                    # Handle timeout errors
                    if exc.error.code == 408:
                        self._pending = asyncio.Future()
                        continue
                    # Handle message not found errors
                    if exc.error.code == 404:
                        self._pending = asyncio.Future()
                        continue
                    self._pending = None
                raise exc
            # Happy path
            pending_message = self._pending.result()
            self._pending = None
            return pending_message

    async def open(self) -> None:
        """Open the pull consumer queue. This will start a subscription on an inbox
        subject used to receive consumer messages.

        It is recommended to use this class as a context manager rather
        than using the `open()` and `close()` method.
        """
        self._subscription_handler = (
            self.consumer.client.typed.connection.create_subscription_handler(
                self._inbox,
                callback=self._process_message,
            )
        )
        await self._subscription_handler.start()

    async def close(self) -> None:
        """Close the pull consumer queue.

        It is recommended to use this class a context manager rather
        than using the `open()` and `close()` methods.
        """
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
        headers = msg.headers()
        # Handle errrors
        if status := headers.get("Status"):
            if self._pending:
                self._pending.set_exception(
                    JetStreamAPIException(
                        error=Error(
                            code=int(status),
                            description=headers.pop("Description", ""),
                        ),
                    )
                )
            return
        # Set pending future with pending message
        if self._pending:
            self._pending.set_result(PendingMessageImpl(msg))


class PushConsumerQueue:
    """An asynchronous context manager which can be used to
    iterate over push consumer messages."""

    def __init__(
        self,
        consumer: EphemeralPushConsumer | DurablePushConsumer,
    ) -> None:
        self.consumer = consumer
        self._queue: asyncio.Queue[PendingMessage] | None = None
        self._subscription_handler: SubscriptionHandler | None = None

    async def peek(self) -> PendingMessage | None:
        """Get the next message available from the push consumer or returns None.

        If no message is available, None is returned.

        Returns:
            None when no message is available, else the pending message.
        """
        if self._queue is None:
            raise RuntimeError("Queue not initialized")
        try:
            return self._queue.get_nowait()
        except asyncio.QueueEmpty:
            return None

    async def next(self) -> PendingMessage:
        """Wait for the next message available from the push consumer.

        This function will not return until a message is available or
        consumer is deleted on server side.

        Returns:
            The next pending message available.
        """
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
    """An asynchronous context manager which can be used to
    process push consumer messages using an arbitrary callback.

    The callback is responsible for acknowledging pending messages in
    case consumer configuration requires acknowledgement.
    """

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
    """An ephemeral pull consumer."""

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
    """A durable pull consumer."""

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
    """An ephemeral push consumer."""

    def __validate__(self) -> None:
        if not super().is_ephemeral():
            raise ValueError("Consumer is not ephemeral")
        if not super().is_push():
            raise ValueError("Consumer is not a push consumer")

    @property
    def deliver_subject(self) -> str:
        """Returns the deliver subject for this push consumer."""
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
        """Create a new message queue for this push consumer.

        Returns:
            A push consumer queue which can be started as an asynchronous context manager.
        """
        return PushConsumerQueue(self)

    def worker(
        self,
        callback: Callable[[PendingMessage], Awaitable[None]],
    ) -> PushConsumerQueueWorker:
        """Create a new queue worker for this push consumer.

        Args:
            callback: The callback to execute on pending messages.

        Returns:
            A push consumer queue worker which can be started as an asynchronous context manager.
        """
        return PushConsumerQueueWorker(self, callback)


class DurablePushConsumer(Consumer):
    """A durable push consumer."""

    def __validate__(self) -> None:
        if not super().is_durable():
            raise ValueError("Consumer is not durable")
        if not super().is_push():
            raise ValueError("Consumer is not a push consumer")

    @property
    def deliver_subject(self) -> str:
        """Returns the deliver subject for this push consumer."""
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
        """Create a new message queue for this push consumer.

        Returns:
            A push consumer queue which can be started as an asynchronous context manager.
        """
        return PushConsumerQueue(self)

    def worker(
        self,
        callback: Callable[[PendingMessage], Awaitable[None]],
    ) -> PushConsumerQueueWorker:
        """Create a new queue worker for this push consumer.

        Args:
            callback: The callback to execute on pending messages.

        Returns:
            A push consumer queue worker which can be started as an asynchronous context manager.
        """
        return PushConsumerQueueWorker(self, callback)
