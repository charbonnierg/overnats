from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MicroOpts:
    """JetStream options for NATS python client."""

    api_prefix: str = "$SRV"
    default_queue: str = "q"
