# @generated

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IoNatsJetstreamMetricV1ConsumerAck:
    """
    Metric published when a message was acknowledged to a consumer with Ack Sampling enabled
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
    The name of the consumer where the message is held
    """
    stream_seq: int
    """
    The sequence of the message in the stream that were acknowledged
    """
    consumer_seq: int
    """
    The sequence of the message in the consumer that were acknowledged
    """
    ack_time: int
    """
    The time it took on the final delivery for the message to be acknowledged in nanoseconds
    """
    deliveries: int
    """
    The number of deliveries that were attempted before being acknowledged
    """
    type: str = "io.nats.jetstream.metric.v1.consumer_ack"
