# @generated

from dataclasses import dataclass
from typing import Optional, Union

from easynats.channel import Channel, Command

from .api_error import JetStreamApiV1Error
from .common.consumer_configuration import ConsumerConfig
from .common.consumer_state import AckFloor, Cluster, Delivered


@dataclass
class JetStreamApiV1ConsumerInfoParams:
    stream_name: str
    """
    The name of the stream to create the consumer on
    """
    consumer_name: str
    """
    The name of the consumer to create
    """


@dataclass
class ConsumerInfoResponse:
    """
    A response from the JetStream $JS.API.CONSUMER.INFO API
    """

    type: str
    stream_name: str
    """
    The Stream the consumer belongs to
    """
    name: str
    """
    A unique name for the consumer, either machine generated or the durable name
    """
    config: ConsumerConfig
    """
    The consumer configuration
    """
    created: str
    """
    The time the Consumer was created
    """
    delivered: Delivered
    """
    The last message delivered from this Consumer
    """
    ack_floor: AckFloor
    """
    The highest contiguous acknowledged message
    """
    num_ack_pending: int
    """
    The number of messages pending acknowledgement
    """
    num_redelivered: int
    """
    The number of redeliveries that have been performed
    """
    num_waiting: int
    """
    The number of pull consumers waiting for messages
    """
    num_pending: int
    """
    The number of messages left unconsumed in this Consumer
    """
    ts: Optional[str] = None
    """
    The server time the consumer info was created
    """
    cluster: Optional[Cluster] = None
    push_bound: Optional[bool] = None
    """
    Indicates if any client is connected and receiving messages from a push consumer
    """


JetstreamApiV1ConsumerInfoResponse = Union[ConsumerInfoResponse, JetStreamApiV1Error]


GET_CONSUMER_INFO = Command(
    channel=Channel(
        subject="CONSUMER.INFO.{stream_name}.{consumer_name}",
        parameters=JetStreamApiV1ConsumerInfoParams,
    ),
    message=type(None),
    reply=JetstreamApiV1ConsumerInfoResponse,
    error=bytes,
)
