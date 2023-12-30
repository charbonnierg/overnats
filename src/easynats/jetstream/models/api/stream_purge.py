# @generated

from dataclasses import dataclass
from typing import Optional, Union

from easynats.channel import Channel, Command

from .api_error import JetStreamApiV1Error


@dataclass
class JetStreamApiV1StreamPurgeParams:
    """
    Parameters for the JetStream $JS.API.STREAM.PURGE API
    """

    stream_name: str
    """
    The name of the stream to purge messages for.
    """


@dataclass
class JetStreamApiV1StreamPurgeRequest:
    """
    A request to the JetStream $JS.API.STREAM.PURGE API
    """

    filter: Optional[str] = None
    """
    Restrict purging to messages that match this subject
    """
    seq: Optional[int] = None
    """
    Purge all messages up to but not including the message with this sequence. Can be combined with subject filter but not the keep option
    """
    keep: Optional[int] = None
    """
    Ensures this many messages are present after the purge. Can be combined with the subject filter but not the sequence
    """


@dataclass
class StreamPurgeResponse:
    """
    A response from the JetStream $JS.API.STREAM.PURGE API
    """

    type: str
    success: bool
    purged: int
    """
    Number of messages purged from the Stream
    """


JetstreamApiV1StreamPurgeResponse = Union[StreamPurgeResponse, JetStreamApiV1Error]


PURGE_STREAM = Command(
    channel=Channel(
        subject="STREAM.PURGE.{stream_name}",
        parameters=JetStreamApiV1StreamPurgeParams,
    ),
    message=JetStreamApiV1StreamPurgeRequest,
    reply=JetstreamApiV1StreamPurgeResponse,
    error=bytes,
)
