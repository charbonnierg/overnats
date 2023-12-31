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
class IoNatsJetstreamApiV1StreamLeaderStepdownResponse1:
    """
    A response from the JetStream $JS.API.STREAM.LEADER.STEPDOWN API
    """

    error: Error
    type: Optional[str] = None


@dataclass
class IoNatsJetstreamApiV1StreamLeaderStepdownResponse2:
    """
    A response from the JetStream $JS.API.STREAM.LEADER.STEPDOWN API
    """

    success: bool
    """
    If the leader successfully stood down
    """
    type: Optional[str] = None


IoNatsJetstreamApiV1StreamLeaderStepdownResponse = Union[
    IoNatsJetstreamApiV1StreamLeaderStepdownResponse1,
    IoNatsJetstreamApiV1StreamLeaderStepdownResponse2,
]
