# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Endpoint:
    """
    Statistics about a specific service endpoint
    """

    name: str
    """
    The endpoint name
    """
    subject: str
    """
    The subject the endpoint listens on
    """
    num_requests: int
    """
    The number of requests this endpoint received
    """
    num_errors: int
    """
    The number of errors this endpoint encountered
    """
    last_error: str
    """
    The last error the service encountered
    """
    processing_time: int
    """
    How long, in total, was spent processing requests in the handler
    """
    average_processing_time: int
    """
    The average time spent processing requests
    """
    queue_group: Optional[str] = None
    """
    The queue group this endpoint listens on for requests
    """
    data: Optional[Dict[str, Any]] = None
    """
    Additional statistics the endpoint makes available
    """


@dataclass
class IoNatsMicroV1StatsResponse:
    """
    A response from the NATS Micro $SRV.STATS API
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
    started: str
    """
    The time the service was stated in RFC3339 format
    """
    endpoints: List[Endpoint]
    """
    Statistics for each known endpoint
    """
    type: str = "io.nats.micro.v1.stats_response"
    metadata: Optional[Dict[str, str]] = None
