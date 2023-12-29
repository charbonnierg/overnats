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
class IoNatsJetstreamApiV1ConsumerDeleteResponse1:
    """
    A response from the JetStream $JS.API.CONSUMER.DELETE API
    """

    type: str
    error: Error


@dataclass
class IoNatsJetstreamApiV1ConsumerDeleteResponse2:
    """
    A response from the JetStream $JS.API.CONSUMER.DELETE API
    """

    type: str
    success: bool


IoNatsJetstreamApiV1ConsumerDeleteResponse = Union[
    IoNatsJetstreamApiV1ConsumerDeleteResponse1,
    IoNatsJetstreamApiV1ConsumerDeleteResponse2,
]
