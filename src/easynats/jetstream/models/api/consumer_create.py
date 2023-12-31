# @generated

from dataclasses import dataclass
from enum import Enum
from typing import Union

from easynats.channel import Channel, Command

from .api_error import JetStreamApiV1Error
from .common.consumer_configuration import ConsumerConfig
from .common.consumer_info import ConsumerInfoExtras, ConsumerInfoRequired


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
class BaseConsumerCreateResponse(ConsumerInfoRequired):
    """
    A response from the JetStream $JS.API.CONSUMER.CREATE API
    """

    type: str


@dataclass
class ConsumerCreateResponse(ConsumerInfoExtras, BaseConsumerCreateResponse):
    pass


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
    error=bytes,
)

CREATE_DURABLE_CONSUMER = Command(
    channel=Channel(
        subject="CONSUMER.DURABLE.CREATE.{stream_name}.{durable_name}",
        parameters=JetstreamApiV1ConsumerDurableCreateParams,
    ),
    message=JetstreamApiV1ConsumerCreateRequest,
    reply=JetstreamApiV1ConsumerCreateResponse,
    error=bytes,
)

CREATE_FILTERED_DURABLE_CONSUMER = Command(
    channel=Channel(
        subject="CONSUMER.CREATE.{stream_name}.{durable_name}.{filter}",
        parameters=JetstreamApiV1ConsumerFilteredDurableCreateParams,
    ),
    message=JetstreamApiV1ConsumerCreateRequest,
    reply=JetstreamApiV1ConsumerCreateResponse,
    error=bytes,
)
