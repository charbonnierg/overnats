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
class JetStreamApiV1Error:
    """
    A response from the JetStream $JS.API.INFO API
    """

    type: str
    error: Error
