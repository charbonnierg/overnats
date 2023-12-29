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
class IoNatsJetstreamApiV1StreamDeleteResponse1:
    """
    A response from the JetStream $JS.API.STREAM.DELETE API
    """

    type: str
    error: Error


@dataclass
class IoNatsJetstreamApiV1StreamDeleteResponse2:
    """
    A response from the JetStream $JS.API.STREAM.DELETE API
    """

    type: str
    success: bool


IoNatsJetstreamApiV1StreamDeleteResponse = Union[
    IoNatsJetstreamApiV1StreamDeleteResponse1, IoNatsJetstreamApiV1StreamDeleteResponse2
]
