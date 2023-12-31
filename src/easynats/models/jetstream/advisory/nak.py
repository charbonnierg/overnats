# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class IoNatsJetstreamAdvisoryV1Nak:
    """
    Advisory published when a message was naked using a AckNak acknowledgement
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
    The name of the stream where the message is stored
    """
    consumer: str
    """
    The name of the consumer where the message was naked
    """
    consumer_seq: str
    """
    The sequence of the message in the consumer that was naked
    """
    stream_seq: str
    """
    The sequence of the message in the stream that was naked
    """
    deliveries: int
    """
    The number of deliveries that were attempted
    """
    type: str = "io.nats.jetstream.advisory.v1.nak"
    domain: Optional[str] = None
    """
    The domain of the JetStreamServer
    """
