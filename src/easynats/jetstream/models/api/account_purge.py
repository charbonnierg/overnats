# @generated

from dataclasses import dataclass
from typing import Optional, Union

from easynats.typed import Channel, Command

from .api_error import JetStreamApiV1Error


@dataclass
class AccountPurgeResponse:
    """
    A response from the JetStream $JS.API.ACCOUNT.PURGE API
    """

    type: Optional[str] = None
    initiated: Optional[bool] = False
    """
    If the purge operation was succesfully started
    """


JetstreamApiV1AccountPurgeResponse = Union[JetStreamApiV1Error, AccountPurgeResponse]


PURGE_ACCOUNT = Command(
    channel=Channel(
        subject="PURGE",
        parameters=type(None),
    ),
    message=type(None),
    reply=JetstreamApiV1AccountPurgeResponse,
    error=bytes,
)
