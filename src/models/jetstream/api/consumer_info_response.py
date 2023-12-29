# @generated

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union


class DeliverPolicy(Enum):
    all = "all"


@dataclass
class Config151:
    deliver_policy: DeliverPolicy


class DeliverPolicy19(Enum):
    last = "last"


@dataclass
class Config152:
    deliver_policy: DeliverPolicy19


class DeliverPolicy20(Enum):
    new = "new"


@dataclass
class Config153:
    deliver_policy: DeliverPolicy20


class DeliverPolicy21(Enum):
    by_start_sequence = "by_start_sequence"


@dataclass
class Config154:
    deliver_policy: DeliverPolicy21
    opt_start_seq: int


class DeliverPolicy22(Enum):
    by_start_time = "by_start_time"


@dataclass
class Config155:
    deliver_policy: DeliverPolicy22
    opt_start_time: str


class DeliverPolicy23(Enum):
    last_per_subject = "last_per_subject"


@dataclass
class Config156:
    deliver_policy: DeliverPolicy23


class AckPolicy(Enum):
    none = "none"
    all = "all"
    explicit = "explicit"


class ReplayPolicy(Enum):
    instant = "instant"
    original = "original"


@dataclass
class Config157:
    ack_policy: AckPolicy
    replay_policy: ReplayPolicy
    durable_name: Optional[str] = None
    """
    A unique name for a durable consumer
    """
    name: Optional[str] = None
    """
    A unique name for a consumer
    """
    description: Optional[str] = None
    """
    A short description of the purpose of this consumer
    """
    deliver_subject: Optional[str] = None
    ack_wait: Optional[int] = "30000000000"
    """
    How long (in nanoseconds) to allow messages to remain un-acknowledged before attempting redelivery
    """
    max_deliver: Optional[int] = -1
    """
    The number of times a message will be redelivered to consumers if not acknowledged in time
    """
    filter_subject: Optional[str] = None
    """
    Filter the stream by a single subjects
    """
    filter_subjects: Optional[List[str]] = None
    """
    Filter the stream by multiple subjects
    """
    sample_freq: Optional[str] = None
    rate_limit_bps: Optional[int] = None
    """
    The rate at which messages will be delivered to clients, expressed in bit per second
    """
    max_ack_pending: Optional[int] = 1000
    """
    The maximum number of messages without acknowledgement that can be outstanding, once this limit is reached message delivery will be suspended
    """
    idle_heartbeat: Optional[int] = None
    """
    If the Consumer is idle for more than this many nano seconds a empty message with Status header 100 will be sent indicating the consumer is still alive
    """
    flow_control: Optional[bool] = None
    """
    For push consumers this will regularly send an empty mess with Status header 100 and a reply subject, consumers must reply to these messages to control the rate of message delivery
    """
    max_waiting: Optional[int] = 512
    """
    The number of pulls that can be outstanding on a pull consumer, pulls received after this is reached are ignored
    """
    direct: Optional[bool] = False
    """
    Creates a special consumer that does not touch the Raft layers, not for general use by clients, internal use only
    """
    headers_only: Optional[bool] = False
    """
    Delivers only the headers of messages in the stream and not the bodies. Additionally adds Nats-Msg-Size header to indicate the size of the removed payload
    """
    max_batch: Optional[int] = 0
    """
    The largest batch property that may be specified when doing a pull on a Pull Consumer
    """
    max_expires: Optional[int] = 0
    """
    The maximum expires value that may be set when doing a pull on a Pull Consumer
    """
    max_bytes: Optional[int] = 0
    """
    The maximum bytes value that maybe set when dong a pull on a Pull Consumer
    """
    inactive_threshold: Optional[int] = 0
    """
    Duration that instructs the server to cleanup ephemeral consumers that are inactive for that long
    """
    backoff: Optional[List[int]] = None
    """
    List of durations in Go format that represents a retry time scale for NaK'd messages
    """
    num_replicas: Optional[int] = None
    """
    When set do not inherit the replica count from the stream but specifically set it to this amount
    """
    mem_storage: Optional[bool] = False
    """
    Force the consumer state to be kept in memory rather than inherit the setting from the stream
    """
    metadata: Optional[Dict[str, str]] = None
    """
    Additional metadata for the Consumer
    """


@dataclass
class Config158(Config151, Config157):
    ack_policy: AckPolicy
    replay_policy: ReplayPolicy
    deliver_policy: DeliverPolicy
    durable_name: Optional[str] = None
    """
    A unique name for a durable consumer
    """
    name: Optional[str] = None
    """
    A unique name for a consumer
    """
    description: Optional[str] = None
    """
    A short description of the purpose of this consumer
    """
    deliver_subject: Optional[str] = None
    ack_wait: Optional[int] = "30000000000"
    """
    How long (in nanoseconds) to allow messages to remain un-acknowledged before attempting redelivery
    """
    max_deliver: Optional[int] = -1
    """
    The number of times a message will be redelivered to consumers if not acknowledged in time
    """
    filter_subject: Optional[str] = None
    """
    Filter the stream by a single subjects
    """
    filter_subjects: Optional[List[str]] = None
    """
    Filter the stream by multiple subjects
    """
    sample_freq: Optional[str] = None
    rate_limit_bps: Optional[int] = None
    """
    The rate at which messages will be delivered to clients, expressed in bit per second
    """
    max_ack_pending: Optional[int] = 1000
    """
    The maximum number of messages without acknowledgement that can be outstanding, once this limit is reached message delivery will be suspended
    """
    idle_heartbeat: Optional[int] = None
    """
    If the Consumer is idle for more than this many nano seconds a empty message with Status header 100 will be sent indicating the consumer is still alive
    """
    flow_control: Optional[bool] = None
    """
    For push consumers this will regularly send an empty mess with Status header 100 and a reply subject, consumers must reply to these messages to control the rate of message delivery
    """
    max_waiting: Optional[int] = 512
    """
    The number of pulls that can be outstanding on a pull consumer, pulls received after this is reached are ignored
    """
    direct: Optional[bool] = False
    """
    Creates a special consumer that does not touch the Raft layers, not for general use by clients, internal use only
    """
    headers_only: Optional[bool] = False
    """
    Delivers only the headers of messages in the stream and not the bodies. Additionally adds Nats-Msg-Size header to indicate the size of the removed payload
    """
    max_batch: Optional[int] = 0
    """
    The largest batch property that may be specified when doing a pull on a Pull Consumer
    """
    max_expires: Optional[int] = 0
    """
    The maximum expires value that may be set when doing a pull on a Pull Consumer
    """
    max_bytes: Optional[int] = 0
    """
    The maximum bytes value that maybe set when dong a pull on a Pull Consumer
    """
    inactive_threshold: Optional[int] = 0
    """
    Duration that instructs the server to cleanup ephemeral consumers that are inactive for that long
    """
    backoff: Optional[List[int]] = None
    """
    List of durations in Go format that represents a retry time scale for NaK'd messages
    """
    num_replicas: Optional[int] = None
    """
    When set do not inherit the replica count from the stream but specifically set it to this amount
    """
    mem_storage: Optional[bool] = False
    """
    Force the consumer state to be kept in memory rather than inherit the setting from the stream
    """
    metadata: Optional[Dict[str, str]] = None
    """
    Additional metadata for the Consumer
    """


@dataclass
class Config159(Config152, Config157):
    ack_policy: AckPolicy
    replay_policy: ReplayPolicy
    deliver_policy: DeliverPolicy19
    durable_name: Optional[str] = None
    """
    A unique name for a durable consumer
    """
    name: Optional[str] = None
    """
    A unique name for a consumer
    """
    description: Optional[str] = None
    """
    A short description of the purpose of this consumer
    """
    deliver_subject: Optional[str] = None
    ack_wait: Optional[int] = "30000000000"
    """
    How long (in nanoseconds) to allow messages to remain un-acknowledged before attempting redelivery
    """
    max_deliver: Optional[int] = -1
    """
    The number of times a message will be redelivered to consumers if not acknowledged in time
    """
    filter_subject: Optional[str] = None
    """
    Filter the stream by a single subjects
    """
    filter_subjects: Optional[List[str]] = None
    """
    Filter the stream by multiple subjects
    """
    sample_freq: Optional[str] = None
    rate_limit_bps: Optional[int] = None
    """
    The rate at which messages will be delivered to clients, expressed in bit per second
    """
    max_ack_pending: Optional[int] = 1000
    """
    The maximum number of messages without acknowledgement that can be outstanding, once this limit is reached message delivery will be suspended
    """
    idle_heartbeat: Optional[int] = None
    """
    If the Consumer is idle for more than this many nano seconds a empty message with Status header 100 will be sent indicating the consumer is still alive
    """
    flow_control: Optional[bool] = None
    """
    For push consumers this will regularly send an empty mess with Status header 100 and a reply subject, consumers must reply to these messages to control the rate of message delivery
    """
    max_waiting: Optional[int] = 512
    """
    The number of pulls that can be outstanding on a pull consumer, pulls received after this is reached are ignored
    """
    direct: Optional[bool] = False
    """
    Creates a special consumer that does not touch the Raft layers, not for general use by clients, internal use only
    """
    headers_only: Optional[bool] = False
    """
    Delivers only the headers of messages in the stream and not the bodies. Additionally adds Nats-Msg-Size header to indicate the size of the removed payload
    """
    max_batch: Optional[int] = 0
    """
    The largest batch property that may be specified when doing a pull on a Pull Consumer
    """
    max_expires: Optional[int] = 0
    """
    The maximum expires value that may be set when doing a pull on a Pull Consumer
    """
    max_bytes: Optional[int] = 0
    """
    The maximum bytes value that maybe set when dong a pull on a Pull Consumer
    """
    inactive_threshold: Optional[int] = 0
    """
    Duration that instructs the server to cleanup ephemeral consumers that are inactive for that long
    """
    backoff: Optional[List[int]] = None
    """
    List of durations in Go format that represents a retry time scale for NaK'd messages
    """
    num_replicas: Optional[int] = None
    """
    When set do not inherit the replica count from the stream but specifically set it to this amount
    """
    mem_storage: Optional[bool] = False
    """
    Force the consumer state to be kept in memory rather than inherit the setting from the stream
    """
    metadata: Optional[Dict[str, str]] = None
    """
    Additional metadata for the Consumer
    """


@dataclass
class Config1510(Config153, Config157):
    ack_policy: AckPolicy
    replay_policy: ReplayPolicy
    deliver_policy: DeliverPolicy20
    durable_name: Optional[str] = None
    """
    A unique name for a durable consumer
    """
    name: Optional[str] = None
    """
    A unique name for a consumer
    """
    description: Optional[str] = None
    """
    A short description of the purpose of this consumer
    """
    deliver_subject: Optional[str] = None
    ack_wait: Optional[int] = "30000000000"
    """
    How long (in nanoseconds) to allow messages to remain un-acknowledged before attempting redelivery
    """
    max_deliver: Optional[int] = -1
    """
    The number of times a message will be redelivered to consumers if not acknowledged in time
    """
    filter_subject: Optional[str] = None
    """
    Filter the stream by a single subjects
    """
    filter_subjects: Optional[List[str]] = None
    """
    Filter the stream by multiple subjects
    """
    sample_freq: Optional[str] = None
    rate_limit_bps: Optional[int] = None
    """
    The rate at which messages will be delivered to clients, expressed in bit per second
    """
    max_ack_pending: Optional[int] = 1000
    """
    The maximum number of messages without acknowledgement that can be outstanding, once this limit is reached message delivery will be suspended
    """
    idle_heartbeat: Optional[int] = None
    """
    If the Consumer is idle for more than this many nano seconds a empty message with Status header 100 will be sent indicating the consumer is still alive
    """
    flow_control: Optional[bool] = None
    """
    For push consumers this will regularly send an empty mess with Status header 100 and a reply subject, consumers must reply to these messages to control the rate of message delivery
    """
    max_waiting: Optional[int] = 512
    """
    The number of pulls that can be outstanding on a pull consumer, pulls received after this is reached are ignored
    """
    direct: Optional[bool] = False
    """
    Creates a special consumer that does not touch the Raft layers, not for general use by clients, internal use only
    """
    headers_only: Optional[bool] = False
    """
    Delivers only the headers of messages in the stream and not the bodies. Additionally adds Nats-Msg-Size header to indicate the size of the removed payload
    """
    max_batch: Optional[int] = 0
    """
    The largest batch property that may be specified when doing a pull on a Pull Consumer
    """
    max_expires: Optional[int] = 0
    """
    The maximum expires value that may be set when doing a pull on a Pull Consumer
    """
    max_bytes: Optional[int] = 0
    """
    The maximum bytes value that maybe set when dong a pull on a Pull Consumer
    """
    inactive_threshold: Optional[int] = 0
    """
    Duration that instructs the server to cleanup ephemeral consumers that are inactive for that long
    """
    backoff: Optional[List[int]] = None
    """
    List of durations in Go format that represents a retry time scale for NaK'd messages
    """
    num_replicas: Optional[int] = None
    """
    When set do not inherit the replica count from the stream but specifically set it to this amount
    """
    mem_storage: Optional[bool] = False
    """
    Force the consumer state to be kept in memory rather than inherit the setting from the stream
    """
    metadata: Optional[Dict[str, str]] = None
    """
    Additional metadata for the Consumer
    """


@dataclass
class Config1511(Config154, Config157):
    ack_policy: AckPolicy
    replay_policy: ReplayPolicy
    deliver_policy: DeliverPolicy21
    durable_name: Optional[str] = None
    """
    A unique name for a durable consumer
    """
    name: Optional[str] = None
    """
    A unique name for a consumer
    """
    description: Optional[str] = None
    """
    A short description of the purpose of this consumer
    """
    deliver_subject: Optional[str] = None
    ack_wait: Optional[int] = "30000000000"
    """
    How long (in nanoseconds) to allow messages to remain un-acknowledged before attempting redelivery
    """
    max_deliver: Optional[int] = -1
    """
    The number of times a message will be redelivered to consumers if not acknowledged in time
    """
    filter_subject: Optional[str] = None
    """
    Filter the stream by a single subjects
    """
    filter_subjects: Optional[List[str]] = None
    """
    Filter the stream by multiple subjects
    """
    sample_freq: Optional[str] = None
    rate_limit_bps: Optional[int] = None
    """
    The rate at which messages will be delivered to clients, expressed in bit per second
    """
    max_ack_pending: Optional[int] = 1000
    """
    The maximum number of messages without acknowledgement that can be outstanding, once this limit is reached message delivery will be suspended
    """
    idle_heartbeat: Optional[int] = None
    """
    If the Consumer is idle for more than this many nano seconds a empty message with Status header 100 will be sent indicating the consumer is still alive
    """
    flow_control: Optional[bool] = None
    """
    For push consumers this will regularly send an empty mess with Status header 100 and a reply subject, consumers must reply to these messages to control the rate of message delivery
    """
    max_waiting: Optional[int] = 512
    """
    The number of pulls that can be outstanding on a pull consumer, pulls received after this is reached are ignored
    """
    direct: Optional[bool] = False
    """
    Creates a special consumer that does not touch the Raft layers, not for general use by clients, internal use only
    """
    headers_only: Optional[bool] = False
    """
    Delivers only the headers of messages in the stream and not the bodies. Additionally adds Nats-Msg-Size header to indicate the size of the removed payload
    """
    max_batch: Optional[int] = 0
    """
    The largest batch property that may be specified when doing a pull on a Pull Consumer
    """
    max_expires: Optional[int] = 0
    """
    The maximum expires value that may be set when doing a pull on a Pull Consumer
    """
    max_bytes: Optional[int] = 0
    """
    The maximum bytes value that maybe set when dong a pull on a Pull Consumer
    """
    inactive_threshold: Optional[int] = 0
    """
    Duration that instructs the server to cleanup ephemeral consumers that are inactive for that long
    """
    backoff: Optional[List[int]] = None
    """
    List of durations in Go format that represents a retry time scale for NaK'd messages
    """
    num_replicas: Optional[int] = None
    """
    When set do not inherit the replica count from the stream but specifically set it to this amount
    """
    mem_storage: Optional[bool] = False
    """
    Force the consumer state to be kept in memory rather than inherit the setting from the stream
    """
    metadata: Optional[Dict[str, str]] = None
    """
    Additional metadata for the Consumer
    """


@dataclass
class Config1512(Config155, Config157):
    ack_policy: AckPolicy
    replay_policy: ReplayPolicy
    deliver_policy: DeliverPolicy22
    durable_name: Optional[str] = None
    """
    A unique name for a durable consumer
    """
    name: Optional[str] = None
    """
    A unique name for a consumer
    """
    description: Optional[str] = None
    """
    A short description of the purpose of this consumer
    """
    deliver_subject: Optional[str] = None
    ack_wait: Optional[int] = "30000000000"
    """
    How long (in nanoseconds) to allow messages to remain un-acknowledged before attempting redelivery
    """
    max_deliver: Optional[int] = -1
    """
    The number of times a message will be redelivered to consumers if not acknowledged in time
    """
    filter_subject: Optional[str] = None
    """
    Filter the stream by a single subjects
    """
    filter_subjects: Optional[List[str]] = None
    """
    Filter the stream by multiple subjects
    """
    sample_freq: Optional[str] = None
    rate_limit_bps: Optional[int] = None
    """
    The rate at which messages will be delivered to clients, expressed in bit per second
    """
    max_ack_pending: Optional[int] = 1000
    """
    The maximum number of messages without acknowledgement that can be outstanding, once this limit is reached message delivery will be suspended
    """
    idle_heartbeat: Optional[int] = None
    """
    If the Consumer is idle for more than this many nano seconds a empty message with Status header 100 will be sent indicating the consumer is still alive
    """
    flow_control: Optional[bool] = None
    """
    For push consumers this will regularly send an empty mess with Status header 100 and a reply subject, consumers must reply to these messages to control the rate of message delivery
    """
    max_waiting: Optional[int] = 512
    """
    The number of pulls that can be outstanding on a pull consumer, pulls received after this is reached are ignored
    """
    direct: Optional[bool] = False
    """
    Creates a special consumer that does not touch the Raft layers, not for general use by clients, internal use only
    """
    headers_only: Optional[bool] = False
    """
    Delivers only the headers of messages in the stream and not the bodies. Additionally adds Nats-Msg-Size header to indicate the size of the removed payload
    """
    max_batch: Optional[int] = 0
    """
    The largest batch property that may be specified when doing a pull on a Pull Consumer
    """
    max_expires: Optional[int] = 0
    """
    The maximum expires value that may be set when doing a pull on a Pull Consumer
    """
    max_bytes: Optional[int] = 0
    """
    The maximum bytes value that maybe set when dong a pull on a Pull Consumer
    """
    inactive_threshold: Optional[int] = 0
    """
    Duration that instructs the server to cleanup ephemeral consumers that are inactive for that long
    """
    backoff: Optional[List[int]] = None
    """
    List of durations in Go format that represents a retry time scale for NaK'd messages
    """
    num_replicas: Optional[int] = None
    """
    When set do not inherit the replica count from the stream but specifically set it to this amount
    """
    mem_storage: Optional[bool] = False
    """
    Force the consumer state to be kept in memory rather than inherit the setting from the stream
    """
    metadata: Optional[Dict[str, str]] = None
    """
    Additional metadata for the Consumer
    """


@dataclass
class Config1513(Config156, Config157):
    ack_policy: AckPolicy
    replay_policy: ReplayPolicy
    deliver_policy: DeliverPolicy23
    durable_name: Optional[str] = None
    """
    A unique name for a durable consumer
    """
    name: Optional[str] = None
    """
    A unique name for a consumer
    """
    description: Optional[str] = None
    """
    A short description of the purpose of this consumer
    """
    deliver_subject: Optional[str] = None
    ack_wait: Optional[int] = "30000000000"
    """
    How long (in nanoseconds) to allow messages to remain un-acknowledged before attempting redelivery
    """
    max_deliver: Optional[int] = -1
    """
    The number of times a message will be redelivered to consumers if not acknowledged in time
    """
    filter_subject: Optional[str] = None
    """
    Filter the stream by a single subjects
    """
    filter_subjects: Optional[List[str]] = None
    """
    Filter the stream by multiple subjects
    """
    sample_freq: Optional[str] = None
    rate_limit_bps: Optional[int] = None
    """
    The rate at which messages will be delivered to clients, expressed in bit per second
    """
    max_ack_pending: Optional[int] = 1000
    """
    The maximum number of messages without acknowledgement that can be outstanding, once this limit is reached message delivery will be suspended
    """
    idle_heartbeat: Optional[int] = None
    """
    If the Consumer is idle for more than this many nano seconds a empty message with Status header 100 will be sent indicating the consumer is still alive
    """
    flow_control: Optional[bool] = None
    """
    For push consumers this will regularly send an empty mess with Status header 100 and a reply subject, consumers must reply to these messages to control the rate of message delivery
    """
    max_waiting: Optional[int] = 512
    """
    The number of pulls that can be outstanding on a pull consumer, pulls received after this is reached are ignored
    """
    direct: Optional[bool] = False
    """
    Creates a special consumer that does not touch the Raft layers, not for general use by clients, internal use only
    """
    headers_only: Optional[bool] = False
    """
    Delivers only the headers of messages in the stream and not the bodies. Additionally adds Nats-Msg-Size header to indicate the size of the removed payload
    """
    max_batch: Optional[int] = 0
    """
    The largest batch property that may be specified when doing a pull on a Pull Consumer
    """
    max_expires: Optional[int] = 0
    """
    The maximum expires value that may be set when doing a pull on a Pull Consumer
    """
    max_bytes: Optional[int] = 0
    """
    The maximum bytes value that maybe set when dong a pull on a Pull Consumer
    """
    inactive_threshold: Optional[int] = 0
    """
    Duration that instructs the server to cleanup ephemeral consumers that are inactive for that long
    """
    backoff: Optional[List[int]] = None
    """
    List of durations in Go format that represents a retry time scale for NaK'd messages
    """
    num_replicas: Optional[int] = None
    """
    When set do not inherit the replica count from the stream but specifically set it to this amount
    """
    mem_storage: Optional[bool] = False
    """
    Force the consumer state to be kept in memory rather than inherit the setting from the stream
    """
    metadata: Optional[Dict[str, str]] = None
    """
    Additional metadata for the Consumer
    """


Config = Union[Config158, Config159, Config1510, Config1511, Config1512, Config1513]


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


@dataclass
class IoNatsJetstreamApiV1ConsumerInfoResponse1:
    """
    A response from the JetStream $JS.API.CONSUMER.INFO API
    """

    type: str
    stream_name: str
    """
    The Stream the consumer belongs to
    """
    name: str
    """
    A unique name for the consumer, either machine generated or the durable name
    """
    config: Config
    created: str
    """
    The time the Consumer was created
    """
    delivered: Delivered
    """
    The last message delivered from this Consumer
    """
    ack_floor: AckFloor
    """
    The highest contiguous acknowledged message
    """
    num_ack_pending: int
    """
    The number of messages pending acknowledgement
    """
    num_redelivered: int
    """
    The number of redeliveries that have been performed
    """
    num_waiting: int
    """
    The number of pull consumers waiting for messages
    """
    num_pending: int
    """
    The number of messages left unconsumed in this Consumer
    """
    ts: Optional[str] = None
    """
    The server time the consumer info was created
    """
    cluster: Optional[Cluster] = None
    push_bound: Optional[bool] = None
    """
    Indicates if any client is connected and receiving messages from a push consumer
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
class IoNatsJetstreamApiV1ConsumerInfoResponse2:
    """
    A response from the JetStream $JS.API.CONSUMER.INFO API
    """

    type: str
    error: Error


IoNatsJetstreamApiV1ConsumerInfoResponse = Union[
    IoNatsJetstreamApiV1ConsumerInfoResponse1, IoNatsJetstreamApiV1ConsumerInfoResponse2
]
