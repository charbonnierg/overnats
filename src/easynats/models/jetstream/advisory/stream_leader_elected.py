# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Replicas:
    name: str
    """
    The server name of the peer
    """
    current: bool
    """
    Indicates if the server is up to date and synchronised
    """
    active: float
    """
    Nanoseconds since this peer was last seen
    """
    offline: Optional[bool] = False
    """
    Indicates the node is considered offline by the group
    """
    lag: Optional[int] = None
    """
    How many uncommitted operations this peer is behind the leader
    """


@dataclass
class IoNatsJetstreamAdvisoryV1StreamLeaderElected:
    """
    An Advisory sent when a clustered Stream elected a new leader
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
    The name of the Stream that elected a leader
    """
    leader: str
    """
    The server name of the elected leader
    """
    replicas: Replicas
    type: str = "io.nats.jetstream.advisory.v1.stream_leader_elected"