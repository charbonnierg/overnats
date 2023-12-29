from __future__ import annotations

from dataclasses import dataclass


@dataclass
class JetStreamOpts:
    """JetStream options for NATS python client."""

    domain: str | None = None
    api_prefix: str = "$JS.API."
