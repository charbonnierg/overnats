# @generated

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class DeliverPolicy(Enum):
    all = "all"
    last = "last"
    new = "new"
    by_start_sequence = "by_start_sequence"
    by_start_time = "by_start_time"
    last_per_subject = "last_per_subject"


class AckPolicy(Enum):
    none = "none"
    all = "all"
    explicit = "explicit"


class ReplayPolicy(Enum):
    instant = "instant"
    original = "original"


@dataclass
class ConsumerConfig:
    """
    The data structure that describe the configuration of a NATS JetStream Consumer
    """

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
    """For push consumer only. The subject to which messages should be delivered."""
    ack_policy: AckPolicy = AckPolicy.explicit
    """The acknowledgement strategy the consumer will employ."""
    replay_policy: ReplayPolicy = ReplayPolicy.instant
    """The replay policy for the consumer."""
    deliver_policy: DeliverPolicy = DeliverPolicy.all
    """The delivery policy for the consumer."""
    opt_start_seq: int | None = None
    """Only valid for DeliverPolicy.by_start_sequence. The sequence number from which to start receiving messages."""
    opt_start_time: str | None = None
    """Only valid for DeliverPolicy.by_start_time. The time from which to start receiving messages."""
    ack_wait: Optional[int] = 30000000000
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
