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
class IoNatsJetstreamApiV1ConsumerLeaderStepdownResponse1:
    """
    A response from the JetStream $JS.API.CONSUMER.LEADER.STEPDOWN API
    """

    error: Error
    type: Optional[str] = None


@dataclass
class IoNatsJetstreamApiV1ConsumerLeaderStepdownResponse2:
    """
    A response from the JetStream $JS.API.CONSUMER.LEADER.STEPDOWN API
    """

    success: bool
    """
    If the leader successfully stood down
    """
    type: Optional[str] = None


IoNatsJetstreamApiV1ConsumerLeaderStepdownResponse = Union[
    IoNatsJetstreamApiV1ConsumerLeaderStepdownResponse1,
    IoNatsJetstreamApiV1ConsumerLeaderStepdownResponse2,
]
