# @generated

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


@dataclass
class Requestor:
    """
    Details about the service requestor
    """

    acc: str
    """
    The account this user logged in to
    """
    start: Optional[str] = None
    """
    Timestamp when the client connected
    """
    stop: Optional[str] = None
    """
    Timestamp when the client disconnected
    """
    host: Optional[str] = None
    """
    The remote host the client is connected from
    """
    id: Optional[str] = None
    """
    The internally assigned client ID for this connection
    """
    user: Optional[str] = None
    """
    The clients username
    """
    name: Optional[str] = None
    """
    The name presented by the client during connection
    """
    lang: Optional[str] = None
    """
    The programming language library in use by the client
    """
    ver: Optional[str] = None
    """
    The version of the client library in use
    """
    rtt: Optional[float] = None
    """
    The last known latency between the NATS Server and the Client in nanoseconds
    """
    server: Optional[str] = None
    """
    The server that the client was connected to
    """
    cluster: Optional[str] = None
    """
    The cluster name the server is connected to
    """
    alts: Optional[List[str]] = None
    jwt: Optional[str] = None
    """
    The JWT presented in the connection
    """
    issuer_key: Optional[str] = None
    """
    The public signing key or account identity key used to issue the user
    """
    name_tag: Optional[str] = None
    """
    The name extracted from the user JWT claim
    """
    kind: Optional[str] = None
    """
    The kind of client. Can be Client/Leafnode/Router/Gateway/JetStream/Account/System
    """
    client_type: Optional[str] = None
    """
    The type of client. When kind is Client, this contains the type: mqtt/websocket/nats
    """
    tags: Optional[List[str]] = None
    """
    Tags extracted from the JWT
    """


@dataclass
class Responder:
    """
    Details about the service responder
    """

    acc: str
    """
    The account this user logged in to
    """
    start: Optional[str] = None
    """
    Timestamp when the client connected
    """
    stop: Optional[str] = None
    """
    Timestamp when the client disconnected
    """
    host: Optional[str] = None
    """
    The remote host the client is connected from
    """
    id: Optional[str] = None
    """
    The internally assigned client ID for this connection
    """
    user: Optional[str] = None
    """
    The clients username
    """
    name: Optional[str] = None
    """
    The name presented by the client during connection
    """
    lang: Optional[str] = None
    """
    The programming language library in use by the client
    """
    ver: Optional[str] = None
    """
    The version of the client library in use
    """
    rtt: Optional[float] = None
    """
    The last known latency between the NATS Server and the Client in nanoseconds
    """
    server: Optional[str] = None
    """
    The server that the client was connected to
    """
    cluster: Optional[str] = None
    """
    The cluster name the server is connected to
    """
    alts: Optional[List[str]] = None
    jwt: Optional[str] = None
    """
    The JWT presented in the connection
    """
    issuer_key: Optional[str] = None
    """
    The public signing key or account identity key used to issue the user
    """
    name_tag: Optional[str] = None
    """
    The name extracted from the user JWT claim
    """
    kind: Optional[str] = None
    """
    The kind of client. Can be Client/Leafnode/Router/Gateway/JetStream/Account/System
    """
    client_type: Optional[str] = None
    """
    The type of client. When kind is Client, this contains the type: mqtt/websocket/nats
    """
    tags: Optional[List[str]] = None
    """
    Tags extracted from the JWT
    """


class Status(Enum):
    """
    The status of the request. 200 OK, 400 Bad Request, no reply subject. 408 Request Timeout, requester lost interest before request completed. 503 Service Unavailable. 504 Service Timeout.
    """

    integer_200 = 200
    integer_400 = 400
    integer_408 = 408
    integer_503 = 503
    integer_504 = 504


@dataclass
class IoNatsServerMetricV1ServiceLatency:
    """
    Metric published about sampled service requests showing request status and latencies
    """

    id: str
    """
    Unique correlation ID for this event
    """
    timestamp: str
    """
    The time this event was created in RFC3339 format
    """
    status: Status
    """
    The status of the request. 200 OK, 400 Bad Request, no reply subject. 408 Request Timeout, requester lost interest before request completed. 503 Service Unavailable. 504 Service Timeout.
    """
    start: str
    """
    The time the request started in RFC3339 format
    """
    service: int
    """
    The time taken by the service to perform the request in nanoseconds
    """
    system: int
    """
    Time spend traversing the NATS network in nanoseconds
    """
    total: int
    """
    The overall request duration in nanoseconds
    """
    type: str = "io.nats.server.metric.v1.service_latency"
    requestor: Optional[Requestor] = None
    """
    Details about the service requestor
    """
    responder: Optional[Responder] = None
    """
    Details about the service responder
    """
    header: Optional[Dict[str, List[str]]] = None
    """
    When header based latency is enabled, the headers that triggered the event
    """
    error: Optional[str] = None
    """
    A description of the status code when not 200
    """
