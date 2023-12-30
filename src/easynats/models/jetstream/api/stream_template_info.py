# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Union

from easynats.channel import Channel, Command

from .api_error import JetStreamApiV1Error
from .common.stream_template_configuration import StreamTemplateConfiguration


@dataclass
class JetStreamApiV1StreamTemplateInfoParams:
    """
    Params for the JetStream $JS.API.STREAM.TEMPLATE.INFO API
    """

    template_name: str
    """
    The name of the template to fetch info for
    """


@dataclass
class StreamTemplateInfoResponse:
    """
    A response from the JetStream $JS.API.STREAM.TEMPLATE.INFO API
    """

    type: str
    config: StreamTemplateConfiguration
    streams: List[str]
    """
    List of Streams managed by this Template
    """


JetStreamApiV1StreamTemplateInfoResponse = Union[
    StreamTemplateInfoResponse,
    JetStreamApiV1Error,
]


GET_STREAM_TEMPLATE_INFO = Command(
    channel=Channel(
        subject="STREAM.TEMPLATE.INFO.{template_name}",
        parameters=JetStreamApiV1StreamTemplateInfoParams,
    ),
    message=type(None),
    reply=JetStreamApiV1StreamTemplateInfoResponse,
    error=str,
)
