# @generated

from dataclasses import dataclass
from typing import Union

from easynats.typed import Channel, Command

from .api_error import JetStreamApiV1Error
from .common.consumer_info import ConsumerInfoExtras, ConsumerInfoRequired


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
class BaseConsumerInfoResponse(ConsumerInfoRequired):
    type: str


class ConsumerInfoResponse(BaseConsumerInfoResponse, ConsumerInfoExtras):
    """
    A response from the JetStream $JS.API.CONSUMER.INFO API
    """

    pass


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
