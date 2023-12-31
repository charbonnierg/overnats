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
    """An [`NatsConnection`][easynats.connection.NatsConnection] is a wrapper around a NATS client.

    It accepts connect options at initialization and provides the
    [`with_options() method`][easynats.connection.NatsConnection.with_options] to apply connect options after initialization.

    An [`NatsConnection`][easynats.connection.NatsConnection] can be used as an asynchronous context manager
    to automatically open and close the connection.
    """

    def __init__(self, options: ConnectOpts | None = None) -> None:
        """Create a new `NatsConnection` out of connect options.

        It's possible to omit the connect options, as they can be applied
        later using the `NatsConnection.with_options` method.

        Args:
            options: Connect options to use. If not provided, the default
                options are used.
        """
        self.options = options or ConnectOpts()
        self._nats_client_or_none: NatsClient | None = None
        self._stack_or_none: AsyncExitStack | None = None

    def with_options(self, *option: ConnectOption) -> Self:
        """Apply connect options to a new `NatsConnection` instance.

        This method returns a new `NatsConnection` instance with the
        provided connect options applied. The original instance is not
        modified.

        This method can only be called before the connection is opened,
        otherwise a `RuntimeError` is raised.

        Args:
            option: Connect options to apply.

        Returns:
            A new `NatsConnection` instance with the connect options applied.

        Raises:
            RuntimeError: If the connection is already open.
        """
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
        """Access the underlying NATS client.

        This method can only be called after the connection is opened,
        otherwise a `RuntimeError` is raised.

        Raises:
            RuntimeError: If the connection is not opened.

        Returns:
            The underlying NATS client.
        """
        if self._nats_client_or_none is None:
            raise RuntimeError("Connection not open")
        return self._nats_client_or_none

    @property
    def stack(self) -> AsyncExitStack:
        """Access the underlying AsyncExitStack.

        This method can only be called after the connection is opened,
        otherwise a `RuntimeError` is raised.

        Raises:
            RuntimeError: If the connection is not opened.

        Returns:
            The underlying AsyncExitStack.
        """
        if self._stack_or_none is None:
            raise RuntimeError("Connection not open")
        return self._stack_or_none

    def jetstream(self, options: JetStreamOpts | None = None) -> JetStreamConnection:
        """Create a new JetStream connection on top of this NATS connection.

        Args:
            options: JetStream options to use. If not provided, the default
                options are used.

        Returns:
            A new NATS JetStream connection.
        """
        return JetStreamConnection(self, options)

    def micro(self, options: MicroOpts | None = None) -> MicroConnection:
        """Create a new Micro connection on top of this NATS connection.

        Args:
            options: Micro options to use. If not provided, the default
                options are used.

        Returns:
            A new NATS Micro connection.
        """
        return MicroConnection(self, options)

    async def open(self) -> None:
        """Open the connection to the NATS server.

        This method can only be called once, otherwise a `RuntimeError`
        is raised.

        Raises:
            RuntimeError: If the connection is already opened.
        """
        if self._stack_or_none is not None:
            raise RuntimeError("Connection already opened")
        self._stack_or_none = AsyncExitStack()
        self._nats_client_or_none = NatsClient()
        await self.client.connect(**self.options.dict())
        self._stack_or_none.push_async_callback(self.client.drain)

    async def close(self) -> None:
        """Close the connection to the NATS server.

        This method can only be called after the connection is opened,
        otherwise a `RuntimeError` is raised.

        Raises:
            RuntimeError: If the connection is not opened.
        """
        await self.stack.aclose()

    async def publish(
        self,
        subject: str,
        payload: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Publish a message to a subject.

        This method can only be called after the connection is opened,
        otherwise a `RuntimeError` is raised.

        Args:
            subject: The subject to publish to.
            payload: The message payload. If `None`, an empty payload (`b""`) is used.
            headers: The message headers. If `None`, no headers are used.

        Raises:
            RuntimeError: If the connection is not opened.

        Returns:
            None. The message is published asynchronously, and it is possible that message is never published in some cases.
        """
        await self.client.publish(
            subject=subject,
            payload=payload or b"",
            headers=headers,
        )

    async def request(
        self,
        subject: str,
        payload: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> Reply:
        """Send a request and wait for a reply.

        This method can only be called after the connection is opened,
        otherwise a `RuntimeError` is raised.

        Args:
            subject: The subject to send the request to.
            payload: The request payload. If `None`, an empty payload (`b""`) is used.
            headers: The request headers. If `None`, no headers are used.

        Raises:
            RuntimeError: If the connection is not opened.
            TimeoutError: If the request times out (if no reply is received within the timeout duration)

        Returns:
            The reply with optional data and headers.
        """
        msg = await self.client.request(subject, payload or b"", headers=headers)
        return Reply(msg.reply, msg.subject, msg.data, msg.headers or {})

    async def publish_request(
        self,
        subject: str,
        reply_subject: str,
        payload: bytes,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Send a request indicating a reply subject and do not wait for a reply.

        This method can only be called after the connection is opened,
        otherwise a `RuntimeError` is raised.

        Args:
            subject: The subject to send the request to.
            reply_subject: The subject to use for the reply. The receiver of the request will send the reply to this subject.
            payload: The request payload. If `None`, an empty payload (`b""`) is used.
            headers: The request headers. If `None`, no headers are used.

        Raises:
            RuntimeError: If the connection is not opened.

        Returns:
            None. The message is published asynchronously, and it is possible that message is never published in some cases.
        """
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
