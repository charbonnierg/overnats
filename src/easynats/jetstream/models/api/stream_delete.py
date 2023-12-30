# @generated

from dataclasses import dataclass
from typing import Union

from easynats.channel import Channel, Command

from .api_error import JetStreamApiV1Error


@dataclass
class JetStreamApiV1StreamDeleteParams:
    stream_name: str
    """
    The name of the stream to delete
    """


@dataclass
class StreamDeleteResponse:
    """
    A response from the JetStream $JS.API.STREAM.DELETE API
    """

    type: str
    success: bool


JetstreamApiV1StreamDeleteResponse = Union[JetStreamApiV1Error, StreamDeleteResponse]


DELETE_STREAM = Command(
    channel=Channel(
        subject="STREAM.DELETE.{stream_name}",
        parameters=JetStreamApiV1StreamDeleteParams,
    ),
    message=type(None),
    reply=JetstreamApiV1StreamDeleteResponse,
    error=str,
)
