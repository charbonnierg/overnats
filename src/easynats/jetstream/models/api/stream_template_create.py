# @generated

from dataclasses import dataclass
from typing import List, Union

from easynats.channel import Channel, Command

from .api_error import JetStreamApiV1Error
from .common.stream_configuration import StreamConfig
from .common.stream_template_configuration import StreamTemplateConfiguration


@dataclass
class JetStreamApiV1StreamTemplateCreateParams:
    """
    Params for the JetStream $JS.API.STREAM.TEMPLATE.CREATE API
    """

    template_name: str
    """
    The name of the template to create
    """


@dataclass
class JetStreamApiV1StreamTemplateCreateRequest:
    """
    A request to the JetStream $JS.API.STREAM.TEMPLATE.CREATE API
    """

    name: str
    """
    A unique name for the Template
    """
    config: StreamConfig
    """
    The template configuration to create Streams with
    """
    max_streams: int
    """
    The maximum number of streams to allow using this Template
    """


@dataclass
class StreamTemplateCreateResponse:
    """
    A response from the JetStream $JS.API.STREAM.TEMPLATE.CREATE API
    """

    type: str
    config: StreamTemplateConfiguration
    streams: List[str]
    """
    List of Streams managed by this Template
    """


JetStreamApiV1StreamTemplateCreateResponse = Union[
    StreamTemplateCreateResponse,
    JetStreamApiV1Error,
]


CREATE_STREAM_TEMPLATE = Command(
    channel=Channel(
        subject="STREAM.TEMPLATE.CREATE.{template_name}",
        parameters=JetStreamApiV1StreamTemplateCreateParams,
    ),
    message=JetStreamApiV1StreamTemplateCreateRequest,
    reply=JetStreamApiV1StreamTemplateCreateResponse,
    error=bytes,
)
