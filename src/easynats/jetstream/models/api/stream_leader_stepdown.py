# @generated

from dataclasses import dataclass
from typing import Optional, Union

from easynats.channel import Channel, Command

from .api_error import JetStreamApiV1Error


@dataclass
class JetStreamApiV1StreamLeaderStepdownParams:
    stream_name: str
    """
    The name of the stream to remove the leader from
    """


@dataclass
class StreamLeaderStepdownResponse:
    """
    A response from the JetStream $JS.API.STREAM.LEADER.STEPDOWN API
    """

    success: bool
    """
    If the leader successfully stood down
    """
    type: Optional[str] = None


JetstreamApiV1StreamLeaderStepdownResponse = Union[
    JetStreamApiV1Error,
    StreamLeaderStepdownResponse,
]


STEPDOWN_STREAM_LEADER = Command(
    channel=Channel(
        subject="STREAM.LEADER.STEPDOWN.{stream_name}",
        parameters=JetStreamApiV1StreamLeaderStepdownParams,
    ),
    message=type(None),
    reply=JetstreamApiV1StreamLeaderStepdownResponse,
    error=str,
)
