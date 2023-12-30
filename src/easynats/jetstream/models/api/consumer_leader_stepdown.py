# @generated

from dataclasses import dataclass
from typing import Optional, Union

from easynats.channel import Channel, Command

from .api_error import JetStreamApiV1Error


@dataclass
class JetStreamApiV1ConsumerLeaderStepdownParams:
    stream_name: str
    """
    The name of the stream to step down the consumer leader
    """
    consumer_name: str
    """
    The name of the consumer to step down
    """


@dataclass
class ConsumerLeaderStepdownResponse:
    """
    A response from the JetStream $JS.API.CONSUMER.LEADER.STEPDOWN API
    """

    success: bool
    """
    If the leader successfully stood down
    """
    type: Optional[str] = None


JetstreamApiV1ConsumerLeaderStepdownResponse = Union[
    JetStreamApiV1Error,
    ConsumerLeaderStepdownResponse,
]


STEPDOWN_CONSUMER_LEADER = Command(
    channel=Channel(
        subject="CONSUMER.LEADER.STEPDOWN.{stream_name}.{consumer_name}",
        parameters=JetStreamApiV1ConsumerLeaderStepdownParams,
    ),
    message=type(None),
    reply=JetstreamApiV1ConsumerLeaderStepdownResponse,
    error=bytes,
)
