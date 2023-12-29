from __future__ import annotations

from contextlib import AsyncExitStack
from dataclasses import dataclass, replace
from typing import TypeVar

from nats.aio.client import Client as NatsClient
from typing_extensions import Self

from . import micro
from .options import ConnectOption, ConnectOpts, JetStreamOpts, MicroOpts

T = TypeVar("T")


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


class NatsConnection:
    def __init__(self, options: ConnectOpts | None = None) -> None:
        self.options = options or ConnectOpts()
        self._nats_client_or_none: NatsClient | None = None
        self._stack_or_none: AsyncExitStack | None = None

    def with_options(self, *option: ConnectOption) -> Self:
        if self._stack_or_none is not None:
            raise RuntimeError(
                "Cannot apply connect options after connection is opened."
            )
        conn = self.__class__(replace(self.options))
        for opt in option:
            opt.apply(conn.options)
        return conn

    @property
    def client(self) -> NatsClient:
        if self._nats_client_or_none is None:
            raise RuntimeError("Connection not open")
        return self._nats_client_or_none

    @property
    def stack(self) -> AsyncExitStack:
        if self._stack_or_none is None:
            raise RuntimeError("Connection not open")
        return self._stack_or_none

    def jetstream(self, options: JetStreamOpts | None = None) -> JetStreamConnection:
        return JetStreamConnection(self, options)

    def micro(self, options: MicroOpts | None = None) -> MicroConnection:
        return MicroConnection(self, options)

    async def open(self) -> None:
        self._stack_or_none = AsyncExitStack()
        self._nats_client_or_none = NatsClient()
        await self.client.connect(**self.options.dict())
        self._stack_or_none.push_async_callback(self.client.drain)

    async def close(self) -> None:
        await self.stack.aclose()

    async def publish(
        self,
        subject: str,
        payload: bytes,
        headers: dict[str, str] | None = None,
    ) -> None:
        await self.client.publish(
            subject=subject,
            payload=payload,
            headers=headers,
        )

    async def request(
        self,
        subject: str,
        payload: bytes,
        headers: dict[str, str] | None = None,
    ) -> Reply:
        msg = await self.client.request(subject, payload, headers=headers)
        return Reply(msg.reply, msg.subject, msg.data, msg.headers or {})

    async def publish_request(
        self,
        subject: str,
        reply_subject: str,
        payload: bytes,
        headers: dict[str, str] | None = None,
    ) -> None:
        await self.client.publish(
            subject=subject,
            reply=reply_subject,
            payload=payload,
            headers=headers,
        )

    async def __aenter__(self) -> NatsConnection:
        await self.open()
        return self

    async def __aexit__(self, *args: object, **kwargs: object) -> None:
        await self.close()


class MicroConnection:
    def __init__(
        self, connection: NatsConnection, opts: MicroOpts | None = None
    ) -> None:
        self.options = opts or MicroOpts()
        self.connection = connection

    def create_service(
        self,
        name: str,
        version: str,
        description: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> micro.Service:
        return micro.create_service(
            self.connection.client,
            name,
            version,
            description,
            metadata,
            self.options.api_prefix,
        )


class MonitoringConnection:
    def __init__(self, connection: NatsConnection) -> None:
        self.connection = connection


class JetStreamConnection:
    def __init__(
        self, connection: NatsConnection, options: JetStreamOpts | None = None
    ) -> None:
        self.connection = connection
        self.options = options or JetStreamOpts()
