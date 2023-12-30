# @generated

from dataclasses import dataclass
from typing import Optional

from easynats.channel import Channel, Command


@dataclass
class JetStreamApiV1ConsumerGetnextParams:
    stream_name: str
    """
    The name of the stream to get the next message from
    """
    consumer_name: str
    """
    The name of the consumer to get the next message from
    """


@dataclass
class JetStreamApiV1ConsumerGetnextRequest:
    """
    A request to the JetStream $JS.API.CONSUMER.MSG.NEXT API
    """

    expires: Optional[int] = None
    """
    A duration from now when the pull should expire, stated in nanoseconds, 0 for no expiry
    """
    batch: Optional[int] = None
    """
    How many messages the server should deliver to the requestor
    """
    max_bytes: Optional[int] = None
    """
    Sends at most this many bytes to the requestor, limited by consumer configuration max_bytes
    """
    no_wait: Optional[bool] = None
    """
    When true a response with a 404 status header will be returned when no messages are available
    """
    idle_heartbeat: Optional[int] = None
    """
    When not 0 idle heartbeats will be sent on this interval
    """


GET_CONSUMER_NEXT_MSG = Command(
    channel=Channel(
        subject="CONSUMER.MSG.NEXT.{stream_name}.{consumer_name}",
        parameters=JetStreamApiV1ConsumerGetnextParams,
    ),
    message=JetStreamApiV1ConsumerGetnextRequest,
    reply=bytes,
    error=bytes,
)
