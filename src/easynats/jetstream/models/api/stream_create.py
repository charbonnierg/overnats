# @generated

from dataclasses import dataclass
from typing import List, Optional, Union

from easynats.typed import Channel, Command

from .api_error import JetStreamApiV1Error
from .common.stream_configuration import StreamConfig
from .common.stream_state import Alternate, Cluster, Mirror, Source, StreamState


@dataclass
class JetstreamApiV1StreamCreateParams:
    stream_name: str
    """
    The name of the stream to create
    """


JetstreamApiV1StreamCreateRequest = StreamConfig
"""
A request to the JetStream $JS.API.STREAM.CREATE API
"""


@dataclass
class StreamCreateResponse:
    """
    A response from the JetStream $JS.API.STREAM.CREATE API
    """

    type: str
    config: StreamConfig
    """
    The active configuration for the Stream
    """
    state: StreamState
    """
    Detail about the current State of the Stream
    """
    created: str
    """
    Timestamp when the stream was created
    """
    ts: Optional[str] = None
    """
    The server time the stream info was created
    """
    cluster: Optional[Cluster] = None
    mirror: Optional[Mirror] = None
    """
    Information about an upstream stream source in a mirror
    """
    sources: Optional[List[Source]] = None
    """
    Streams being sourced into this Stream
    """
    alternates: Optional[List[Alternate]] = None
    """
    List of mirrors sorted by priority
    """


JetstreamApiV1StreamCreateResponse = Union[StreamCreateResponse, JetStreamApiV1Error]


CREATE_STREAM = Command(
    channel=Channel(
        subject="STREAM.CREATE.{stream_name}",
        parameters=JetstreamApiV1StreamCreateParams,
    ),
    message=JetstreamApiV1StreamCreateRequest,
    reply=JetstreamApiV1StreamCreateResponse,
    error=bytes,
)
