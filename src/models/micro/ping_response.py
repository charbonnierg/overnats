# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class IoNatsMicroV1PingResponse:
    """
    A response from the NATS Micro $SRV.PING API
    """

    name: str
    """
    The kind of the service. Shared by all the services that have the same name
    """
    id: str
    """
    A unique ID for this instance of a service
    """
    version: str
    """
    The version of the service
    """
    type: str = "io.nats.micro.v1.ping_response"
    metadata: Optional[Dict[str, str]] = None
