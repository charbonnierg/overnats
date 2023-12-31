# @generated

import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union

from ._parser import encode_nanoseconds_timedelta, encode_utc_rfc3339
from .stream_configuration import get_or


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
    opt_start_seq: Optional[int] = None
    """Only valid for DeliverPolicy.by_start_sequence. The sequence number from which to start receiving messages."""
    opt_start_time: Optional[str] = None
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

    @classmethod
    def new_ephemeral_pull_config(
        cls,
        description: Optional[str] = None,
        ack_policy: Optional[AckPolicy] = None,
        replay_policy: Optional[ReplayPolicy] = None,
        deliver_policy: Optional[DeliverPolicy] = None,
        opt_start_seq: Optional[int] = None,
        opt_start_time: Optional[datetime.datetime] = None,
        ack_wait: Optional[int] = None,
        max_deliver: Optional[int] = None,
        filter_subjects: Union[str, List[str], None] = None,
        sample_freq: Optional[datetime.timedelta] = None,
        max_ack_pending: Optional[int] = None,
        max_waiting: Optional[int] = None,
        direct: Optional[bool] = None,
        headers_only: Optional[bool] = None,
        max_batch: Optional[int] = None,
        max_expires: Optional[datetime.timedelta] = None,
        max_bytes: Optional[int] = None,
        inactive_threshold: Optional[datetime.timedelta] = None,
        backoff: Optional[List[int]] = None,
        num_replicas: Optional[int] = None,
        mem_storage: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> "ConsumerConfig":
        if opt_start_seq:
            if deliver_policy is None:
                deliver_policy = DeliverPolicy.by_start_sequence
            elif deliver_policy != DeliverPolicy.by_start_sequence:
                raise ValueError(
                    "deliver_policy must be DeliverPolicy.by_start_sequence"
                )
        if opt_start_time:
            if deliver_policy is None:
                deliver_policy = DeliverPolicy.by_start_time
            elif deliver_policy != DeliverPolicy.by_start_time:
                raise ValueError("deliver_policy must be DeliverPolicy.by_start_time")
        filter_subject: Optional[str] = None
        if isinstance(filter_subjects, str):
            filter_subject = filter_subjects
            filter_subjects = None
        elif filter_subjects is not None:
            if len(filter_subjects) == 0:
                filter_subjects = None
            elif len(filter_subjects) == 1:
                filter_subject = filter_subjects[0]
                filter_subjects = None
        if backoff:
            if ack_wait:
                if ack_wait != backoff[0]:
                    raise ValueError(
                        "ack_wait must be the same as the first element of backoff"
                    )
            else:
                ack_wait = backoff[0]
            if max_deliver is None:
                max_deliver = len(backoff) + 1
            elif max_deliver <= len(backoff):
                raise ValueError(
                    "max_deliver must be greater than the length of backoff"
                )
        start = encode_utc_rfc3339(opt_start_time) if opt_start_time else None
        sample_frequency = (
            str(encode_nanoseconds_timedelta(sample_freq)) if sample_freq else None
        )
        max_expires_int = (
            encode_nanoseconds_timedelta(max_expires) if max_expires else 0
        )
        inactive_threshold_int = (
            encode_nanoseconds_timedelta(inactive_threshold)
            if inactive_threshold
            else 5000000000
        )
        return cls(
            description=description,
            ack_policy=get_or(ack_policy, AckPolicy.explicit),
            replay_policy=get_or(replay_policy, ReplayPolicy.instant),
            deliver_policy=get_or(deliver_policy, DeliverPolicy.all),
            opt_start_seq=opt_start_seq,
            opt_start_time=start,
            ack_wait=get_or(ack_wait, 30000000000),
            max_deliver=get_or(max_deliver, -1),
            filter_subject=filter_subject,
            filter_subjects=filter_subjects,
            sample_freq=sample_frequency,
            max_ack_pending=get_or(max_ack_pending, 1000),
            max_waiting=get_or(max_waiting, 512),
            direct=get_or(direct, False),
            headers_only=get_or(headers_only, False),
            max_batch=get_or(max_batch, 0),
            max_expires=max_expires_int,
            max_bytes=get_or(max_bytes, 0),
            inactive_threshold=inactive_threshold_int,
            backoff=backoff,
            num_replicas=num_replicas,
            mem_storage=get_or(mem_storage, False),
            metadata=metadata,
        )

    @classmethod
    def new_durable_pull_config(
        cls,
        name: str,
        description: Optional[str] = None,
        ack_policy: Optional[AckPolicy] = None,
        replay_policy: Optional[ReplayPolicy] = None,
        deliver_policy: Optional[DeliverPolicy] = None,
        opt_start_seq: Optional[int] = None,
        opt_start_time: Optional[datetime.datetime] = None,
        ack_wait: Optional[int] = None,
        max_deliver: Optional[int] = None,
        filter_subjects: Union[str, List[str], None] = None,
        sample_freq: Optional[datetime.timedelta] = None,
        max_ack_pending: Optional[int] = None,
        max_waiting: Optional[int] = None,
        headers_only: Optional[bool] = None,
        max_batch: Optional[int] = None,
        max_expires: Optional[datetime.timedelta] = None,
        max_bytes: Optional[int] = None,
        inactive_threshold: Optional[datetime.timedelta] = None,
        backoff: Optional[List[int]] = None,
        num_replicas: Optional[int] = None,
        mem_storage: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> "ConsumerConfig":
        if opt_start_seq:
            if deliver_policy is None:
                deliver_policy = DeliverPolicy.by_start_sequence
            elif deliver_policy != DeliverPolicy.by_start_sequence:
                raise ValueError(
                    "deliver_policy must be DeliverPolicy.by_start_sequence"
                )
        if opt_start_time:
            if deliver_policy is None:
                deliver_policy = DeliverPolicy.by_start_time
            elif deliver_policy != DeliverPolicy.by_start_time:
                raise ValueError("deliver_policy must be DeliverPolicy.by_start_time")
        filter_subject: Optional[str] = None
        if isinstance(filter_subjects, str):
            filter_subject = filter_subjects
            filter_subjects = None
        elif filter_subjects is not None:
            if len(filter_subjects) == 0:
                filter_subjects = None
            elif len(filter_subjects) == 1:
                filter_subject = filter_subjects[0]
                filter_subjects = None
        if backoff:
            if ack_wait:
                if ack_wait != backoff[0]:
                    raise ValueError(
                        "ack_wait must be the same as the first element of backoff"
                    )
            else:
                ack_wait = backoff[0]
            if max_deliver is None:
                max_deliver = len(backoff) + 1
            elif max_deliver <= len(backoff):
                raise ValueError(
                    "max_deliver must be greater than the length of backoff"
                )
        start = encode_utc_rfc3339(opt_start_time) if opt_start_time else None
        sample_frequency = (
            str(int(sample_freq.total_seconds() * 1e9)) if sample_freq else None
        )
        max_expires_int = int(max_expires.total_seconds() * 1e9) if max_expires else 0
        inactive_threshold_int = (
            int(inactive_threshold.total_seconds() * 1e9) if inactive_threshold else 0
        )
        return cls(
            name=name,
            durable_name=name,
            description=description,
            ack_policy=get_or(ack_policy, AckPolicy.explicit),
            replay_policy=get_or(replay_policy, ReplayPolicy.instant),
            deliver_policy=get_or(deliver_policy, DeliverPolicy.all),
            opt_start_seq=opt_start_seq,
            opt_start_time=start,
            ack_wait=get_or(ack_wait, 30000000000),
            max_deliver=get_or(max_deliver, -1),
            filter_subject=filter_subject,
            filter_subjects=filter_subjects,
            sample_freq=sample_frequency,
            max_ack_pending=get_or(max_ack_pending, 1000),
            max_waiting=get_or(max_waiting, 512),
            headers_only=get_or(headers_only, False),
            max_batch=get_or(max_batch, 0),
            max_expires=max_expires_int,
            max_bytes=get_or(max_bytes, 0),
            inactive_threshold=inactive_threshold_int,
            backoff=backoff,
            num_replicas=num_replicas,
            mem_storage=get_or(mem_storage, False),
            metadata=metadata,
        )

    @classmethod
    def new_ephemeral_push_config(  # noqa: C901
        cls,
        deliver_subject: str,
        description: Optional[str] = None,
        ack_policy: Optional[AckPolicy] = None,
        replay_policy: Optional[ReplayPolicy] = None,
        deliver_policy: Optional[DeliverPolicy] = None,
        opt_start_seq: Optional[int] = None,
        opt_start_time: Optional[datetime.datetime] = None,
        ack_wait: Optional[int] = None,
        max_deliver: Optional[int] = None,
        filter_subjects: Union[str, List[str], None] = None,
        sample_freq: Optional[datetime.timedelta] = None,
        rate_limit_bps: Optional[int] = None,
        max_ack_pending: Optional[int] = None,
        idle_heartbeat: Optional[datetime.timedelta] = None,
        flow_control: Optional[bool] = None,
        direct: Optional[bool] = None,
        headers_only: Optional[bool] = None,
        inactive_threshold: Optional[datetime.timedelta] = None,
        backoff: Optional[List[int]] = None,
        num_replicas: Optional[int] = None,
        mem_storage: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> "ConsumerConfig":
        if ack_policy == AckPolicy.none and max_ack_pending is not None:
            raise ValueError(
                "max_ack_pending must be None when ack_policy is AckPolicy.none"
            )
        if opt_start_seq:
            if deliver_policy is None:
                deliver_policy = DeliverPolicy.by_start_sequence
            elif deliver_policy != DeliverPolicy.by_start_sequence:
                raise ValueError(
                    "deliver_policy must be DeliverPolicy.by_start_sequence"
                )
        if opt_start_time:
            if deliver_policy is None:
                deliver_policy = DeliverPolicy.by_start_time
            elif deliver_policy != DeliverPolicy.by_start_time:
                raise ValueError("deliver_policy must be DeliverPolicy.by_start_time")
        filter_subject: Optional[str] = None
        if isinstance(filter_subjects, str):
            filter_subject = filter_subjects
            filter_subjects = None
        elif filter_subjects is not None:
            if len(filter_subjects) == 0:
                filter_subjects = None
            elif len(filter_subjects) == 1:
                filter_subject = filter_subjects[0]
                filter_subjects = None
        if backoff:
            if ack_wait:
                if ack_wait != backoff[0]:
                    raise ValueError(
                        "ack_wait must be the same as the first element of backoff"
                    )
            else:
                ack_wait = backoff[0]
            if max_deliver is None:
                max_deliver = len(backoff) + 1
            elif max_deliver <= len(backoff):
                raise ValueError(
                    "max_deliver must be greater than the length of backoff"
                )
        if flow_control:
            if idle_heartbeat is None:
                idle_heartbeat = datetime.timedelta(seconds=30)
        start = encode_utc_rfc3339(opt_start_time) if opt_start_time else None
        sample_frequency = (
            str(encode_nanoseconds_timedelta(sample_freq)) if sample_freq else None
        )
        heartbeat_frequency = (
            encode_nanoseconds_timedelta(idle_heartbeat) if idle_heartbeat else None
        )
        inactive_threshold_int = (
            encode_nanoseconds_timedelta(inactive_threshold)
            if inactive_threshold
            else 5000000000
        )
        return cls(
            description=description,
            deliver_subject=deliver_subject,
            ack_policy=get_or(ack_policy, AckPolicy.explicit),
            replay_policy=get_or(replay_policy, ReplayPolicy.instant),
            deliver_policy=get_or(deliver_policy, DeliverPolicy.all),
            opt_start_seq=opt_start_seq,
            opt_start_time=start,
            ack_wait=get_or(ack_wait, 30000000000),
            max_deliver=get_or(max_deliver, -1),
            filter_subject=filter_subject,
            filter_subjects=filter_subjects,
            sample_freq=sample_frequency,
            rate_limit_bps=rate_limit_bps,
            max_ack_pending=get_or(max_ack_pending, 1000)
            if ack_policy != AckPolicy.none
            else None,
            idle_heartbeat=heartbeat_frequency,
            flow_control=flow_control,
            direct=get_or(direct, False),
            headers_only=get_or(headers_only, False),
            inactive_threshold=inactive_threshold_int,
            backoff=backoff,
            num_replicas=num_replicas,
            mem_storage=get_or(mem_storage, False),
            metadata=metadata,
            # Must be set to None for push consumers
            max_waiting=None,
        )

    @classmethod
    def new_durable_push_config(  # noqa: C901
        cls,
        name: str,
        deliver_subject: str,
        description: Optional[str] = None,
        ack_policy: Optional[AckPolicy] = None,
        replay_policy: Optional[ReplayPolicy] = None,
        deliver_policy: Optional[DeliverPolicy] = None,
        opt_start_seq: Optional[int] = None,
        opt_start_time: Optional[datetime.datetime] = None,
        ack_wait: Optional[int] = None,
        max_deliver: Optional[int] = None,
        filter_subjects: Union[str, List[str], None] = None,
        sample_freq: Optional[datetime.timedelta] = None,
        rate_limit_bps: Optional[int] = None,
        max_ack_pending: Optional[int] = None,
        flow_control: Optional[bool] = None,
        headers_only: Optional[bool] = None,
        idle_heartbeat: Optional[datetime.timedelta] = None,
        inactive_threshold: Optional[datetime.timedelta] = None,
        backoff: Optional[List[int]] = None,
        num_replicas: Optional[int] = None,
        mem_storage: Optional[bool] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> "ConsumerConfig":
        if ack_policy == AckPolicy.none and max_ack_pending is not None:
            raise ValueError(
                "max_ack_pending must be None when ack_policy is AckPolicy.none"
            )
        if opt_start_seq:
            if deliver_policy is None:
                deliver_policy = DeliverPolicy.by_start_sequence
            elif deliver_policy != DeliverPolicy.by_start_sequence:
                raise ValueError(
                    "deliver_policy must be DeliverPolicy.by_start_sequence"
                )
        if opt_start_time:
            if deliver_policy is None:
                deliver_policy = DeliverPolicy.by_start_time
            elif deliver_policy != DeliverPolicy.by_start_time:
                raise ValueError("deliver_policy must be DeliverPolicy.by_start_time")
        filter_subject: Optional[str] = None
        if isinstance(filter_subjects, str):
            filter_subject = filter_subjects
            filter_subjects = None
        elif filter_subjects is not None:
            if len(filter_subjects) == 0:
                filter_subjects = None
            elif len(filter_subjects) == 1:
                filter_subject = filter_subjects[0]
                filter_subjects = None
        if backoff:
            if ack_wait:
                if ack_wait != backoff[0]:
                    raise ValueError(
                        "ack_wait must be the same as the first element of backoff"
                    )
            else:
                ack_wait = backoff[0]
            if max_deliver is None:
                max_deliver = len(backoff) + 1
            elif max_deliver <= len(backoff):
                raise ValueError(
                    "max_deliver must be greater than the length of backoff"
                )
        if flow_control:
            if idle_heartbeat is None:
                idle_heartbeat = datetime.timedelta(seconds=30)
        start = encode_utc_rfc3339(opt_start_time) if opt_start_time else None
        sample_frequency = (
            str(encode_nanoseconds_timedelta(sample_freq)) if sample_freq else None
        )
        heartbeat_frequency = (
            encode_nanoseconds_timedelta(idle_heartbeat) if idle_heartbeat else None
        )
        inactive_threshold_int = (
            encode_nanoseconds_timedelta(inactive_threshold)
            if inactive_threshold
            else 0
        )
        return cls(
            name=name,
            durable_name=name,
            description=description,
            ack_policy=get_or(ack_policy, AckPolicy.explicit),
            replay_policy=get_or(replay_policy, ReplayPolicy.instant),
            deliver_policy=get_or(deliver_policy, DeliverPolicy.all),
            opt_start_seq=opt_start_seq,
            opt_start_time=start,
            deliver_subject=deliver_subject,
            ack_wait=get_or(ack_wait, 30000000000),
            max_deliver=get_or(max_deliver, -1),
            filter_subject=filter_subject,
            filter_subjects=filter_subjects,
            sample_freq=sample_frequency,
            rate_limit_bps=rate_limit_bps,
            max_ack_pending=get_or(max_ack_pending, 1000)
            if ack_policy != AckPolicy.none
            else None,
            idle_heartbeat=heartbeat_frequency,
            flow_control=flow_control,
            headers_only=get_or(headers_only, False),
            inactive_threshold=inactive_threshold_int,
            backoff=backoff,
            num_replicas=num_replicas,
            mem_storage=get_or(mem_storage, False),
            metadata=metadata,
            # Must be set to None for push consumers
            max_waiting=None,
        )
