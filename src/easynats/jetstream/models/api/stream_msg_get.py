# @generated

from dataclasses import dataclass
from typing import Optional, Union

from easynats.channel import Channel, Command

from .api_error import JetStreamApiV1Error


@dataclass
class JetStreamApiV1StreamMsgGetParams:
    """
    Parameters for the JetStream $JS.API.STREAM.MSG.GET API
    """

    stream_name: str
    """
    The stream to get messages from
    """


@dataclass
class JetStreamApiV1StreamDirectMsgGetParams:
    """
    Parameters for the JetStream $JS.API.DIRECT.GET API
    """

    stream_name: str
    """
    The stream to get messages from
    """


@dataclass
class JetStreamApiV1StreamDirectGetLastMsgForSubjectParams:
    """
    Parameters for the JetStream $JS.API.DIRECT.GET.{stream_name}.{subject} API
    """

    stream_name: str
    """
    The stream to get messages from
    """
    subject: str
    """
    The subject to get the last message from
    """


@dataclass
class JetStreamApiV1StreamMsgGetRequest:
    """
    A request to the JetStream $JS.API.STREAM.MSG.GET API
    """

    seq: Optional[int] = None
    """
    Stream sequence number of the message to retrieve, cannot be combined with last_by_subj
    """
    last_by_subj: Optional[str] = None
    """
    Retrieves the last message for a given subject, cannot be combined with seq
    """
    next_by_subj: Optional[str] = None
    """
    Combined with sequence gets the next message for a subject with the given sequence or higher
    """


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
class StreamMsgGetResponse:
    """
    A response from the JetStream $JS.API.STREAM.MSG.GET API
    """

    type: str
    message: Message


JetStreamApiV1StreamMsgGetResponse = Union[StreamMsgGetResponse, JetStreamApiV1Error]


GET_STREAM_MSG = Command(
    channel=Channel(
        subject="STREAM.MSG.GET.{stream_name}",
        parameters=JetStreamApiV1StreamMsgGetParams,
    ),
    message=JetStreamApiV1StreamMsgGetRequest,
    reply=JetStreamApiV1StreamMsgGetResponse,
    error=bytes,
)


DIRECT_GET_STREAM_MSG = Command(
    channel=Channel(
        subject="DIRECT.GET.{stream_name}",
        parameters=JetStreamApiV1StreamDirectMsgGetParams,
    ),
    message=JetStreamApiV1StreamMsgGetRequest,
    reply=bytes,
    error=bytes,
)


DIRECT_GET_STREAM_LAST_MSG_FOR_SUBJECT = Command(
    channel=Channel(
        subject="DIRECT.GET.{stream_name}.{subject}",
        parameters=JetStreamApiV1StreamDirectGetLastMsgForSubjectParams,
    ),
    message=type(None),
    reply=bytes,
    error=bytes,
)
