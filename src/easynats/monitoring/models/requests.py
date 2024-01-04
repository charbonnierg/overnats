from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SortOption(str, Enum):
    # Don't sort
    NO_SORT = ""
    # Connection ID
    CID = "cid"
    # Connection start time, same as CID
    START = "start"
    # Number of subscriptions
    SUBS = "subs"
    # Amount of data in bytes waiting to be sent to client
    PENDING = "pending"
    # Number of messages sent
    MSGS_TO = "msgs_to"
    # Number of messages received
    MSGS_FROM = "msgs_from"
    # Number of bytes sent
    BYTES_TO = "bytes_to"
    # Number of bytes received
    BYTES_FROM = "bytes_from"
    # Last activity
    LAST = "last"
    # Amount of inactivity
    IDLE = "idle"
    # Lifetime of the connection
    UPTIME = "uptime"
    # Stop time for a closed connection
    STOP = "stop"
    # Reason for a closed connection
    REASON = "reason"


class SubsOption(str, Enum):
    FALSE = "false"
    # Don't include subscriptions at all
    TRUE = "true"
    # Include simple stats
    DETAIL = "detail"
    # Include detailed stats


class StateOption(int, Enum):
    OPEN = 0
    CLOSED = 1
    ALL = 2


@dataclass
class VarzRequest:
    server_name: str | None = None
    cluster: str | None = None
    host: str | None = None
    tags: str | None = None


@dataclass
class JszRequest:
    acc: str | None = None
    accounts: bool | None = None
    streams: bool | None = None
    consumers: bool | None = None
    config: bool | None = None
    leader_only: bool = False
    offset: int = 0
    limit: int = 1024
    server_name: str | None = None
    cluster: str | None = None
    host: str | None = None
    tags: str | None = None


@dataclass
class ConnzRequest:
    sort: SortOption = SortOption.NO_SORT
    auth: bool = False
    subs: SubsOption = SubsOption.FALSE
    offset: int = 0
    limit: int = 1024
    cid: int | None = None
    state: StateOption = StateOption.OPEN
    mqtt_client: str | None = None
    server_name: str | None = None
    cluster: str | None = None
    host: str | None = None
    tags: str | None = None


@dataclass
class InfoRequest:
    server_name: str | None = None
    cluster: str | None = None
    host: str | None = None
    tags: str | None = None


@dataclass
class AccountzRequest(InfoRequest):
    acc: str | None = None


@dataclass
class StatszRequest:
    unused: bool = False


@dataclass
class SubszRequest:
    subs: bool = False
    offset: int = 0
    limit: int = 1024
    test: str | None = None
    server_name: str | None = None
    cluster: str | None = None
    host: str | None = None
    tags: str | None = None


@dataclass
class RoutezRequest:
    subs: SubsOption = SubsOption.FALSE
    server_name: str | None = None
    cluster: str | None = None
    host: str | None = None
    tags: str | None = None


@dataclass
class LeafzRequest:
    subs: bool = False
    server_name: str | None = None
    cluster: str | None = None
    host: str | None = None
    tags: str | None = None


@dataclass
class GatewayzRequest:
    accs: bool = False
    gw_name: str | None = None
    acc_name: str | None = None
    server_name: str | None = None
    cluster: str | None = None
    host: str | None = None
    tags: str | None = None


@dataclass
class HealthzRequest:
    js_enabled: bool = False
    js_server_only: bool = False
