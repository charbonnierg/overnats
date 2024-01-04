# @generated

from dataclasses import dataclass
from typing import List, Optional

from easynats.typed import Channel, Command


@dataclass
class JetStreamApiV1ConsumerNamesParams:
    stream_name: str
    """
    The name of the stream to list consumers from
    """


@dataclass
class JetstreamApiV1ConsumerNamesRequest:
    """
    A request to the JetStream $JS.API.CONSUMER.NAMES API
    """

    offset: int
    subject: Optional[str] = None
    """
    Filter the names to those consuming messages matching this subject or wildcard
    """


@dataclass
class ConsumerNamesResponse:
    """
    A response from the JetStream $JS.API.CONSUMER.NAMES API
    """

    total: int
    offset: int
    limit: int
    type: str
    consumers: List[str]


JetstreamApiV1ConsumerNamesResponse = ConsumerNamesResponse


LIST_CONSUMER_NAMES = Command(
    channel=Channel(
        subject="CONSUMER.NAMES.{stream_name}",
        parameters=JetStreamApiV1ConsumerNamesParams,
    ),
    message=JetstreamApiV1ConsumerNamesRequest,
    reply=JetstreamApiV1ConsumerNamesResponse,
    error=bytes,
)
