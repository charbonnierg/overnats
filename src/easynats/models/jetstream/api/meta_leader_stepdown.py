# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union

from easynats.channel import Channel, Command

from .api_error import JetStreamApiV1Error


@dataclass
class Placement:
    """
    Placement requirements for a stream
    """

    cluster: str
    """
    The desired cluster name to place the stream
    """
    tags: Optional[List[str]] = None
    """
    Tags required on servers hosting this stream
    """


@dataclass
class JetstreamApiV1MetaLeaderStepdownRequest:
    """
    A request to the JetStream $JS.API.META.LEADER.STEPDOWN API
    """

    placement: Optional[Placement] = None
    """
    Placement requirements for a stream
    """


@dataclass
class MetaLeaderStepdownResponse:
    """
    A response from the JetStream $JS.API.META.LEADER.STEPDOWN API
    """

    success: bool
    """
    If the leader successfully stood down
    """
    type: Optional[str] = None


JetstreamApiV1MetaLeaderStepdownResponse = Union[
    JetStreamApiV1Error,
    MetaLeaderStepdownResponse,
]


STEPDOWN_LEADER = Command(
    channel=Channel(
        subject="META.LEADER.STEPDOWN",
        parameters=type(None),
    ),
    message=JetstreamApiV1MetaLeaderStepdownRequest,
    reply=JetstreamApiV1MetaLeaderStepdownResponse,
    error=str,
)
