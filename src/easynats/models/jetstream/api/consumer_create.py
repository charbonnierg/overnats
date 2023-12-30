# @generated

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

from easynats.channel import Channel, Command

from .api_error import JetStreamApiV1Error
from .common.consumer_configuration import ConsumerConfig
from .common.consumer_state import AckFloor, Cluster, Delivered


class Action(str, Enum):
    """Action for the $JS.API.CONSUMER.CREATE API."""

    CREATE = "create"
    UPDATE = "update"
    CREATE_OR_UPDATE = ""


@dataclass
class JetstreamApiV1ConsumerCreateParams:
    stream_name: str
    """
    The name of the stream to create the consumer in
    """


@dataclass
class JetstreamApiV1ConsumerDurableCreateParams:
    stream_name: str
    """
    The name of the stream to create the consumer in
    """
    durable_name: str
    """
    The name of the durable consumer
    """


@dataclass
class JetstreamApiV1ConsumerFilteredDurableCreateParams:
    stream_name: str
    """
    The name of the stream to create the consumer in
    """
    durable_name: str
    """
    The name of the durable consumer
    """
    filter: str
    """
    The filter expression for the consumer
    """


@dataclass
class JetstreamApiV1ConsumerCreateRequest:
    """
    A request to the JetStream $JS.API.CONSUMER.CREATE and $JS.API.CONSUMER.DURABLE.CREATE APIs
    """

    stream_name: str
    """
    The name of the stream to create the consumer in
    """
    config: ConsumerConfig
    """
    The consumer configuration
    """
    action: Action = Action.CREATE_OR_UPDATE
    """
    The consumer create action
    """


@dataclass
class ConsumerCreateResponse:
    """
    A response from the JetStream $JS.API.CONSUMER.CREATE API
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


JetstreamApiV1ConsumerCreateResponse = Union[
    ConsumerCreateResponse, JetStreamApiV1Error
]


CREATE_EPHEMERAL_CONSUMER = Command(
    channel=Channel(
        subject="CONSUMER.CREATE.{stream_name}",
        parameters=JetstreamApiV1ConsumerCreateParams,
    ),
    message=JetstreamApiV1ConsumerCreateRequest,
    reply=JetstreamApiV1ConsumerCreateResponse,
    error=str,
)

CREATE_DURABLE_CONSUMER = Command(
    channel=Channel(
        subject="CONSUMER.DURABLE.CREATE.{stream_name}.{durable_name}",
        parameters=JetstreamApiV1ConsumerDurableCreateParams,
    ),
    message=JetstreamApiV1ConsumerCreateRequest,
    reply=JetstreamApiV1ConsumerCreateResponse,
    error=str,
)

CREATE_FILTERED_DURABLE_CONSUMER = Command(
    channel=Channel(
        subject="CONSUMER.CREATE.{stream_name}.{durable_name}.{filter}",
        parameters=JetstreamApiV1ConsumerFilteredDurableCreateParams,
    ),
    message=JetstreamApiV1ConsumerCreateRequest,
    reply=JetstreamApiV1ConsumerCreateResponse,
    error=str,
)
