from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from typing_extensions import Self

from ..options.micro_opts import MicroOption, MicroOpts
from .api import Service, create_service

if TYPE_CHECKING:
    from ..connection import Connection


class MicroClient:
    """A high-level interface to NATS Micro."""

    def __init__(self, connection: Connection, opts: MicroOpts | None = None) -> None:
        self.options = opts or MicroOpts()
        self.connection = connection

    def configure(self, *options: MicroOption) -> Self:
        """Apply Micro options to a new `MicroClient` instance.

        Args:
            options: Micro options to apply.

        Returns:
            A new `MicroClient` instance with the Micro options applied.
        """
        opts = replace(self.options)
        for opt in options:
            opt(opts)
        return self.__class__(
            self.connection,
            opts,
        )

    def create_service(
        self,
        name: str,
        version: str,
        description: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> Service:
        """Create a new micro service.

        Args:
            name: The service name.
            version: The service version.
            description: The service description.
            metadata: The service metadata.

        Returns:
            The micro service.
        """
        return create_service(
            self.connection.nats_client,
            name,
            version,
            description,
            metadata,
            self.options.api_prefix,
        )
