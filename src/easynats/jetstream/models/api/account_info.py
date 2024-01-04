# @generated

from dataclasses import dataclass
from typing import Dict, Optional, Union

from easynats.typed import Channel, Command

from .api_error import JetStreamApiV1Error


@dataclass
class Limits:
    max_memory: int
    """
    The maximum amount of Memory storage Stream Messages may consume
    """
    max_storage: int
    """
    The maximum amount of File storage Stream Messages may consume
    """
    max_streams: int
    """
    The maximum number of Streams an account can create
    """
    max_consumers: int
    """
    The maximum number of Consumer an account can create
    """
    max_bytes_required: Optional[bool] = False
    """
    Indicates if Streams created in this account requires the max_bytes property set
    """
    max_ack_pending: Optional[int] = None
    """
    The maximum number of outstanding ACKs any consumer may configure
    """
    memory_max_stream_bytes: Optional[int] = -1
    """
    The maximum size any single memory stream may be
    """
    storage_max_stream_bytes: Optional[int] = -1
    """
    The maximum size any single storage based stream may be
    """


@dataclass
class Tiers:
    memory: int
    """
    Memory Storage being used for Stream Message storage
    """
    storage: int
    """
    File Storage being used for Stream Message storage
    """
    streams: int
    """
    Number of active Streams
    """
    consumers: int
    """
    Number of active Consumers
    """
    limits: Limits


@dataclass
class Api:
    total: int
    """
    Total number of API requests received for this account
    """
    errors: int
    """
    API requests that resulted in an error response
    """


@dataclass
class AccountInfoResponse:
    """
    A response from the JetStream $JS.API.INFO API
    """

    type: str
    memory: int
    """
    Memory Storage being used for Stream Message storage
    """
    storage: int
    """
    File Storage being used for Stream Message storage
    """
    streams: int
    """
    Number of active Streams
    """
    consumers: int
    """
    Number of active Consumers
    """
    limits: Limits
    api: Api
    domain: Optional[str] = None
    """
    The JetStream domain this account is in
    """
    tiers: Optional[Dict[str, Tiers]] = None


JetstreamApiV1AccountInfoResponse = Union[AccountInfoResponse, JetStreamApiV1Error]


GET_ACCOUNT_INFO = Command(
    channel=Channel(
        subject="INFO",
        parameters=type(None),
    ),
    message=type(None),
    reply=JetstreamApiV1AccountInfoResponse,
    error=bytes,
)
