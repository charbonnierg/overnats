# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union

from easynats.channel import Channel, Command

from .api_error import JetStreamApiV1Error


@dataclass
class JetStreamApiV1StreamRemovePeerParams:
    """
    Parameters for the JetStream $JS.API.STREAM.PEER.REMOVE API
    """

    stream_name: str
    """
    Name of the stream to remove the peer from
    """


@dataclass
class JetStreamApiV1StreamRemovePeerRequest:
    """
    A request to the JetStream $JS.API.STREAM.PEER.REMOVE API
    """

    peer: str
    """
    Server name of the peer to remove
    """


@dataclass
class StreamRemovePeerResponse:
    """
    A response from the JetStream $JS.API.STREAM.PEER.REMOVE API
    """

    success: bool
    """
    If the peer was successfully removed
    """
    type: Optional[str] = None


IoNatsJetstreamApiV1StreamRemovePeerResponse = Union[
    StreamRemovePeerResponse,
    JetStreamApiV1Error,
]


STREAM_PEER_REMOVE = Command(
    channel=Channel(
        subject="STREAM.PEER.REMOVE.{stream_name}",
        parameters=JetStreamApiV1StreamRemovePeerParams,
    ),
    message=JetStreamApiV1StreamRemovePeerRequest,
    reply=IoNatsJetstreamApiV1StreamRemovePeerResponse,
    error=str,
)
