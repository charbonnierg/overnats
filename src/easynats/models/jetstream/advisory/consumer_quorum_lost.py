# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .common.replicas import Replicas


@dataclass
class ConsumerQuorumLost:
    """
    An Advisory sent when a clustered Consumer lost quorum
    """

    id: str
    """
    Unique correlation ID for this event
    """
    timestamp: str
    """
    The time this event was created in RFC3339 format
    """
    stream: str
    """
    The name of the Stream the Consumer belongs to
    """
    consumer: str
    """
    The name of the Consumer that lost quorum
    """
    replicas: Replicas
    type: str = "io.nats.jetstream.advisory.v1.consumer_quorum_lost"

    def __post_init__(self) -> None:
        if not isinstance(
            self.replicas, Replicas
        ):  # pyright: ignore[reportUnnecessaryIsInstance]
            self.replicas = Replicas(
                **self.replicas  # pyright: ignore[reportUnknownArgumentType]
            )
