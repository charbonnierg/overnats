# @generated

from dataclasses import dataclass
from typing import List, Optional

from easynats.channel import Channel, Command

from .common.stream_info import StreamInfo


@dataclass
class JetstreamApiV1StreamListRequest:
    """
    A request to the JetStream $JS.API.STREAM.LIST API
    """

    subject: Optional[str] = None
    """
    Limit the list to streams matching this subject filter
    """
    offset: Optional[int] = None


@dataclass
class StreamListResponse:
    """
    A response from the JetStream $JS.API.STREAM.LIST API
    """

    total: int
    offset: int
    limit: int
    type: str
    streams: List[StreamInfo]


JetstreamApiV1StreamListResponse = StreamListResponse


LIST_STREAMS = Command(
    channel=Channel(
        subject="STREAM.LIST",
        parameters=type(None),
    ),
    message=JetstreamApiV1StreamListRequest,
    reply=JetstreamApiV1StreamListResponse,
    error=str,
)
