# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Endpoint:
    """
    Information about an endpoint
    """

    name: str
    """
    The endopoint name
    """
    subject: str
    """
    The subject the endpoint listens on
    """
    metadata: Optional[Dict[str, str]] = None
    queue_group: Optional[str] = None
    """
    The queue group this endpoint listens on for requests
    """


@dataclass
class IoNatsMicroV1InfoResponse:
    """
    A response from the NATS Micro $SRV.INFO API
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
    description: str
    """
    The description of the service supplied as configuration while creating the service
    """
    type: str = "io.nats.micro.v1.info_response"
    metadata: Optional[Dict[str, str]] = None
    endpoints: Optional[List[Endpoint]] = None
    """
    List of declared endpoints
    """
