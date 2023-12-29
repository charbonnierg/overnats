# @generated

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union


@dataclass
class SubjectTransform:
    """
    Subject transform to apply to matching messages
    """

    src: str
    """
    The subject transform source
    """
    dest: str
    """
    The subject transform destination
    """


class Retention(Enum):
    """
    How messages are retained in the Stream, once this is exceeded old messages are removed.
    """

    limits = "limits"
    interest = "interest"
    workqueue = "workqueue"


class Storage(Enum):
    """
    The storage backend to use for the Stream.
    """

    file = "file"
    memory = "memory"


class Compression(Enum):
    """
    Optional compression algorithm used for the Stream.
    """

    none = "none"
    s2 = "s2"


class Discard(Enum):
    """
    When a Stream reach it's limits either old messages are deleted or new ones are denied
    """

    old = "old"
    new = "new"


@dataclass
class Placement:
    """
    Placement directives to consider when placing replicas of this stream, random placement when unset
    """

    cluster: str
    """
    The desired cluster name to place the stream
    """
    tags: Optional[List[str]] = None
    """
    Tags required on servers hosting this stream
    """


@dataclass
class SubjectTransform35:
    """
    Subject transform to apply to matching messages going into the stream
    """

    src: str
    """
    The subject transform source
    """
    dest: str
    """
    The subject transform destination
    """


@dataclass
class External:
    """
    Configuration referencing a stream source in another account or JetStream domain
    """

    api: str
    """
    The subject prefix that imports the other account/domain $JS.API.CONSUMER.> subjects
    """
    deliver: Optional[str] = None
    """
    The delivery subject to use for the push consumer
    """


@dataclass
class Mirror:
    """
    Maintains a 1:1 mirror of another stream with name matching this property.  When a mirror is configured subjects and sources must be empty.
    """

    name: str
    """
    Stream name
    """
    opt_start_seq: Optional[int] = None
    """
    Sequence to start replicating from
    """
    opt_start_time: Optional[str] = None
    """
    Time stamp to start replicating from
    """
    filter_subject: Optional[str] = None
    """
    Replicate only a subset of messages based on filter
    """
    subject_transforms: Optional[List[SubjectTransform35]] = None
    """
    The subject filtering sources and associated destination transforms
    """
    external: Optional[External] = None
    """
    Configuration referencing a stream source in another account or JetStream domain
    """


@dataclass
class Source:
    """
    Defines a source where streams should be replicated from
    """

    name: str
    """
    Stream name
    """
    opt_start_seq: Optional[int] = None
    """
    Sequence to start replicating from
    """
    opt_start_time: Optional[str] = None
    """
    Time stamp to start replicating from
    """
    filter_subject: Optional[str] = None
    """
    Replicate only a subset of messages based on filter
    """
    subject_transforms: Optional[List[SubjectTransform35]] = None
    """
    The subject filtering sources and associated destination transforms
    """
    external: Optional[External] = None
    """
    Configuration referencing a stream source in another account or JetStream domain
    """


@dataclass
class Republish:
    """
    Rules for republishing messages from a stream with subject mapping onto new subjects for partitioning and more
    """

    src: str
    """
    The source subject to republish
    """
    dest: str
    """
    The destination to publish to
    """
    headers_only: Optional[bool] = False
    """
    Only send message headers, no bodies
    """


@dataclass
class Config:
    """
    The active configuration for the Stream
    """

    retention: Retention
    """
    How messages are retained in the Stream, once this is exceeded old messages are removed.
    """
    max_consumers: int
    """
    How many Consumers can be defined for a given Stream. -1 for unlimited.
    """
    max_msgs: int
    """
    How many messages may be in a Stream, oldest messages will be removed if the Stream exceeds this size. -1 for unlimited.
    """
    max_bytes: int
    """
    How big the Stream may be, when the combined stream size exceeds this old messages are removed. -1 for unlimited.
    """
    max_age: int
    """
    Maximum age of any message in the stream, expressed in nanoseconds. 0 for unlimited.
    """
    storage: Storage
    """
    The storage backend to use for the Stream.
    """
    num_replicas: int
    """
    How many replicas to keep for each message.
    """
    name: Optional[str] = None
    """
    A unique name for the Stream, empty for Stream Templates.
    """
    description: Optional[str] = None
    """
    A short description of the purpose of this stream
    """
    subjects: Optional[List[str]] = None
    """
    A list of subjects to consume, supports wildcards. Must be empty when a mirror is configured. May be empty when sources are configured.
    """
    subject_transform: Optional[SubjectTransform] = None
    """
    Subject transform to apply to matching messages
    """
    max_msgs_per_subject: Optional[int] = -1
    """
    For wildcard streams ensure that for every unique subject this many messages are kept - a per subject retention limit
    """
    max_msg_size: Optional[int] = -1
    """
    The largest message that will be accepted by the Stream. -1 for unlimited.
    """
    compression: Optional[Compression] = Compression.none
    """
    Optional compression algorithm used for the Stream.
    """
    first_seq: Optional[int] = None
    """
    A custom sequence to use for the first message in the stream
    """
    no_ack: Optional[bool] = False
    """
    Disables acknowledging messages that are received by the Stream.
    """
    template_owner: Optional[str] = None
    """
    When the Stream is managed by a Stream Template this identifies the template that manages the Stream.
    """
    discard: Optional[Discard] = Discard.old
    """
    When a Stream reach it's limits either old messages are deleted or new ones are denied
    """
    duplicate_window: Optional[int] = 0
    """
    The time window to track duplicate messages for, expressed in nanoseconds. 0 for default
    """
    placement: Optional[Placement] = None
    """
    Placement directives to consider when placing replicas of this stream, random placement when unset
    """
    mirror: Optional[Mirror] = None
    """
    Maintains a 1:1 mirror of another stream with name matching this property.  When a mirror is configured subjects and sources must be empty.
    """
    sources: Optional[List[Source]] = None
    """
    List of Stream names to replicate into this Stream
    """
    sealed: Optional[bool] = False
    """
    Sealed streams do not allow messages to be deleted via limits or API, sealed streams can not be unsealed via configuration update. Can only be set on already created streams via the Update API
    """
    deny_delete: Optional[bool] = False
    """
    Restricts the ability to delete messages from a stream via the API. Cannot be changed once set to true
    """
    deny_purge: Optional[bool] = False
    """
    Restricts the ability to purge messages from a stream via the API. Cannot be change once set to true
    """
    allow_rollup_hdrs: Optional[bool] = False
    """
    Allows the use of the Nats-Rollup header to replace all contents of a stream, or subject in a stream, with a single new message
    """
    allow_direct: Optional[bool] = False
    """
    Allow higher performance, direct access to get individual messages
    """
    mirror_direct: Optional[bool] = False
    """
    Allow higher performance, direct access for mirrors as well
    """
    republish: Optional[Republish] = None
    """
    Rules for republishing messages from a stream with subject mapping onto new subjects for partitioning and more
    """
    discard_new_per_subject: Optional[bool] = False
    """
    When discard policy is new and the stream is one with max messages per subject set, this will apply the new behavior to every subject. Essentially turning discard new from maximum number of subjects into maximum number of messages in a subject.
    """
    metadata: Optional[Dict[str, str]] = None
    """
    Additional metadata for the Stream
    """


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
class State:
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
class Error:
    code: int
    """
    HTTP like error code in the 300 to 500 range
    """
    description: Optional[str] = None
    """
    A human friendly description of the error
    """
    err_code: Optional[int] = None
    """
    The NATS error code unique to each kind of error
    """


@dataclass
class Mirror13:
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
    subject_transforms: Optional[List[SubjectTransform35]] = None
    """
    The subject filtering sources and associated destination transforms
    """
    external: Optional[External] = None
    """
    Configuration referencing a stream source in another account or JetStream domain
    """
    error: Optional[Error] = None


@dataclass
class Source13:
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
    subject_transforms: Optional[List[SubjectTransform35]] = None
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


@dataclass
class IoNatsJetstreamApiV1StreamUpdateResponse1:
    """
    A response from the JetStream $JS.API.STREAM.UPDATE API
    """

    type: str
    config: Config
    """
    The active configuration for the Stream
    """
    state: State
    """
    Detail about the current State of the Stream
    """
    created: str
    """
    Timestamp when the stream was created
    """
    ts: Optional[str] = None
    """
    The server time the stream info was created
    """
    cluster: Optional[Cluster] = None
    mirror: Optional[Mirror13] = None
    """
    Information about an upstream stream source in a mirror
    """
    sources: Optional[List[Source13]] = None
    """
    Streams being sourced into this Stream
    """
    alternates: Optional[List[Alternate]] = None
    """
    List of mirrors sorted by priority
    """


@dataclass
class IoNatsJetstreamApiV1StreamUpdateResponse2:
    """
    A response from the JetStream $JS.API.STREAM.UPDATE API
    """

    type: str
    error: Error


IoNatsJetstreamApiV1StreamUpdateResponse = Union[
    IoNatsJetstreamApiV1StreamUpdateResponse1, IoNatsJetstreamApiV1StreamUpdateResponse2
]
