from __future__ import annotations

from typing import AsyncIterator, Awaitable, Callable

from nats.aio.client import Client as NatsClient
from nats.aio.msg import Msg as NatsMsg
from nats.aio.subscription import Subscription as NatsSubscription
from typing_extensions import Self

from .msg import Msg, MsgImpl


class SubscriptionHandler:
    """Callback based subscription handler.

    This class can be used to start a subscription and handle the
    messages received using a callback function.

    It can be used as a context manager, in which case the subscription
    is started when the context is entered and stopped when the context
    is exited.
    """

    def __init__(
        self,
        client: NatsClient,
        subject: str,
        callback: Callable[[Msg], Awaitable[None]],
        queue: str | None = None,
        drain_on_exit: bool = True,
    ) -> None:
        self.client = client
        self.subsription: NatsSubscription | None = None
        self.subject = subject
        self.callback = callback
        self.queue = queue
        self.drain_on_exit = drain_on_exit

    async def start(self) -> None:
        """Start the subscription.

        This method will start the subscription and wait until the
        subscription is ready to receive messages.
        """
        self.subscription = (
            await self.client.subscribe(  # pyright: ignore[reportUnknownMemberType]
                subject=self.subject,
                queue=self.queue or "",
                cb=self._make_callback(),
            )
        )

    async def stop(self) -> None:
        """Stop the subscription.

        This method will stop the subscription and wait until the
        subscription is stopped.
        """
        if self.subscription:
            await self.subscription.unsubscribe()

    async def drain(self) -> None:
        """Drain the subscription.

        Draining the subscription will wait until all messages have been
        processed from the pending queue of the NATS client before stopping
        the subscription.
        """
        if self.subscription:
            await self.subscription.drain()

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(self, *args: object, **kwargs: object) -> None:
        if self.drain_on_exit:
            await self.drain()
        else:
            await self.stop()

    def _make_callback(self) -> Callable[[NatsMsg], Awaitable[None]]:
        async def callback(msg: NatsMsg) -> None:
            await self.callback(MsgImpl(msg))

        return callback


class SubscriptionIterator:
    """Python iterator for NATS subscriptions.

    This class can be used to start a subscription and iterate over the
    messages received.

    It can be used as a context manager, in which case the subscription
    is started when the context is entered and stopped when the context
    is exited.
    """

    def __init__(
        self,
        client: NatsClient,
        subject: str,
        queue: str | None = None,
        drain_on_exit: bool = True,
    ) -> None:
        self.client = client
        self.subsription: NatsSubscription | None = None
        self.subject = subject
        self.queue = queue
        self.drain_on_exit = drain_on_exit

    async def next(self, timeout: int = 5) -> Msg:
        """Get the next message.

        Returns:
            The next message.

        Raises:
            StopAsyncIteration: If the subscription is stopped.
        """
        if not self.subscription:
            raise RuntimeError("Subscription not started")
        msg = await self.subscription.next_msg(timeout=timeout)
        return MsgImpl(msg)

    async def messages(self) -> AsyncIterator[Msg]:
        """Get an asynchroneous iterator over the messages.

        Returns:
            An asynchronous iterator over the messages.

        Usage:

            ```python
            async for msg in subscription.messages():
                print(msg.payload())
            ```
        """
        if not self.subscription:
            raise RuntimeError("Subscription not started")
        async for msg in self.subscription.messages:
            yield MsgImpl(msg)

    async def start(self) -> None:
        """Start the subscription.

        This method will start the subscription and wait until the
        subscription is ready to receive messages.
        """
        self.subscription = (
            await self.client.subscribe(  # pyright: ignore[reportUnknownMemberType]
                subject=self.subject,
                queue=self.queue or "",
            )
        )

    async def stop(self) -> None:
        """Stop the subscription.

        This method will stop the subscription and wait until the
        subscription is stopped.
        """
        if self.subscription:
            await self.subscription.unsubscribe()

    async def drain(self) -> None:
        """Drain the subscription.

        Draining the subscription will wait until all messages have been
        processed from the pending queue of the NATS client before stopping
        the subscription.
        """
        if self.subscription:
            await self.subscription.drain()

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(self, *args: object, **kwargs: object) -> None:
        if self.drain_on_exit:
            await self.drain()
        else:
            await self.stop()
