# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class IoNatsJetstreamApiV1StreamSnapshotRequest:
    """
    A request to the JetStream $JS.API.STREAM.SNAPSHOT API
    """

    deliver_subject: str
    """
    The NATS subject where the snapshot will be delivered
    """
    no_consumers: Optional[bool] = None
    """
    When true consumer states and configurations will not be present in the snapshot
    """
    chunk_size: Optional[int] = None
    """
    The size of data chunks to send to deliver_subject
    """
    jsck: Optional[bool] = False
    """
    Check all message's checksums prior to snapshot
    """
