# @generated

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IoNatsJetstreamAdvisoryV1Terminated:
    """
    Advisory published when a message was terminated using a AckTerm acknowledgement
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
    The name of the consumer where the message was terminated
    """
    stream_seq: str
    """
    The sequence of the message in the stream that was terminated
    """
    consumer_seq: str
    """
    The sequence of the message in the consumer that was terminated
    """
    deliveries: int
    """
    The number of deliveries that were attempted
    """
    type: str = "io.nats.jetstream.advisory.v1.terminated"
