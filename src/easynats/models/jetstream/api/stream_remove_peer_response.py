# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class Error:
    code: int
    """
    HTTP like error code in the 300 to 500 range
    """
    description: Optional[str] = None
    """
    A human friendly description of the error
    """
    err_code: Optional[int] = None
    """
    The NATS error code unique to each kind of error
    """


@dataclass
class IoNatsJetstreamApiV1StreamRemovePeerResponse1:
    """
    A response from the JetStream $JS.API.STREAM.PEER.REMOVE API
    """

    error: Error
    type: Optional[str] = None


@dataclass
class IoNatsJetstreamApiV1StreamRemovePeerResponse2:
    """
    A response from the JetStream $JS.API.STREAM.PEER.REMOVE API
    """

    success: bool
    """
    If the peer was successfully removed
    """
    type: Optional[str] = None


IoNatsJetstreamApiV1StreamRemovePeerResponse = Union[
    IoNatsJetstreamApiV1StreamRemovePeerResponse1,
    IoNatsJetstreamApiV1StreamRemovePeerResponse2,
]
