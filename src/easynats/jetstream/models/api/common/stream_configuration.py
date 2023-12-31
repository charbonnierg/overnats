# @generated

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, TypeVar

T = TypeVar("T")


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

    cluster: Optional[str] = None
    """
    The desired cluster name to place the stream
    """
    tags: Optional[List[str]] = None
    """
    Tags required on servers hosting this stream
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
    subject_transforms: Optional[List[SubjectTransform]] = None
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
    subject_transforms: Optional[List[SubjectTransform]] = None
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
class StreamConfig:
    """
    The data structure that describe the configuration of a NATS JetStream Stream
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
    duplicate_window: Optional[int] = None
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

    @classmethod
    def new(
        cls,
        name: str,
        subjects: Optional[List[str]] = None,
        retention: Optional[Retention] = None,
        max_consumers: Optional[int] = None,
        max_msgs: Optional[int] = None,
        max_bytes: Optional[int] = None,
        max_age: Optional[int] = None,
        storage: Optional[Storage] = None,
        num_replicas: Optional[int] = None,
        duplicate_window: Optional[int] = None,
        description: Optional[str] = None,
        subject_transform: Optional[SubjectTransform] = None,
        max_msgs_per_subject: Optional[int] = None,
        max_msg_size: Optional[int] = None,
        compression: Optional[Compression] = None,
        first_seq: Optional[int] = None,
        no_ack: Optional[bool] = None,
        discard: Optional[Discard] = None,
        placement: Optional[Placement] = None,
        mirror: Optional[Mirror] = None,
        sources: Optional[List[Source]] = None,
        sealed: Optional[bool] = None,
        deny_delete: Optional[bool] = None,
        deny_purge: Optional[bool] = None,
        allow_rollup_hdrs: Optional[bool] = None,
        allow_direct: Optional[bool] = None,
        mirror_direct: Optional[bool] = None,
        republish: Optional[Republish] = None,
        discard_new_per_subject: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> "StreamConfig":
        return cls(
            name=name,
            max_consumers=get_or(max_consumers, -1),
            max_msgs=get_or(max_msgs, -1),
            max_bytes=get_or(max_bytes, -1),
            max_age=get_or(max_age, 0),
            storage=get_or(storage, Storage.file),
            retention=get_or(retention, Retention.limits),
            num_replicas=get_or(num_replicas, 1),
            duplicate_window=get_or(duplicate_window, 120000000000),
            subjects=subjects,
            description=description,
            subject_transform=subject_transform,
            max_msgs_per_subject=get_or(max_msgs_per_subject, -1),
            max_msg_size=get_or(max_msg_size, -1),
            compression=get_or(compression, Compression.none),
            first_seq=first_seq,
            no_ack=get_or(no_ack, False),
            discard=get_or(discard, Discard.old),
            placement=placement,
            mirror=mirror,
            sources=sources,
            sealed=get_or(sealed, False),
            deny_delete=get_or(deny_delete, False),
            deny_purge=get_or(deny_purge, False),
            allow_rollup_hdrs=get_or(allow_rollup_hdrs, False),
            allow_direct=get_or(allow_direct, False),
            mirror_direct=get_or(mirror_direct, False),
            republish=republish,
            discard_new_per_subject=get_or(discard_new_per_subject, False),
            metadata=metadata,
        )


def get_or(value: Optional[T], default: T) -> T:
    return default if value is None else value
