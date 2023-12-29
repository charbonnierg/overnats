# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Client:
    """
    Details about the client that connected to the server
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
class IoNatsJetstreamAdvisoryV1RestoreComplete:
    """
    An Advisory sent when a Stream restore is completed
    """

    id: str
    """
    Unique correlation ID for this event
    """
    timestamp: str
    """
    The time this event was created in RFC3339 format
    """
    stream: str
    """
    The Stream being restored
    """
    start: str
    """
    The time the Restore process started
    """
    end: str
    """
    The time the Restore was completed
    """
    bytes: int
    """
    The number of bytes that was received
    """
    client: Client
    """
    Details about the client that connected to the server
    """
    type: str = "io.nats.jetstream.advisory.v1.restore_complete"
