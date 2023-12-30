# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from easynats.channel import Channel, Command


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
