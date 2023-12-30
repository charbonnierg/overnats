# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union

from easynats.channel import Channel, Command

from .api_error import JetStreamApiV1Error
from .common.stream_configuration import StreamConfiguration
from .common.stream_state import Alternate, Cluster, Mirror, Source, StreamState


@dataclass
class JetStreamApiV1StreamInfoParams:
    """
    Parameters for the JetStream $JS.API.STREAM.INFO API
    """

    stream_name: str
    """
    The name of the stream to get info for
    """


@dataclass
class JetStreamApiV1StreamInfoRequest:
    """
    A request to the JetStream $JS.API.STREAM.INFO API
    """

    deleted_details: Optional[bool] = None
    """
    When true will result in a full list of deleted message IDs being returned in the info response
    """
    subjects_filter: Optional[str] = None
    """
    When set will return a list of subjects and how many messages they hold for all matching subjects. Filter is a standard NATS subject wildcard pattern.
    """
    offset: Optional[int] = None
    """
    Paging offset when retrieving pages of subjet details
    """


@dataclass
class StreamInfoResponse:
    """
    A response from the JetStream $JS.API.STREAM.INFO API
    """

    type: str
    config: StreamConfiguration
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
    total: Optional[int] = None
    offset: Optional[int] = None
    limit: Optional[int] = None
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


@dataclass
class JetstreamApiV1StreamInfoResponseError(JetStreamApiV1Error):
    """
    A response from the JetStream $JS.API.STREAM.INFO API
    """

    total: Optional[int] = None
    offset: Optional[int] = None
    limit: Optional[int] = None


JetstreamApiV1StreamInfoResponse = Union[StreamInfoResponse, JetStreamApiV1Error]


GET_STREAM_INFO = Command(
    channel=Channel(
        subject="STREAM.INFO.{stream_name}",
        parameters=JetStreamApiV1StreamInfoParams,
    ),
    message=JetStreamApiV1StreamInfoRequest,
    reply=JetstreamApiV1StreamInfoResponse,
    error=str,
)
