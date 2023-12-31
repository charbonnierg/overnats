# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class IoNatsJetstreamApiV1ConsumerGetnextRequest:
    """
    A request to the JetStream $JS.API.CONSUMER.MSG.NEXT API
    """

    expires: Optional[int] = None
    """
    A duration from now when the pull should expire, stated in nanoseconds, 0 for no expiry
    """
    batch: Optional[int] = None
    """
    How many messages the server should deliver to the requestor
    """
    max_bytes: Optional[int] = None
    """
    Sends at most this many bytes to the requestor, limited by consumer configuration max_bytes
    """
    no_wait: Optional[bool] = None
    """
    When true a response with a 404 status header will be returned when no messages are available
    """
    idle_heartbeat: Optional[int] = None
    """
    When not 0 idle heartbeats will be sent on this interval
    """
