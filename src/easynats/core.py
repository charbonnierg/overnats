"""`easynats.connection` module defines the `NatsConnection` class.

It is the main entry point for using easynats. It provides methods for:

- Connecting to a NATS server.
- Publishing messages.
- Requesting messages.
- Creating a JetStream connection.
- Creating a Micro connection.
- Creating a Monitoring connection.
"""
from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import AsyncIterator, Awaitable, Callable, TypeVar

from nats.aio.client import Client as NatsClient
from nats.aio.msg import Msg as NatsMsg
from nats.aio.subscription import Subscription as NatsSubscription
from typing_extensions import Self

T = TypeVar("T")


class SubscriptionHandler:
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
        self.subscription = (
            await self.client.subscribe(  # pyright: ignore[reportUnknownMemberType]
                subject=self.subject,
                queue=self.queue or "",
                cb=self._make_callback(),
            )
        )

    async def stop(self) -> None:
        if self.subscription:
            await self.subscription.unsubscribe()

    async def drain(self) -> None:
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

    async def messages(self) -> AsyncIterator[Msg]:
        if not self.subscription:
            raise RuntimeError("Subscription not started")
        async for msg in self.subscription.messages:
            yield MsgImpl(msg)

    async def start(self) -> None:
        self.subscription = (
            await self.client.subscribe(  # pyright: ignore[reportUnknownMemberType]
                subject=self.subject,
                queue=self.queue or "",
            )
        )

    async def stop(self) -> None:
        if self.subscription:
            await self.subscription.unsubscribe()

    async def drain(self) -> None:
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


class Msg(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def subject(self) -> str:
        ...

    @abc.abstractmethod
    def payload(self) -> bytes:
        ...

    @abc.abstractmethod
    def headers(self) -> dict[str, str]:
        ...

    @abc.abstractmethod
    def reply(self) -> str | None:
        ...

    @abc.abstractmethod
    async def respond(self, payload: bytes, headers: dict[str, str] | None = None):
        ...


class MsgImpl(Msg):
    def __init__(self, msg: NatsMsg) -> None:
        self.nats_msg = msg

    def subject(self) -> str:
        return self.nats_msg.subject

    def payload(self) -> bytes:
        return self.nats_msg.data

    def headers(self) -> dict[str, str]:
        return self.nats_msg.headers or {}

    def reply(self) -> str | None:
        return self.nats_msg.reply

    async def respond(self, payload: bytes, headers: dict[str, str] | None = None):
        await self.nats_msg._client.publish(self.nats_msg.reply, payload, headers=headers)  # type: ignore[protected-access]


@dataclass
class Reply:
    """The reply of request."""

    origin: str
    """The subject for which this reply is sent."""
    subject: str
    """The subject on which reply was received."""
    payload: bytes
    """The reply data."""
    headers: dict[str, str]
    """The reply headers."""
