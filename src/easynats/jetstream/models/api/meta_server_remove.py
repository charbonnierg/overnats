# @generated

from dataclasses import dataclass
from typing import Optional, Union

from easynats.channel import Channel, Command

from .api_error import JetStreamApiV1Error


@dataclass
class JetstreamApiV1MetaServerRemoveRequest:
    """
    A request to the JetStream $JS.API.SERVER.REMOVE API
    """

    peer: Optional[str] = None
    """
    The Name of the server to remove from the meta group
    """
    peer_id: Optional[str] = None
    """
    Peer ID of the peer to be removed. If specified this is used instead of the server name
    """


@dataclass
class MetaServerRemoveResponse:
    """
    A response from the JetStream $JS.API.SERVER.REMOVE API
    """

    success: bool
    """
    If the peer was successfully removed
    """
    type: Optional[str] = None


JetstreamApiV1MetaServerRemoveResponse = Union[
    MetaServerRemoveResponse,
    JetStreamApiV1Error,
]

REMOVE_SERVER = Command(
    channel=Channel(
        subject="META.SERVER.REMOVE",
        parameters=type(None),
    ),
    message=JetstreamApiV1MetaServerRemoveRequest,
    reply=JetstreamApiV1MetaServerRemoveResponse,
    error=str,
)
