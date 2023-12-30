from dataclasses import dataclass
from typing import List, Optional

from .stream_configuration import StreamConfig
from .stream_state import Alternate, Cluster, Mirror, Source, StreamState


@dataclass
class StreamInfoRequired:
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


@dataclass
class StreamInfoExtras:
    ts: Optional[str] = None
    """
    The server time the stream info was created
    """
    cluster: Optional[Cluster] = None
    """
    Informaton about the cluster the stream is in
    """
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
class StreamInfo(StreamInfoExtras, StreamInfoRequired):
    pass
