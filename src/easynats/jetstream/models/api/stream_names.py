# @generated

from dataclasses import dataclass
from typing import List, Optional

from easynats.typed import Channel, Command


@dataclass
class JetstreamApiV1StreamNamesRequest:
    """
    A request to the JetStream $JS.API.STREAM.NAMES API
    """

    subject: Optional[str] = None
    """
    Limit the list to streams matching this subject filter
    """
    offset: Optional[int] = None


@dataclass
class StreamNamesResponse:
    """
    A response from the JetStream $JS.API.STREAM.NAMES API
    """

    total: int
    offset: int
    limit: int
    type: str
    streams: List[str]


JetstreamApiV1StreamNamesResponse = StreamNamesResponse


LIST_STREAM_NAMES = Command(
    channel=Channel(
        subject="STREAM.NAMES",
        parameters=type(None),
    ),
    message=JetstreamApiV1StreamNamesRequest,
    reply=JetstreamApiV1StreamNamesResponse,
    error=bytes,
)
