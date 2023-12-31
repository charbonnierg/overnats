from __future__ import annotations

from dataclasses import dataclass


@dataclass
class JetStreamOpts:
    """JetStream options for NATS python client."""

    domain: str | None = None
    api_prefix: str = "$JS.API."

    def get_api_prefix(self) -> str:
        """Return the API prefix."""
        if self.domain:
            return f"$JS.{self.domain}.API."
        return self.api_prefix
