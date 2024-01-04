# @generated

from dataclasses import dataclass
from typing import Union

from easynats.typed import Channel, Command

from .api_error import JetStreamApiV1Error


@dataclass
class JetStreamApiV1StreamTemplateDeleteParams:
    """
    Params for the JetStream $JS.API.STREAM.TEMPLATE.DELETE API
    """

    template_name: str
    """
    The name of the template to delete
    """


@dataclass
class StreamTemplateDeleteResponse:
    """
    A response from the JetStream $JS.API.STREAM.TEMPLATE.DELETE API
    """

    type: str
    success: bool


JetStreamApiV1StreamTemplateDeleteResponse = Union[
    StreamTemplateDeleteResponse,
    JetStreamApiV1Error,
]


DELETE_STREAM_TEMPLATE = Command(
    channel=Channel(
        subject="STREAM.TEMPLATE.DELETE.{template_name}",
        parameters=JetStreamApiV1StreamTemplateDeleteParams,
    ),
    message=type(None),
    reply=JetStreamApiV1StreamTemplateDeleteResponse,
    error=bytes,
)
