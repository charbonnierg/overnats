# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Server:
    """
    Details about the server the client connected to
    """

    name: str
    """
    The configured name for the server, matches ID when unconfigured
    """
    host: str
    """
    The host this server runs on, typically a IP address
    """
    id: str
    """
    The unique server ID for this node
    """
    ver: str
    """
    The version NATS running on the server
    """
    seq: int
    """
    Internal server sequence ID
    """
    jetstream: bool
    """
    Indicates if this server has JetStream enabled
    """
    time: str
    """
    The local time of the server
    """
    cluster: Optional[str] = None
    """
    The cluster the server belongs to
    """


@dataclass
class Sent:
    """
    Data sent by this account
    """

    msgs: Optional[int] = None
    """
    The number of messages handled by the client
    """
    bytes: Optional[int] = None
    """
    The number of bytes handled by the client
    """


@dataclass
class Received:
    """
    Data received by this account
    """

    msgs: Optional[int] = None
    """
    The number of messages handled by the client
    """
    bytes: Optional[int] = None
    """
    The number of bytes handled by the client
    """


@dataclass
class IoNatsServerAdvisoryV1AccountConnections:
    """
    Regular advisory published with account states
    """

    id: str
    """
    Unique correlation ID for this event
    """
    timestamp: str
    """
    The time this event was created in RFC3339 format
    """
    server: Server
    """
    Details about the server the client connected to
    """
    acc: str
    """
    The account the update is for
    """
    conns: int
    """
    The number of active client connections to the server
    """
    leafnodes: int
    """
    The number of active leafnode connections to the server
    """
    total_conns: int
    """
    The combined client and leafnode account connections
    """
    type: str = "io.nats.server.advisory.v1.account_connections"
    sent: Optional[Sent] = None
    """
    Data sent by this account
    """
    received: Optional[Received] = None
    """
    Data received by this account
    """
    slow_consumers: Optional[int] = None
    """
    The number of slow consumer errors this account encountered
    """
