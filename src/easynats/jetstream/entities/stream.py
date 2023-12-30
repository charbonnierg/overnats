from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from pydantic import TypeAdapter

if TYPE_CHECKING:
    from ..api import JetStreamClient, StreamMessage

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


@dataclass
class StreamMeta:
    config: StreamConfig
    state: StreamState

    def to_dict(self) -> dict[str, Any]:
        return _StreamMetaAdapter.dump_python(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StreamMeta:
        return _StreamMetaAdapter.validate_python(data)

    def to_json(self) -> bytes:
        return _StreamMetaAdapter.dump_json(self)

    @classmethod
    def from_json(cls, data: str | bytes) -> StreamMeta:
        return _StreamMetaAdapter.validate_json(data)


_StreamMetaAdapter = TypeAdapter(StreamMeta)


class Stream:
    def __init__(
        self,
        client: JetStreamClient,
        stream_name: str,
        stream_config: StreamConfig,
        created_timestamp: datetime.datetime,
    ) -> None:
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
        if not stream_info.config.name:
            raise ValueError("Stream name is required")
        created_timestamp = datetime.datetime.fromisoformat(
            stream_info.created[:26]
        ).replace(tzinfo=datetime.timezone.utc)
        return cls(
            client=client,
            stream_name=stream_info.config.name,
            stream_config=stream_info.config,
            created_timestamp=created_timestamp,
        )

    async def state(self) -> StreamState:
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
            The message.
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
        """
        await self.client.delete_stream_msg(
            stream_name=self.name,
            sequence=sequence,
            no_erase=no_erase,
        )
