# @generated

from dataclasses import dataclass
from typing import Optional

from .api_error import Error


@dataclass
class PubAckResponse:
    stream: str
    """
    The name of the stream that received the message
    """
    """If not successful, this will be the error"""
    seq: int
    """
    The sequence the message is stored at
    """
    duplicate: Optional[bool] = False
    """
    Indicates that the message was not stored due to the Nats-Msg-Id header and duplicate tracking
    """
    domain: Optional[str] = None
    """
    If the Stream accepting the message is in a JetStream server configured for a domain this would be that domain
    """


@dataclass
class JetstreamApiV1PubAckResponse:
    """
    A response received when publishing a message
    """

    stream: str
    """
    The name of the stream that received the message
    """
    error: Optional[Error] = None
    """If not successful, this will be the error"""
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
