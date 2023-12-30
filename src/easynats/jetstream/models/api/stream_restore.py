# @generated

from dataclasses import dataclass
from typing import Optional, Union

from easynats.channel import Channel, Command

from .api_error import JetStreamApiV1Error
from .common.stream_configuration import StreamConfig
from .common.stream_state import StreamState


@dataclass
class JetStreamApiV1StreamRestoreParams:
    """
    Parameters for the JetStream $JS.API.STREAM.PEER.REMOVE API
    """

    stream_name: str
    """
    Name of the stream to remove the peer from
    """


@dataclass
class JetStreamApiV1StreamRestoreRequest:
    """
    A response from the JetStream $JS.API.STREAM.RESTORE API
    """

    config: StreamConfig
    state: StreamState


@dataclass
class StreamRestoreResponse:
    """
    A response from the JetStream $JS.API.STREAM.RESTORE API
    """

    deliver_subject: str
    """
    The Subject to send restore chunks to
    """
    type: Optional[str] = None


JetstreamApiV1StreamRestoreResponse = Union[
    StreamRestoreResponse,
    JetStreamApiV1Error,
]


RESTORE_STREAM = Command(
    channel=Channel(
        subject="STREAM.RESTORE.{stream_name}",
        parameters=JetStreamApiV1StreamRestoreParams,
    ),
    message=JetStreamApiV1StreamRestoreRequest,
    reply=JetstreamApiV1StreamRestoreResponse,
    error=str,
)
