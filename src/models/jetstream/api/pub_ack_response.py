# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


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
class IoNatsJetstreamApiV1PubAckResponse:
    """
    A response received when publishing a message
    """

    stream: str
    """
    The name of the stream that received the message
    """
    error: Optional[Error] = None
    seq: Optional[int] = None
    """
    If successful this will be the sequence the message is stored at
    """
    duplicate: Optional[bool] = False
    """
    Indicates that the message was not stored due to the Nats-Msg-Id header and duplicate tracking
    """
    domain: Optional[str] = None
    """
    If the Stream accepting the message is in a JetStream server configured for a domain this would be that domain
    """
