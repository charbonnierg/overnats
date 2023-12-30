# @generated

from dataclasses import dataclass
from typing import List, Optional, Union

from easynats.channel import Channel, Command

from .api_error import JetStreamApiV1Error
from .common.stream_configuration import StreamConfig
from .common.stream_state import Alternate, Cluster, Mirror, Source, StreamState


@dataclass
class JetStreamApiV1StreamUpdateParams:
    """
    Paramsfor the JetStream $JS.API.STREAM.UPDATE API
    """

    stream_name: str
    """
    The name of the stream to update
    """


JetstreamApiV1StreamUpdateRequest = StreamConfig


@dataclass
class StreamUpdateResponse:
    """
    A response from the JetStream $JS.API.STREAM.UPDATE API
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


JetstreamApiV1StreamUpdateResponse = Union[StreamUpdateResponse, JetStreamApiV1Error]


UPDATE_STREAM = Command(
    channel=Channel(
        subject="STREAM.UPDATE.{stream_name}",
        parameters=JetStreamApiV1StreamUpdateParams,
    ),
    message=JetstreamApiV1StreamUpdateRequest,
    reply=JetstreamApiV1StreamUpdateResponse,
    error=str,
)
