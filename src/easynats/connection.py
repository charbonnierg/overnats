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
from dataclasses import replace

from nats.aio.client import Client as NatsClient
from typing_extensions import Self

from .core import CoreClient
from .jetstream import JetStreamClient
from .micro import MicroClient
from .options import (
    ConnectOption,
    ConnectOpts,
    JetStreamOption,
    JetStreamOpts,
    MicroOption,
    MicroOpts,
)
from .typed.client import TypedClient


class Connection:
    """An [`NatsConnection`][easynats.connection.Connection] is a wrapper around a NATS client.

    It accepts connect options at initialization and provides the
    [`configure() method`][easynats.connection.Connection.configure] to apply connect options after initialization.

    An [`NatsConnection`][easynats.connection.Connection] can be used as an asynchronous context manager
    to automatically open and close the connection.
    """

    def __init__(
        self,
        options: ConnectOpts | None = None,
        jetstream_options: JetStreamOpts | None = None,
        micro_options: MicroOpts | None = None,
    ) -> None:
        """Create a new `NatsConnection` out of connect options.

        Args:
            options: Connect options to use. If not provided, the default
                options are used.
            jetstream_options: JetStream options to use. If not provided, the default
                options are used.
            micro_options: Micro options to use. If not provided, the default
                options are used.
        """
        self.options = options or ConnectOpts()
        self.jetstream_options = jetstream_options or JetStreamOpts()
        self.micro_options = micro_options or MicroOpts()
        self._natspy_client_or_none: NatsClient | None = None
        self._core_client_or_none: CoreClient | None = None
        self._jetstream_client_or_none: JetStreamClient | None = None
        self._micro_client_or_none: MicroClient | None = None
        self._typed_client_or_none: TypedClient | None = None
        self._stack_or_none: AsyncExitStack | None = None

    def configure(self, *option: ConnectOption | JetStreamOption | MicroOption) -> Self:
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
        conn = self.__class__(
            options=replace(self.options),
            jetstream_options=replace(self.jetstream_options),
        )
        for opt in option:
            if isinstance(opt, ConnectOption):
                opt(conn.options)
            elif isinstance(opt, MicroOption):
                opt(conn.micro_options)
            elif isinstance(
                opt, JetStreamOption
            ):  # pyright: ignore[reportUnnecessaryIsInstance]
                opt(conn.jetstream_options)
            else:
                raise TypeError(f"Invalid option type: {type(opt)}")
        return conn

    @property
    def exit_stack(self) -> AsyncExitStack:
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

    @property
    def nats_client(self) -> NatsClient:
        """Access the underlying NATS client.

        This method can only be called after the connection is opened,
        otherwise a `RuntimeError` is raised.

        Raises:
            RuntimeError: If the connection is not opened.

        Returns:
            The underlying NATS client.
        """
        if self._natspy_client_or_none is None:
            raise RuntimeError("Connection not open")
        return self._natspy_client_or_none

    @property
    def core(self) -> CoreClient:
        """Access the underlying core client.

        This method can only be called after the connection is opened,
        otherwise a `RuntimeError` is raised.

        Raises:
            RuntimeError: If the connection is not opened.

        Returns:
            The underlying core client.

        See also:
            [`easynats.options.connect_opts`][easynats.options.connect_opts] for a list of available connect options.
        """
        if self._core_client_or_none is None:
            if self._natspy_client_or_none is None:
                raise RuntimeError("Connection not open")
            self._core_client_or_none = CoreClient(self._natspy_client_or_none)
        return self._core_client_or_none

    @property
    def jetstream(self) -> JetStreamClient:
        """Access the JetStream client on top of this NATS connection.

        Returns:
            A NATS JetStream client.

        See also:
            [`easynats.options.jetstream_opts`][easynats.options.jetstream_opts] for a list of available JetStream options.
        """
        if self._jetstream_client_or_none is None:
            self._jetstream_client_or_none = JetStreamClient(
                self, self.jetstream_options
            )
        return self._jetstream_client_or_none

    @property
    def micro(self) -> MicroClient:
        """Access the Micro client on top of this NATS connection.

        Returns:
            A NATS Micro client.

        See also:
            [`easynats.options.micro_opts`][easynats.options.micro_opts] for a list of available Micro options.
        """
        if self._micro_client_or_none is None:
            self._micro_client_or_none = MicroClient(self, self.micro_options)
        return self._micro_client_or_none

    @property
    def typed(self) -> TypedClient:
        """Create a new typed client on top of this NATS connection.

        A [`TypedClient`][easynats.typed.client.TypedClient] provides methods for publishing and requesting typed messages.

        Returns:
            A new typed client.
        """
        if self._typed_client_or_none is None:
            self._typed_client_or_none = TypedClient(self)
        return self._typed_client_or_none

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
        self._natspy_client_or_none = NatsClient()
        await self.nats_client.connect(**self.options.to_dict())
        self._stack_or_none.push_async_callback(self.nats_client.drain)

    async def close(self) -> None:
        """Close the connection to the NATS server.

        This method can only be called after the connection is opened,
        otherwise a `RuntimeError` is raised.

        Raises:
            RuntimeError: If the connection is not opened.
        """
        await self.exit_stack.aclose()

    async def __aenter__(self) -> Connection:
        await self.open()
        return self

    async def __aexit__(self, *args: object, **kwargs: object) -> None:
        await self.close()
