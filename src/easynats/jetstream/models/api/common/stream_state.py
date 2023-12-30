# @generated

from dataclasses import dataclass
from typing import Dict, List, Optional

from ..api_error import Error
from .stream_configuration import SubjectTransform

DeletedItem = int


@dataclass
class Lost:
    """
    Records messages that were damaged and unrecoverable
    """

    msgs: Optional[List[int]] = None
    """
    The messages that were lost
    """
    bytes: Optional[int] = None
    """
    The number of bytes that were lost
    """


@dataclass
class StreamState:
    """
    Detail about the current State of the Stream
    """

    messages: int
    """
    Number of messages stored in the Stream
    """
    bytes: int
    """
    Combined size of all messages in the Stream
    """
    first_seq: int
    """
    Sequence number of the first message in the Stream
    """
    last_seq: int
    """
    Sequence number of the last message in the Stream
    """
    consumer_count: int
    """
    Number of Consumers attached to the Stream
    """
    first_ts: Optional[str] = None
    """
    The timestamp of the first message in the Stream
    """
    last_ts: Optional[str] = None
    """
    The timestamp of the last message in the Stream
    """
    deleted: Optional[List[DeletedItem]] = None
    """
    IDs of messages that were deleted using the Message Delete API or Interest based streams removing messages out of order
    """
    subjects: Optional[Dict[str, int]] = None
    """
    Subjects and their message counts when a subjects_filter was set
    """
    num_subjects: Optional[int] = None
    """
    The number of unique subjects held in the stream
    """
    num_deleted: Optional[int] = None
    """
    The number of deleted messages
    """
    lost: Optional[Lost] = None
    """
    Records messages that were damaged and unrecoverable
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


@dataclass
class External:
    """
    Configuration referencing a stream source in another account or JetStream domain
    """

    api: str
    """
    The subject prefix that imports the other account/domain $JS.api.consumers.> subjects
    """
    deliver_subject: Optional[str] = None
    """
    The delivery subject used for the push consumer
    """


@dataclass
class Mirror:
    """
    Information about an upstream stream source in a mirror
    """

    name: str
    """
    The name of the Stream being replicated
    """
    lag: int
    """
    How many messages behind the mirror operation is
    """
    active: int
    """
    When last the mirror had activity, in nanoseconds. Value will be -1 when there has been no activity.
    """
    filter_subject: Optional[str] = None
    """
    The subject filter to apply to the messages
    """
    subject_transforms: Optional[List[SubjectTransform]] = None
    """
    The subject filtering sources and associated destination transforms
    """
    external: Optional[External] = None
    """
    Configuration referencing a stream source in another account or JetStream domain
    """
    error: Optional[Error] = None


@dataclass
class Source:
    """
    Information about an upstream stream source in a mirror
    """

    name: str
    """
    The name of the Stream being replicated
    """
    lag: int
    """
    How many messages behind the mirror operation is
    """
    active: int
    """
    When last the mirror had activity, in nanoseconds. Value will be -1 when there has been no activity.
    """
    filter_subject: Optional[str] = None
    """
    The subject filter to apply to the messages
    """
    subject_transforms: Optional[List[SubjectTransform]] = None
    """
    The subject filtering sources and associated destination transforms
    """
    external: Optional[External] = None
    """
    Configuration referencing a stream source in another account or JetStream domain
    """
    error: Optional[Error] = None


@dataclass
class Alternate:
    """
    An alternate location to read mirrored data
    """

    name: str
    """
    The mirror stream name
    """
    cluster: str
    """
    The name of the cluster holding the stream
    """
    domain: Optional[str] = None
    """
    The domain holding the string
    """
