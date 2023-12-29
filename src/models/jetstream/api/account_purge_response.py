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
class IoNatsJetstreamApiV1AccountPurgeResponse1:
    """
    A response from the JetStream $JS.API.ACCOUNT.PURGE API
    """

    error: Error
    type: Optional[str] = None


@dataclass
class IoNatsJetstreamApiV1AccountPurgeResponse2:
    """
    A response from the JetStream $JS.API.ACCOUNT.PURGE API
    """

    type: Optional[str] = None
    initiated: Optional[bool] = False
    """
    If the purge operation was succesfully started
    """


IoNatsJetstreamApiV1AccountPurgeResponse = Union[
    IoNatsJetstreamApiV1AccountPurgeResponse1, IoNatsJetstreamApiV1AccountPurgeResponse2
]
