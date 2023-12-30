from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Delivered:
    """
    The last message delivered from this Consumer
    """

    consumer_seq: int
    """
    The sequence number of the Consumer
    """
    stream_seq: int
    """
    The sequence number of the Stream
    """
    last_active: Optional[str] = None
    """
    The last time a message was delivered or acknowledged (for ack_floor)
    """


@dataclass
class AckFloor:
    """
    The highest contiguous acknowledged message
    """

    consumer_seq: int
    """
    The sequence number of the Consumer
    """
    stream_seq: int
    """
    The sequence number of the Stream
    """
    last_active: Optional[str] = None
    """
    The last time a message was delivered or acknowledged (for ack_floor)
    """


@dataclass
class Replica:
    name: str
    """
    The server name of the peer
    """
    current: bool
    """
    Indicates if the server is up to date and synchronised
    """
    active: float
    """
    Nanoseconds since this peer was last seen
    """
    offline: Optional[bool] = False
    """
    Indicates the node is considered offline by the group
    """
    lag: Optional[int] = None
    """
    How many uncommitted operations this peer is behind the leader
    """


@dataclass
class Cluster:
    name: Optional[str] = None
    """
    The cluster name
    """
    leader: Optional[str] = None
    """
    The server name of the RAFT leader
    """
    replicas: Optional[List[Replica]] = None
    """
    The members of the RAFT cluster
    """
