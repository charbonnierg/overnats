from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from typing_extensions import Self

from ..options.jetstream_opts import JetStreamOption, JetStreamOpts
from .api import JetStreamApiClient
from .sdk.kv.manager import KVManager
from .sdk.streams.manager import StreamManager

if TYPE_CHECKING:
    from ..connection import Connection


class JetStreamClient:
    """A high-level interface to JetStream."""

    streams: StreamManager
    """The [stream manager][easynats.jetstream.sdk.streams.manager.StreamManager] which can be used to manage streams."""

    kv: KVManager
    """The [key-value manager][easynats.jetstream.sdk.kv.manager.KVManager] which can be used to manage key-value stores."""

    def __init__(
        self,
        connection: Connection,
        options: JetStreamOpts | JetStreamOption | None = None,
        *opts: JetStreamOption,
    ) -> None:
        if isinstance(options, JetStreamOption):
            _opt = options
            options = JetStreamOpts()
            opts = (_opt, *opts)
        if options is None:
            options = JetStreamOpts()
        for opt in opts:
            opt(options)
        self.options = options
        self._connection = connection
        self._client = JetStreamApiClient(
            self._connection, api_prefix=self.options.get_api_prefix()
        )
        self.streams = StreamManager(self._client)
        self.kv = KVManager(self._client)

    def configure(self, *options: JetStreamOption) -> Self:
        """Apply JetStream options to a new `JetStreamClient` instance.

        Args:
            options: JetStream options to apply.

        Returns:
            A new `JetStreamClient` instance with the JetStream options applied.
        """
        opts = replace(self.options)
        for opt in options:
            opt(opts)
        return self.__class__(
            self._connection,
            opts,
        )
