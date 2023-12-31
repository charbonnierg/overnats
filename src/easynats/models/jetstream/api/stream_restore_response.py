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
class IoNatsJetstreamApiV1StreamRestoreResponse1:
    """
    A response from the JetStream $JS.API.STREAM.RESTORE API
    """

    error: Error
    type: Optional[str] = None


@dataclass
class IoNatsJetstreamApiV1StreamRestoreResponse2:
    """
    A response from the JetStream $JS.API.STREAM.RESTORE API
    """

    deliver_subject: str
    """
    The Subject to send restore chunks to
    """
    type: Optional[str] = None


IoNatsJetstreamApiV1StreamRestoreResponse = Union[
    IoNatsJetstreamApiV1StreamRestoreResponse1,
    IoNatsJetstreamApiV1StreamRestoreResponse2,
]
