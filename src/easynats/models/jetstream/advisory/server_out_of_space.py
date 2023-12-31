# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class IoNatsJetstreamAdvisoryV1ServerOutOfSpace:
    """
    An Advisory sent when a Server has run out of disk space
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
    The server name that ran out of space
    """
    server_id: str
    """
    The server ID that ran out of space
    """
    type: str = "io.nats.jetstream.advisory.v1.server_out_of_space"
    stream: Optional[str] = None
    """
    The Stream that triggered the out of space event
    """
    cluster: Optional[str] = None
    """
    The cluster the server is in
    """
