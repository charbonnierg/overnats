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
class IoNatsJetstreamApiV1StreamMsgGetResponse1:
    """
    A response from the JetStream $JS.API.STREAM.MSG.GET API
    """

    type: str
    error: Error


@dataclass
class Message:
    subject: str
    """
    The subject the message was originally received on
    """
    seq: int
    """
    The sequence number of the message in the Stream
    """
    time: str
    """
    The time the message was received
    """
    data: Optional[str] = None
    """
    The base64 encoded payload of the message body
    """
    hdrs: Optional[str] = None
    """
    Base64 encoded headers for the message
    """


@dataclass
class IoNatsJetstreamApiV1StreamMsgGetResponse2:
    """
    A response from the JetStream $JS.API.STREAM.MSG.GET API
    """

    type: str
    message: Message


IoNatsJetstreamApiV1StreamMsgGetResponse = Union[
    IoNatsJetstreamApiV1StreamMsgGetResponse1, IoNatsJetstreamApiV1StreamMsgGetResponse2
]
