from __future__ import annotations

import contextlib
import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from ...api import Error, JetStreamApiClient, JetStreamAPIException, StreamMessage
from ...models.api.common._parser import parse_utc_rfc3339
from ...models.api.common.consumer_configuration import DeliverPolicy
from ...models.api.common.stream_configuration import (
    Compression,
    Discard,
    Mirror,
    Placement,
    Republish,
    Retention,
    Source,
    Storage,
    StreamConfig,
    SubjectTransform,
    get_or,
)
from ...models.api.common.stream_info import StreamInfo
from ...models.api.pub_ack_response import PubAckResponse
from ...models.api.stream_create import StreamCreateResponse
from ...models.api.stream_info import StreamInfoResponse
from ...models.api.stream_update import StreamUpdateResponse
from ..streams.consumer import EphemeralPushConsumer, PendingMessage
from ..streams.stream import Stream


class Operation(str, Enum):
    PUT = "PUT"
    DEL = "DEL"
    PURGE = "PURGE"


@dataclass
class Entry:
    key: str
    operation: Operation
    value: bytes
    sequence: int
    headers: dict[str, str]
    timestamp: datetime.datetime

    @classmethod
    def from_stream_message(cls, msg: StreamMessage) -> Entry:
        return cls(
            key=msg.subject.split(".")[-1],
            value=msg.payload,
            sequence=msg.sequence,
            headers=msg.headers,
            timestamp=msg.timestamp,
            operation=Operation(msg.headers.get("KV-Operation", "PUT")),
        )

    @classmethod
    def from_pending_message(cls, msg: PendingMessage) -> Entry:
        return cls(
            key=msg.subject().split(".")[-1],
            value=msg.data(),
            sequence=msg.stream_sequence(),
            headers=msg.headers(),
            timestamp=msg.timestamp(),
            operation=Operation(msg.headers().get("KV-Operation", "PUT")),
        )


class UpToDateSignal:
    pass


class KeyWatcher:
    def __init__(
        self,
        consumer: EphemeralPushConsumer,
        ignore_delete: bool = False,
    ) -> None:
        self.ignore_delete = ignore_delete
        self._consumer = consumer
        self._queue = self._consumer.messages()
        self._up_to_date = False
        self._delivered_up_to_date_signal = False
        self._stack = contextlib.AsyncExitStack()

    async def _start(self) -> None:
        # Check if the consumer is already up to date
        consumer_state = await self._consumer.state()
        if consumer_state.num_pending == 0 and consumer_state.num_ack_pending == 0:
            self._up_to_date = True
        await self._stack.__aenter__()
        # Always destroy the consumer when the watcher is stopped
        self._stack.push_async_callback(self._consumer.destroy)
        # Start the consumer and stop it when the watcher is stopped
        await self._stack.enter_async_context(self._queue)

    async def stop(self) -> None:
        """Stop the watcher."""
        await self._stack.aclose()

    async def next(self) -> Entry | UpToDateSignal:
        """Get the next entry from the watcher.

        Returns:
            The next entry, or an UpToDateSignal if the watcher is up to date.
        """
        while True:
            if self._up_to_date is True and not self._delivered_up_to_date_signal:
                self._delivered_up_to_date_signal = True
                return UpToDateSignal()
            msg = await self._queue.next()
            if msg.num_pending() == 0:
                self._up_to_date = True
            entry = Entry.from_pending_message(msg)
            if self.ignore_delete:
                if entry.operation == Operation.DEL:
                    continue
                if entry.operation == Operation.PURGE:
                    continue
            return entry

    async def __aenter__(self) -> KeyWatcher:
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        await self.stop()


@dataclass
class KVConfig:
    """Key value store config"""

    name: str
    """
    A unique name for the Stream, empty for Stream Templates.
    """
    ttl: int
    """
    Maximum age of any message in the stream, expressed in nanoseconds. 0 for unlimited.
    """
    history: int
    """
    For wildcard streams ensure that for every unique subject this many messages are kept - a per subject retention limit
    """
    storage: Storage
    """
    The storage backend to use for the Stream.
    """
    num_replicas: int
    """
    How many replicas to keep for each message.
    """
    max_bucket_size: Optional[int]
    """
    How big the Stream may be, when the combined stream size exceeds this old messages are removed. -1 for unlimited.
    """
    max_msg_size: Optional[int]
    """
    The largest message that will be accepted by the Stream. -1 for unlimited.
    """
    description: Optional[str]
    """
    A short description of the purpose of this stream
    """
    compression: Optional[Compression]
    """
    Optional compression algorithm used for the Stream.
    """
    placement: Optional[Placement]
    """
    Placement directives to consider when placing replicas of this stream, random placement when unset
    """
    mirror: Optional[Mirror]
    """
    Maintains a 1:1 mirror of another stream with name matching this property.  When a mirror is configured subjects and sources must be empty.
    """
    sources: Optional[List[Source]]
    """
    List of Stream names to replicate into this Stream
    """
    republish: Optional[Republish]
    """
    Rules for republishing messages from a stream with subject mapping onto new subjects for partitioning and more
    """
    subject_transform: Optional[SubjectTransform]
    """
    Rules for transforming subjects for this stream
    """
    metadata: Optional[Dict[str, str]]
    """
    Additional metadata for the Stream
    """

    def to_stream_config(self) -> StreamConfig:
        return StreamConfig.new(
            name=self.name,
            max_bytes=self.max_bucket_size,
            max_age=self.ttl,
            max_msgs_per_subject=self.history,
            storage=self.storage,
            num_replicas=self.num_replicas,
            description=self.description,
            max_msg_size=self.max_msg_size,
            compression=self.compression,
            placement=self.placement,
            mirror=self.mirror,
            sources=self.sources,
            republish=self.republish,
            metadata=self.metadata,
            subject_transform=self.subject_transform,
            sealed=False,
            deny_delete=True,
            deny_purge=False,
            allow_direct=True,
            allow_rollup_hdrs=True,
            duplicate_window=self.ttl if self.ttl <= 120_000_000_000 else 0,
            no_ack=False,
            retention=Retention.limits,
            discard=Discard.new,
        )

    @classmethod
    def from_stream_config(cls, config: StreamConfig) -> KVConfig:
        if not config.name:
            raise ValueError("config.name is required")
        if config.max_msgs_per_subject is None:
            raise ValueError("config.max_msg_per_subject is required")
        return cls(
            name=config.name,
            max_bucket_size=config.max_bytes,
            ttl=config.max_age,
            history=config.max_msgs_per_subject,
            storage=config.storage,
            num_replicas=config.num_replicas,
            description=config.description,
            max_msg_size=config.max_msg_size,
            compression=config.compression,
            placement=config.placement,
            mirror=config.mirror,
            sources=config.sources,
            republish=config.republish,
            subject_transform=config.subject_transform,
            metadata=config.metadata,
        )

    @classmethod
    def new(
        cls,
        name: str,
        max_bucket_size: int | None = None,
        ttl: int | None = None,
        history: int | None = None,
        storage: Storage | None = None,
        num_replicas: int | None = None,
        description: str | None = None,
        max_msg_size: int | None = None,
        compression: Compression | None = None,
        placement: Placement | None = None,
        mirror: Mirror | None = None,
        sources: List[Source] | None = None,
        republish: Republish | None = None,
        subject_transform: SubjectTransform | None = None,
        metadata: Dict[str, str] | None = None,
    ) -> KVConfig:
        return cls(
            name=name,
            max_bucket_size=get_or(max_bucket_size, -1),
            ttl=get_or(ttl, 0),
            history=get_or(history, 1),
            storage=get_or(storage, Storage.file),
            num_replicas=get_or(num_replicas, 1),
            description=description,
            max_msg_size=get_or(max_msg_size, -1),
            compression=get_or(compression, Compression.none),
            placement=placement,
            mirror=mirror,
            sources=sources,
            republish=republish,
            subject_transform=subject_transform,
            metadata=metadata,
        )


class KV:
    def __init__(
        self,
        client: JetStreamApiClient,
        stream_name: str,
        bucket_name: str,
        kv_config: StreamConfig,
        created_timestamp: datetime.datetime,
    ) -> None:
        self.stream_name = stream_name
        self.bucket_name = bucket_name
        self.client = client
        self.config = kv_config
        self.created_timestamp = created_timestamp
        self._stream: Stream | None = None

    @classmethod
    def from_stream(cls, client: JetStreamApiClient, stream: Stream) -> KV:
        """Create a new stream object from a stream object.

        Args:
            client: The JetStreamClient used to interact with the stream.
            stream: The stream object.

        Returns:
            The new stream object.
        """
        if not stream.config.name:
            raise ValueError("Stream name is required")
        if not stream.config.name.startswith("KV_"):
            raise ValueError("Stream name must start with KV_")
        bucket_name = stream.config.name[3:]
        return cls(
            client=client,
            stream_name=stream.config.name,
            bucket_name=bucket_name,
            kv_config=stream.config,
            created_timestamp=stream.created_timestamp,
        )

    @classmethod
    def from_stream_info(
        cls,
        client: JetStreamApiClient,
        stream_info: StreamInfo
        | StreamInfoResponse
        | StreamCreateResponse
        | StreamUpdateResponse,
    ) -> KV:
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
        if not stream_info.config.name.startswith("KV_"):
            raise ValueError("Stream name must start with KV_")
        bucket_name = stream_info.config.name[3:]
        return cls(
            client=client,
            stream_name=stream_info.config.name,
            bucket_name=bucket_name,
            kv_config=stream_info.config,
            created_timestamp=parse_utc_rfc3339(stream_info.created),
        )

    async def put(
        self,
        key: str,
        value: bytes,
        last_sequence: int | None = None,
    ) -> PubAckResponse:
        """Put a value into the bucket.

        Args:
            key: The key to store the value under.
            value: The value to store.
            last_sequence: The sequence number of the last value stored under this key. If the sequence number
                does not match, the put operation will fail.
        """
        return await self.client.publish(
            f"$KV.{self.bucket_name}.{key}",
            value,
            expected_last_subject_sequence=last_sequence,
        )

    async def create(self, key: str, value: bytes) -> PubAckResponse:
        """Create a new entry in the bucket.

        This method will fail if the key already exists or last operation is not a purge operation.

        Args:
            key: The key to store the value under.
            value: The value to store.
        """
        return await self.put(key, value, last_sequence=0)

    async def update(
        self, key: str, value: bytes, last_sequence: int
    ) -> PubAckResponse:
        """Update an entry in the bucket.

        This method will fail if the key does not exist, or if the last sequence number does not match.

        Args:
            key: The key to store the value under.
            value: The value to store.
            last_sequence: The sequence number of the last value stored under this key. If the sequence number
                does not match, the update operation will fail. If None, the latest value is updated.
        """
        return await self.put(key, value, last_sequence=last_sequence)

    async def get(self, key: str, sequence: int | None = None) -> Entry:
        """Get a value from the bucket.

        Args:
            key: The key to get the value for.
            sequence: The sequence number of the value to get. If the sequence number does not match, the get
                operation will fail. If None, the latest value is returned.

        Returns:
            The value, or None if the key does not exist.
        """
        # Direct bytes API
        if self.config.allow_direct:
            # Last by subject shortcut
            if sequence is None:
                msg = await self.client.direct_get_last_stream_msg_for_subject(
                    stream_name=self.stream_name,
                    subject=f"$KV.{self.bucket_name}.{key}",
                )
            else:
                # Regular direct api
                msg = await self.client.direct_get_stream_msg(
                    stream_name=self.stream_name,
                    sequence=sequence,
                    last_by_subject=f"$KV.{self.bucket_name}.{key}",
                )
        else:
            # Regular JSON (base64-encoded) API
            msg = await self.client.get_stream_msg(
                stream_name=self.stream_name,
                sequence=sequence,
                last_by_subject=f"$KV.{self.bucket_name}.{key}",
            )
        entry = Entry.from_stream_message(msg)
        if entry.operation == Operation.DEL:
            raise JetStreamAPIException(
                error=Error(
                    code=404,
                    description="Entry has been deleted",
                )
            )
        if entry.operation == Operation.PURGE:
            raise JetStreamAPIException(
                error=Error(
                    code=404,
                    description="Entry has been purged",
                )
            )
        return entry

    async def delete(
        self, key: str, last_sequence: int | None = None
    ) -> PubAckResponse:
        """Delete a value from the bucket.

        Args:
            key: The key to delete.
            last_sequence: The sequence number of the last value stored under this key. If the sequence number
                does not match, the delete operation will fail. If None, the latest value is deleted.
        """
        return await self.client.publish(
            f"$KV.{self.bucket_name}.{key}",
            b"",
            headers={"KV-Operation": "DEL"},
            expected_last_subject_sequence=last_sequence,
        )

    async def watch(
        self,
        key: str,
        include_history: bool = False,
        ignore_delete: bool = False,
        metadata_only: bool = False,
    ) -> KeyWatcher:
        """Watch a key for changes.

        Args:
            key: The key to watch.
            include_history: Whether to include the history of the key in the watcher.
            ignore_delete: Whether to ignore delete and purge operations.
            metadata_only: Whether to only watch metadata, e.g., everything except the message payload.
        """
        if not self._stream:
            stream_info = await self.client.get_stream_info(self.stream_name)
            self._stream = Stream.from_stream_info(self.client, stream_info)
        if include_history:
            deliver_policy = DeliverPolicy.all
        else:
            deliver_policy = DeliverPolicy.last_per_subject
        consumer = await self._stream.create_ephemeral_push_consumer(
            filter_subjects=f"$KV.{self.bucket_name}.{key}",
            deliver_policy=deliver_policy,
            headers_only=metadata_only,
        )
        watcher = KeyWatcher(
            consumer,
            ignore_delete=ignore_delete,
        )
        await watcher._start()  # pyright: ignore[reportPrivateUsage]
        return watcher

    async def purge(
        self,
        key: str,
        last_sequence: int | None = None,
    ) -> PubAckResponse:
        """Purge all values for a key from the bucket.

        Args:
            key: The key to purge.
            last_sequence: The sequence number of the last value stored under this key. If the sequence number
                does not match, the purge operation will fail.
        """
        return await self.client.publish(
            f"$KV.{self.bucket_name}.{key}",
            b"",
            headers={"KV-Operation": "PURGE", "Nats-Rollup": "sub"},
            expected_last_subject_sequence=last_sequence,
        )

    async def destroy(self) -> None:
        """Destroy the bucket."""
        await self.client.delete_stream(self.stream_name)

    async def list_keys(self) -> List[str]:
        """List all keys in the bucket."""
        async with await self.watch(
            ">", include_history=False, ignore_delete=True, metadata_only=True
        ) as watcher:
            keys: list[str] = []
            while True:
                entry = await watcher.next()
                if isinstance(entry, UpToDateSignal):
                    return keys
                keys.append(entry.key)
