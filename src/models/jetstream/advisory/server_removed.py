# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class IoNatsJetstreamAdvisoryV1ServerRemoved:
    """
    An Advisory sent when a Server has been removed from the cluster
    """

    id: str
    """
    Unique correlation ID for this event
    """
    timestamp: str
    """
    The time this event was created in RFC3339 format
    """
    server: str
    """
    The server name that was remove
    """
    server_id: str
    """
    The server ID that was remove
    """
    cluster: str
    """
    The cluster the server was in
    """
    type: str = "io.nats.jetstream.advisory.v1.server_removed"
    domain: Optional[str] = None
    """
    The domain the server was in
    """
