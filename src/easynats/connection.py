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
from typing import Any, Awaitable, Callable, Generic, TypeVar

from nats.aio.client import Client as NatsClient
from typing_extensions import Self

from . import micro
from .channel import Command, ErrorT, Event, MessageT, ParamsT, ReplyT
from .core import Msg, Reply, SubscriptionHandler, SubscriptionIterator
from .jetstream.api import JetStreamClient
from .jetstream.manager import StreamManager
from .options import ConnectOption, ConnectOpts, JetStreamOpts, MicroOpts

T = TypeVar("T")


@dataclass
class TypedReply(Generic[ParamsT, ReplyT, ErrorT]):
    """The reply of request."""

    success: bool
    """Whether the reply is a success or an error."""
    payload: ReplyT | ErrorT
    """The reply data."""
    headers: dict[str, str]
    """The reply headers."""

    def get_error(self) -> ErrorT | None:
        """Get the error payload or None if reply is a success."""
        if not self.success:
            return self.payload  # type: ignore

    def get_data(self) -> ReplyT | None:
        """Get the data payload or None if reply is an error."""
        if self.success:
            return self.payload  # type: ignore

    def error(self) -> ErrorT:
        """Get the error payload or raise an exception if reply is a success."""
        if self.success:
            raise RuntimeError("Reply is not an error")
        return self.payload  # type: ignore

    def data(self) -> ReplyT:
        """Get the data payload or raise an exception if reply is an error."""
        if not self.success:
            raise RuntimeError("Reply is not a success")
        return self.payload  # type: ignore

    @classmethod
    def create(
        cls, command: Command[ParamsT, Any, ReplyT, ErrorT], reply: Reply
    ) -> TypedReply[ParamsT, ReplyT, ErrorT]:
        """Create a typed reply from a command and a reply."""
        success = command.is_success(reply)
        if success:
            reply_data = command.decode_reply(reply.payload)
        else:
            reply_data = command.decode_error(reply.payload)
        return cls(
            success=success,
            payload=reply_data,
            headers=reply.headers,
        )


class Connection:
    """An [`NatsConnection`][easynats.connection.Connection] is a wrapper around a NATS client.

    It accepts connect options at initialization and provides the
    [`with_options() method`][easynats.connection.Connection.configure] to apply connect options after initialization.

    An [`NatsConnection`][easynats.connection.Connection] can be used as an asynchronous context manager
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

    def configure(self, *option: ConnectOption) -> Self:
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

    def typed(self) -> TypedConnection:
        """Create a new typed connection on top of this NATS connection.

        A [`TypedConnection`][easynats.connection.TypedConnection] provides methods for publishing and requesting typed messages.

        Returns:
            A new typed connection.
        """
        return TypedConnection(self)

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
        timeout: float | None = None,
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
        msg = await self.client.request(
            subject, payload or b"", headers=headers, timeout=timeout or float("inf")
        )
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

    def create_subscription_handler(
        self,
        subject: str,
        callback: Callable[[Msg], Awaitable[None]],
        queue: str | None = None,
        drain_on_exit: bool = True,
    ) -> SubscriptionHandler:
        return SubscriptionHandler(
            client=self.client,
            subject=subject,
            callback=callback,
            queue=queue,
            drain_on_exit=drain_on_exit,
        )

    def create_subscription_iterator(
        self,
        subject: str,
        queue: str | None = None,
        drain_on_exit: bool = True,
    ) -> SubscriptionIterator:
        return SubscriptionIterator(
            client=self.client,
            subject=subject,
            queue=queue,
            drain_on_exit=drain_on_exit,
        )

    async def __aenter__(self) -> Connection:
        await self.open()
        return self

    async def __aexit__(self, *args: object, **kwargs: object) -> None:
        await self.close()


class TypedConnection:
    """A [`TypedConnection][easynats.connection.TypedConnection]
    can be used to publish or request typed messages over channels
    rather than simple subjects.

    Checkout the [channel][easynats.channel] module to learn more
    about typed connection usage.
    """

    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    async def publish_event(
        self,
        event_type: Event[ParamsT, MessageT],
        params: ParamsT,
        payload: MessageT,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Publish an event.

        Args:
            event_type: The event type.
            params: The parameters for the event.
            payload: The event payload.
            headers: The event headers.

        Raises:
            RuntimeError: If the connection is not opened.

        Returns:
            None. The message is published asynchronously, and it is possible that message is never published in some cases.
        """
        await self.connection.publish(
            subject=event_type.channel.address.get_subject(params),
            payload=event_type.encode(payload),
            headers=headers,
        )

    async def publish_command(
        self,
        command_type: Command[ParamsT, MessageT, Any, Any],
        reply_subject: str,
        params: ParamsT,
        payload: MessageT,
        headers: dict[str, str] | None = None,
        prefix: str | None = None,
    ) -> None:
        """Publish a command.

        Args:
            command_type: The command type.
            reply_subject: The subject to use for the reply. The receiver of the command will send the reply to this subject.
            params: The parameters for the command.
            payload: The command payload.
            headers: The command headers.

        Raises:
            RuntimeError: If the connection is not opened.

        Returns:
            None. The message is published asynchronously, and it is possible that message is never published in some cases.
        """
        subject = command_type.channel.address.get_subject(params)
        if prefix is not None:
            subject = prefix + subject
        await self.connection.publish_request(
            subject=subject,
            reply_subject=reply_subject,
            payload=command_type.encode_request(payload),
            headers=headers,
        )

    async def request_command(
        self,
        command_type: Command[ParamsT, MessageT, ReplyT, ErrorT],
        params: ParamsT,
        payload: MessageT,
        headers: dict[str, str] | None = None,
        prefix: str | None = None,
    ) -> TypedReply[ParamsT, ReplyT, ErrorT]:
        """Send a command and wait for a reply.

        Args:
            command_type: The command type.
            params: The parameters for the command.
            payload: The command payload.
            headers: The command headers.

        Raises:
            RuntimeError: If the connection is not opened.
            TimeoutError: If the request times out (if no reply is received within the timeout duration)

        Returns:
            The typed reply with optional headers.
        """
        subject = command_type.channel.address.get_subject(params)
        if prefix is not None:
            subject = prefix + subject
        reply = await self.connection.request(
            subject=subject,
            payload=command_type.encode_request(payload),
            headers=headers,
        )
        return TypedReply.create(command_type, reply)


class MicroConnection:
    def __init__(self, connection: Connection, opts: MicroOpts | None = None) -> None:
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
    def __init__(self, connection: Connection) -> None:
        self.connection = connection


class JetStreamConnection:
    def __init__(
        self, connection: Connection, options: JetStreamOpts | None = None
    ) -> None:
        self.options = options or JetStreamOpts()
        self._connection = connection
        self._client = JetStreamClient(
            self._connection, api_prefix=self.options.get_api_prefix()
        )
        self.streams = StreamManager(self._client)
