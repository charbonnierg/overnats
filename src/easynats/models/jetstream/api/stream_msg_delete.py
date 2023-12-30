# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from easynats.channel import Channel, Command

from .api_error import JetStreamApiV1Error


@dataclass
class JetStreamApiV1StreamMsgDeleteParams:
    """
    Parameters for the JetStream $JS.API.STREAM.MSG.DELETE API
    """

    stream_name: str
    """
    The name of the stream
    """


@dataclass
class JetStreamApiV1StreamMsgDeleteRequest:
    """
    A request to the JetStream $JS.API.STREAM.MSG.DELETE API
    """

    seq: int
    no_erase: bool | None = None


@dataclass
class StreamMsgDeleteResponse:
    """
    A response from the JetStream $JS.API.STREAM.MSG.DELETE API
    """

    type: str
    success: bool


JetstreamApiV1StreamMsgDeleteResponse = Union[
    JetStreamApiV1Error,
    StreamMsgDeleteResponse,
]

DELETE_STREAM_MSG = Command(
    channel=Channel(
        subject="STREAM.MSG.DELETE.{stream_name}",
        parameters=JetStreamApiV1StreamMsgDeleteParams,
    ),
    message=JetStreamApiV1StreamMsgDeleteRequest,
    reply=JetstreamApiV1StreamMsgDeleteResponse,
    error=str,
)
