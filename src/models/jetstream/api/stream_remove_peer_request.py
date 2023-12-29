# @generated

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IoNatsJetstreamApiV1StreamRemovePeerRequest:
    """
    A request to the JetStream $JS.API.STREAM.PEER.REMOVE API
    """

    peer: str
    """
    Server name of the peer to remove
    """
