# @generated

from __future__ import annotations

from dataclasses import dataclass

from easynats.channel import Channel, Command


@dataclass
class JetStreamApiV1StreamTemplateNamesRequest:
    """
    A request to the JetStream $JS.API.STREAM.TEMPLATE.NAMES API
    """

    offset: int


@dataclass
class StreamTemplateNamesResponse:
    """
    A response from the JetStream $JS.API.STREAM.TEMPLATE.NAMES API
    """

    total: int
    offset: int
    limit: int
    type: str


JetStreamApiV1StreamTemplateNamesResponse = StreamTemplateNamesResponse


LIST_STREAM_TEMPLATE_NAMES = Command(
    channel=Channel(
        subject="STREAM.TEMPLATE.NAMES",
        parameters=type(None),
    ),
    message=JetStreamApiV1StreamTemplateNamesRequest,
    reply=JetStreamApiV1StreamTemplateNamesResponse,
    error=str,
)
