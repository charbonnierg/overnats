# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from easynats.channel import Channel, Command

from .api_error import JetStreamApiV1Error


@dataclass
class JetStreamApiV1ConsumerDeleteParams:
    stream_name: str
    """
    The name of the stream to delete the consumer from
    """
    consumer_name: str
    """
    The name of the consumer to delete
    """


@dataclass
class ConsumerDeleteResponse:
    """
    A response from the JetStream $JS.API.CONSUMER.DELETE API
    """

    type: str
    success: bool


JetstreamApiV1ConsumerDeleteResponse = Union[
    JetStreamApiV1Error,
    ConsumerDeleteResponse,
]

DELETE_CONSUMER = Command(
    channel=Channel(
        subject="CONSUMER.DELETE.{stream_name}.{consumer_name}",
        parameters=JetStreamApiV1ConsumerDeleteParams,
    ),
    message=type(None),
    reply=JetstreamApiV1ConsumerDeleteResponse,
    error=str,
)
