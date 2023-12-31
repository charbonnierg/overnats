# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class IoNatsJetstreamApiV1MetaServerRemoveRequest:
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
