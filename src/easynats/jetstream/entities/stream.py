from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from pydantic import TypeAdapter

if TYPE_CHECKING:
    from ..api import JetStreamClient, StreamMessage

from ..models.api.common._parser import parse_utc_rfc3339
from ..models.api.common.consumer_configuration import (
    AckPolicy,
    DeliverPolicy,
    ReplayPolicy,
)
from ..models.api.common.stream_configuration import (
    Compression,
    Discard,
    Placement,
    Republish,
    Retention,
    Source,
    StreamConfig,
    SubjectTransform,
)
from ..models.api.common.stream_info import StreamInfo
from ..models.api.common.stream_state import StreamState
from ..models.api.pub_ack_response import PubAckResponse
from ..models.api.stream_create import StreamCreateResponse
from ..models.api.stream_info import StreamInfoResponse
from ..models.api.stream_update import StreamUpdateResponse
from .consumer import (
    Consumer,
    ConsumerConfig,
    DurablePullConsumer,
    DurablePushConsumer,
    EphemeralPullConsumer,
    EphemeralPushConsumer,
)


@dataclass
class StreamMeta:
    """StreamMeta holds both the configuration and the state of a stream."""

    config: StreamConfig
    """The stream configuration."""
    state: StreamState
    """The stream state."""

    def to_dict(self) -> dict[str, Any]:
        """Encode stream meta to a python dictionary.

        This is useful for serialization to other formats than JSON.
        For JSON serialization, prefer the `to_json()` method.

        Returns:
            The encoded stream meta as a python dictionary.
        """
        return _StreamMetaAdapter.dump_python(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StreamMeta:
        """Decode stream meta from a python dictionary.

        This is useful for deserialization from JSON or other formats.
        For JSON deserialization, prefer the `from_json()` method.

        Args:
            data: The encoded stream meta as a dictionary.

        Returns:
            The decoded stream meta.
        """
        return _StreamMetaAdapter.validate_python(data)

    def to_json(self) -> bytes:
        """Encode stream meta to JSON.

        Returns:
            The encoded stream meta as JSON bytes.
        """
        return _StreamMetaAdapter.dump_json(self)

    @classmethod
    def from_json(cls, data: str | bytes) -> StreamMeta:
        """Decode stream meta from JSON bytes or string.

        Args:
            data: The encoded stream meta as JSON bytes or string.

        Returns:
            The decoded stream meta.
        """
        return _StreamMetaAdapter.validate_json(data)


_StreamMetaAdapter = TypeAdapter(StreamMeta)


class Stream:
    """A python object representing a JetStream stream.

    This object is a wrapper around the JetStreamClient and the stream configuration.
    It provides a convenient interface to interact with the stream.
    """

    def __init__(
        self,
        client: JetStreamClient,
        stream_name: str,
        stream_config: StreamConfig,
        created_timestamp: datetime.datetime,
    ) -> None:
        """Create a new stream object. Note that it DOES NOT create the stream
        on the server, instead, it represents an existing stream.

        Args:
            client: The JetStreamClient used to interact with the stream.
            stream_name: The name of the stream.
            stream_config: The configuration of the stream.
            created_timestamp: The timestamp when the stream was created.
        """
        self.client = client
        self.name = stream_name
        self.config = stream_config
        self.created = created_timestamp

    @classmethod
    def from_stream_info(
        cls,
        client: JetStreamClient,
        stream_info: StreamInfo
        | StreamInfoResponse
        | StreamCreateResponse
        | StreamUpdateResponse,
    ) -> Stream:
        """Create a new stream object from a stream info object, or from
        a response object containing stream info.

        Args:
            client: The JetStreamClient used to interact with the stream.
            stream_info: The stream info object.

        Returns:
            The new stream object.
        """
        if not stream_info.config.name:
            raise ValueError("Stream name is required")
        return cls(
            client=client,
            stream_name=stream_info.config.name,
            stream_config=stream_info.config,
            created_timestamp=parse_utc_rfc3339(stream_info.created),
        )

    async def state(self) -> StreamState:
        """Get the state of the stream.

        Returns:
            The state of the stream. This object contains data which expires quickly,
            so it should be used immediately after fetching it.
        """
        stream_info_response = await self.client.get_stream_info(stream_name=self.name)
        return stream_info_response.state

    async def update(  # noqa: C901
        self,
        subjects: list[str] | None = None,
        retention: Retention | None = None,
        max_msgs: int | None = None,
        max_bytes: int | None = None,
        max_age: int | None = None,
        num_replicas: int | None = None,
        duplicate_window: int | None = None,
        description: str | None = None,
        subject_transform: SubjectTransform | None = None,
        max_msgs_per_subject: int | None = None,
        max_msg_size: int | None = None,
        compression: Compression | None = None,
        first_seq: int | None = None,
        no_ack: bool | None = None,
        discard: Discard | None = None,
        placement: Placement | None = None,
        sources: list[Source] | None = None,
        sealed: bool | None = None,
        deny_delete: bool | None = None,
        deny_purge: bool | None = None,
        allow_rollup_hdrs: bool | None = None,
        allow_direct: bool | None = None,
        mirror_direct: bool | None = None,
        republish: Republish | None = None,
        discard_new_per_subject: bool | None = None,
        metadata: dict[str, str] | None = None,
    ) -> Stream:
        """Update the stream configuration.

        All arguments are optional, and ignored when `None`.

        Args:
            subjects: The list of subjects to consume from.
            retention: The retention policy.
            max_msgs: The maximum number of messages to retain.
            max_bytes: The maximum number of bytes to retain.
            max_age: The maximum age of messages to retain.
            num_replicas: The number of replicas.
            duplicate_window: The duplicate window.
            description: The description.
            subject_transform: The subject transform.
            max_msgs_per_subject: The maximum number of messages to retain per subject.
            max_msg_size: The maximum message size.
            compression: The compression.
            first_seq: The first sequence number.
            no_ack: Whether to disable acknowledgements.
            discard: The discard policy.
            placement: The placement.
            sources: The list of sources.
            sealed: Whether to seal the stream.
            deny_delete: Whether to deny stream deletion.
            deny_purge: Whether to deny stream purging.
            allow_rollup_hdrs: Whether to allow purge using rollup headers.
            allow_direct: Whether to allow direct access.
            mirror_direct: Whether to mirror direct access.
            republish: The republish policy.
            discard_new_per_subject: Whether to discard new per subject.
            metadata: The metadata.

        Returns:
            The updated stream object.
        """
        if subjects is not None:
            self.config.subjects = subjects
        if retention:
            self.config.retention = retention
        if max_msgs is not None:
            self.config.max_msgs = max_msgs
        if max_bytes is not None:
            self.config.max_bytes = max_bytes
        if max_age is not None:
            self.config.max_age = max_age
        if num_replicas is not None:
            self.config.num_replicas = num_replicas
        if duplicate_window is not None:
            self.config.duplicate_window = duplicate_window
        if description:
            self.config.description = description
        if subject_transform:
            self.config.subject_transform = subject_transform
        if max_msgs_per_subject is not None:
            self.config.max_msgs_per_subject = max_msgs_per_subject
        if max_msg_size is not None:
            self.config.max_msg_size = max_msg_size
        if compression:
            self.config.compression = compression
        if first_seq is not None:
            self.config.first_seq = first_seq
        if no_ack is not None:
            self.config.no_ack = no_ack
        if discard:
            self.config.discard = discard
        if placement:
            self.config.placement = placement
        if sources:
            self.config.sources = sources
        if sealed is not None:
            self.config.sealed = sealed
        if deny_delete is not None:
            self.config.deny_delete = deny_delete
        if deny_purge is not None:
            self.config.deny_purge = deny_purge
        if allow_rollup_hdrs is not None:
            self.config.allow_rollup_hdrs = allow_rollup_hdrs
        if allow_direct is not None:
            self.config.allow_direct = allow_direct
        if mirror_direct is not None:
            self.config.mirror_direct = mirror_direct
        if republish:
            self.config.republish = republish
        if discard_new_per_subject is not None:
            self.config.discard_new_per_subject = discard_new_per_subject
        if metadata:
            self.config.metadata = metadata
        stream_info_response = await self.client.update_stream(self.config)
        return Stream.from_stream_info(
            client=self.client, stream_info=stream_info_response
        )

    async def purge(
        self,
        subject: str | None = None,
        until_sequence: int | None = None,
        keep: int | None = None,
    ) -> None:
        """Purge messages within the stream.

        Args:
            subject: Purge messages for this subject.
            until_sequence: Purge messages up to this sequence number.
            keep: Keep this many messages.

        Returns:
            None. The messages are guaranteed to be purged when this method returns.
        """
        await self.client.purge_stream(
            stream_name=self.name,
            subject=subject,
            until_sequence=until_sequence,
            keep=keep,
        )

    async def publish(
        self,
        subject: str,
        payload: bytes | None = None,
        headers: dict[str, Any] | None = None,
        msg_id: str | None = None,
        expected_last_msg_id: str | None = None,
        expected_last_sequence: int | None = None,
        expected_last_subject_sequence: int | None = None,
        purge: Literal["sub", "all"] | None = None,
    ) -> PubAckResponse:
        """Publish a message to the stream.

        Args:
            subject: The subject to publish the message to.
            payload: The payload of the message.
            headers: The headers of the message.
            msg_id: The message ID. This is used for message deduplication and optimistic concurrency control.
            expected_last_msg_id: The expected last message ID. This is used for optimistic concurrency control.
            expected_last_sequence: The expected last sequence number. This is used for optimistic concurrency control.
            expected_last_subject_sequence: The expected last sequence number for the subject. This is used for optimistic concurrency control.
            purge: Purge messages from the stream before publishing. The stream must be configured to allow purging with headers.

        Returns:
            The publish acknowledgement response. It contains the sequence number of the published message.
        """
        return await self.client.publish(
            subject=subject,
            payload=payload,
            headers=headers,
            msg_id=msg_id,
            expected_stream=self.name,
            expected_last_msg_id=expected_last_msg_id,
            expected_last_sequence=expected_last_sequence,
            expected_last_subject_sequence=expected_last_subject_sequence,
            purge=purge,
        )

    async def get_msg(
        self,
        sequence: int | None = None,
        last_by_subject: str | None = None,
        next_by_subject: str | None = None,
    ) -> StreamMessage:
        """Get the specified message from the stream.

        If the stream is configured to allow direct access, the message will be fetched
        using the DIRECT api, otherwise it will be fetched using the regular api.

        Args:
            sequence: get the message with this sequence number
            last_by_subject: get the last message for this subject
            next_by_subject: get the next message for this subject wit sequence greater than `seq`

        Returns:
            The stream message.
        """
        # Request validation
        if next_by_subject:
            if not sequence:
                raise ValueError("sequence must be set when next_by_subject is set")
            if last_by_subject:
                raise ValueError(
                    "last_by_subject must not be set when next_by_subject is set"
                )
        elif last_by_subject:
            if sequence:
                raise ValueError("sequence must not be set when last_by_subject is set")
        elif sequence is None:
            last_by_subject = ">"
        # Direct bytes API
        if self.config.allow_direct:
            # Last by subject shortcut
            if sequence is None and last_by_subject:
                return await self.client.direct_get_last_stream_msg_for_subject(
                    stream_name=self.name,
                    subject=last_by_subject,
                )
            # Regular direct api
            return await self.client.direct_get_stream_msg(
                stream_name=self.name,
                sequence=sequence,
                last_by_subject=last_by_subject,
                next_by_subject=next_by_subject,
            )
        # Regular JSON (base64-encoded) API
        return await self.client.get_stream_msg(
            stream_name=self.name,
            sequence=sequence,
            last_by_subject=last_by_subject,
            next_by_subject=next_by_subject,
        )

    async def delete_msg(
        self,
        sequence: int,
        no_erase: bool = False,
    ) -> None:
        """Delete the specified message from the stream.

        Args:
            sequence: delete the message with this sequence number
            no_erase: if True, the message will be marked as deleted but not erased

        Returns:
            None. The message is guaranteed to be deleted when this method returns.
        """
        await self.client.delete_stream_msg(
            stream_name=self.name,
            sequence=sequence,
            no_erase=no_erase,
        )

    async def list_consumers(
        self,
        offset: int = 0,
    ) -> list[Consumer]:
        """List the names of all consumers on this stream.

        Args:
            offset: The offset to start from.

        Returns:
            The list of consumer.
        """
        response = await self.client.list_consumers(
            stream_name=self.name,
            offset=offset,
        )
        return [
            Consumer.from_consumer_info(self.client, info)
            for info in response.consumers
        ]

    async def list_consumer_names(
        self,
        offset: int = 0,
    ) -> list[str]:
        """List the names of all consumers on this stream.

        Args:
            offset: The offset to start from.

        Returns:
            The list of consumer names.
        """
        response = await self.client.list_consumers(
            stream_name=self.name,
            offset=offset,
        )
        return [info.name for info in response.consumers]

    async def get_consumer(self, consumer_name: str) -> Consumer:
        consumer_info = await self.client.get_consumer_info(
            stream_name=self.name, consumer_name=consumer_name
        )
        return Consumer.from_consumer_info(self.client, consumer_info)

    async def create_ephemeral_consumer_from_config(
        self,
        config: ConsumerConfig,
    ) -> EphemeralPushConsumer | EphemeralPullConsumer:
        """Create an ephemeral consumer on this stream.

        Args:
            config: The consumer configuration.

        Returns:
            The new consumer.
        """
        if config.durable_name:
            raise ValueError("config.durable_name must not be set")
        if config.num_replicas is None:
            if not self.config.num_replicas:
                config.num_replicas = 0
            else:
                config.num_replicas = self.config.num_replicas
        response = await self.client.create_ephemeral_consumer(
            stream_name=self.name,
            consumer_config=config,
        )
        return Consumer.from_consumer_info(self.client, response)  # type: ignore

    async def create_durable_consumer_from_config(
        self,
        config: ConsumerConfig,
    ) -> DurablePullConsumer | DurablePushConsumer:
        """Create a durable consumer on this stream.

        Args:
            config: The consumer configuration.

        Returns:
            The new consumer.
        """
        if not config.durable_name:
            raise ValueError("durable_name is required")
        if config.name and config.name != config.durable_name:
            raise ValueError(
                "config.name must not be set or must be equal to durable_name"
            )
        if not config.name:
            config.name = config.durable_name
        if config.num_replicas is None:
            if not self.config.num_replicas:
                config.num_replicas = 0
            else:
                config.num_replicas = self.config.num_replicas
        # Prefer the filtered API when possible as it allows ACLs to be applied
        # to the consumer subject
        if config.filter_subjects is None and config.filter_subject:
            response = await self.client.create_filtered_durable_consumer(
                stream_name=self.name,
                consumer_config=config,
            )
        else:
            response = await self.client.create_durable_consumer(
                stream_name=self.name,
                consumer_config=config,
            )
        return Consumer.from_consumer_info(self.client, response)  # type: ignore

    async def create_durable_pull_consumer(
        self,
        name: str,
        description: str | None = None,
        ack_policy: AckPolicy | None = None,
        replay_policy: ReplayPolicy | None = None,
        deliver_policy: DeliverPolicy | None = None,
        opt_start_seq: int | None = None,
        opt_start_time: datetime.datetime | None = None,
        ack_wait: int | None = None,
        max_deliver: int | None = None,
        filter_subjects: str | list[str] | None = None,
        sample_freq: datetime.timedelta | None = None,
        max_ack_pending: int | None = None,
        max_waiting: int | None = None,
        headers_only: bool | None = None,
        max_batch: int | None = None,
        max_expires: datetime.timedelta | None = None,
        max_bytes: int | None = None,
        inactive_threshold: datetime.timedelta | None = None,
        backoff: list[int] | None = None,
        num_replicas: int | None = None,
        mem_storage: bool | None = None,
        metadata: dict[str, str] | None = None,
    ) -> DurablePullConsumer:
        consumer_config = ConsumerConfig.new_durable_pull_config(
            name=name,
            description=description,
            ack_policy=ack_policy,
            replay_policy=replay_policy,
            deliver_policy=deliver_policy,
            opt_start_seq=opt_start_seq,
            opt_start_time=opt_start_time,
            ack_wait=ack_wait,
            max_deliver=max_deliver,
            filter_subjects=filter_subjects,
            sample_freq=sample_freq,
            max_ack_pending=max_ack_pending,
            max_waiting=max_waiting,
            headers_only=headers_only,
            max_batch=max_batch,
            max_expires=max_expires,
            max_bytes=max_bytes,
            inactive_threshold=inactive_threshold,
            backoff=backoff,
            num_replicas=num_replicas,
            mem_storage=mem_storage,
            metadata=metadata,
        )
        return await self.create_durable_consumer_from_config(consumer_config)  # type: ignore

    async def create_ephemeral_pull_consumer(
        self,
        description: str | None = None,
        ack_policy: AckPolicy | None = None,
        replay_policy: ReplayPolicy | None = None,
        deliver_policy: DeliverPolicy | None = None,
        opt_start_seq: int | None = None,
        opt_start_time: datetime.datetime | None = None,
        ack_wait: int | None = None,
        max_deliver: int | None = None,
        filter_subjects: str | list[str] | None = None,
        sample_freq: datetime.timedelta | None = None,
        max_ack_pending: int | None = None,
        max_waiting: int | None = None,
        headers_only: bool | None = None,
        max_batch: int | None = None,
        max_expires: datetime.timedelta | None = None,
        max_bytes: int | None = None,
        inactive_threshold: datetime.timedelta | None = None,
        backoff: list[int] | None = None,
        num_replicas: int | None = None,
        mem_storage: bool | None = None,
        metadata: dict[str, str] | None = None,
    ) -> EphemeralPullConsumer:
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(
            description=description,
            ack_policy=ack_policy,
            replay_policy=replay_policy,
            deliver_policy=deliver_policy,
            opt_start_seq=opt_start_seq,
            opt_start_time=opt_start_time,
            ack_wait=ack_wait,
            max_deliver=max_deliver,
            filter_subjects=filter_subjects,
            sample_freq=sample_freq,
            max_ack_pending=max_ack_pending,
            max_waiting=max_waiting,
            headers_only=headers_only,
            max_batch=max_batch,
            max_expires=max_expires,
            max_bytes=max_bytes,
            inactive_threshold=inactive_threshold,
            backoff=backoff,
            num_replicas=num_replicas,
            mem_storage=mem_storage,
            metadata=metadata,
        )
        return await self.create_ephemeral_consumer_from_config(consumer_config)  # type: ignore

    async def create_durable_push_consumer(
        self,
        name: str,
        deliver_subject: str,
        description: str | None = None,
        ack_policy: AckPolicy | None = None,
        replay_policy: ReplayPolicy | None = None,
        deliver_policy: DeliverPolicy | None = None,
        opt_start_seq: int | None = None,
        opt_start_time: datetime.datetime | None = None,
        ack_wait: int | None = None,
        max_deliver: int | None = None,
        filter_subjects: str | list[str] | None = None,
        sample_freq: datetime.timedelta | None = None,
        rate_limit_bps: int | None = None,
        max_ack_pending: int | None = None,
        flow_control: bool | None = None,
        headers_only: bool | None = None,
        idle_heartbeat: datetime.timedelta | None = None,
        inactive_threshold: datetime.timedelta | None = None,
        backoff: list[int] | None = None,
        num_replicas: int | None = None,
        mem_storage: bool | None = None,
        metadata: dict[str, str] | None = None,
    ) -> DurablePushConsumer:
        consumer_config = ConsumerConfig.new_durable_push_config(
            name=name,
            deliver_subject=deliver_subject,
            description=description,
            ack_policy=ack_policy,
            replay_policy=replay_policy,
            deliver_policy=deliver_policy,
            opt_start_seq=opt_start_seq,
            opt_start_time=opt_start_time,
            ack_wait=ack_wait,
            max_deliver=max_deliver,
            filter_subjects=filter_subjects,
            sample_freq=sample_freq,
            rate_limit_bps=rate_limit_bps,
            max_ack_pending=max_ack_pending,
            flow_control=flow_control,
            headers_only=headers_only,
            idle_heartbeat=idle_heartbeat,
            inactive_threshold=inactive_threshold,
            backoff=backoff,
            num_replicas=num_replicas,
            mem_storage=mem_storage,
            metadata=metadata,
        )
        return await self.create_durable_consumer_from_config(consumer_config)  # type: ignore

    async def create_ephemeral_push_consumer(
        self,
        deliver_subject: str | None = None,
        description: str | None = None,
        ack_policy: AckPolicy | None = None,
        replay_policy: ReplayPolicy | None = None,
        deliver_policy: DeliverPolicy | None = None,
        opt_start_seq: int | None = None,
        opt_start_time: datetime.datetime | None = None,
        ack_wait: int | None = None,
        max_deliver: int | None = None,
        filter_subjects: str | list[str] | None = None,
        sample_freq: datetime.timedelta | None = None,
        rate_limit_bps: int | None = None,
        max_ack_pending: int | None = None,
        flow_control: bool | None = None,
        headers_only: bool | None = None,
        idle_heartbeat: datetime.timedelta | None = None,
        inactive_threshold: datetime.timedelta | None = None,
        direct: bool | None = None,
        backoff: list[int] | None = None,
        num_replicas: int | None = None,
        mem_storage: bool | None = None,
        metadata: dict[str, str] | None = None,
    ) -> EphemeralPushConsumer:
        if not deliver_subject:
            deliver_subject = self.client.typed.connection.client.new_inbox()
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            deliver_subject=deliver_subject,
            description=description,
            ack_policy=ack_policy,
            replay_policy=replay_policy,
            deliver_policy=deliver_policy,
            opt_start_seq=opt_start_seq,
            opt_start_time=opt_start_time,
            ack_wait=ack_wait,
            max_deliver=max_deliver,
            filter_subjects=filter_subjects,
            sample_freq=sample_freq,
            rate_limit_bps=rate_limit_bps,
            max_ack_pending=max_ack_pending,
            flow_control=flow_control,
            headers_only=headers_only,
            idle_heartbeat=idle_heartbeat,
            inactive_threshold=inactive_threshold,
            direct=direct,
            backoff=backoff,
            num_replicas=num_replicas,
            mem_storage=mem_storage,
            metadata=metadata,
        )
        return await self.create_ephemeral_consumer_from_config(consumer_config)  # type: ignore
