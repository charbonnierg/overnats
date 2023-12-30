from __future__ import annotations

import base64
import json
from typing import Any, NoReturn, TypeVar

from typing_extensions import Literal

from ..connection import NatsConnection, TypedReply
from ..models.jetstream.api.account_info import GET_ACCOUNT_INFO, AccountInfoResponse
from ..models.jetstream.api.account_purge import PURGE_ACCOUNT, AccountPurgeResponse
from ..models.jetstream.api.api_error import Error, JetStreamApiV1Error
from ..models.jetstream.api.common.consumer_configuration import ConsumerConfig
from ..models.jetstream.api.common.stream_configuration import StreamConfiguration
from ..models.jetstream.api.common.stream_state import StreamState
from ..models.jetstream.api.consumer_create import (
    CREATE_DURABLE_CONSUMER,
    CREATE_EPHEMERAL_CONSUMER,
    CREATE_FILTERED_DURABLE_CONSUMER,
    ConsumerCreateResponse,
    JetstreamApiV1ConsumerCreateParams,
    JetstreamApiV1ConsumerCreateRequest,
    JetstreamApiV1ConsumerDurableCreateParams,
    JetstreamApiV1ConsumerFilteredDurableCreateParams,
)
from ..models.jetstream.api.consumer_delete import (
    DELETE_CONSUMER,
    ConsumerDeleteResponse,
    JetStreamApiV1ConsumerDeleteParams,
)
from ..models.jetstream.api.consumer_getnext import (
    GET_CONSUMER_NEXT_MSG,
    JetStreamApiV1ConsumerGetnextParams,
    JetStreamApiV1ConsumerGetnextRequest,
)
from ..models.jetstream.api.consumer_info import (
    GET_CONSUMER_INFO,
    ConsumerInfoResponse,
    JetStreamApiV1ConsumerInfoParams,
)
from ..models.jetstream.api.consumer_leader_stepdown import (
    STEPDOWN_CONSUMER_LEADER,
    ConsumerLeaderStepdownResponse,
    JetStreamApiV1ConsumerLeaderStepdownParams,
)
from ..models.jetstream.api.consumer_list import (
    LIST_CONSUMERS,
    ConsumerListResponse,
    JetStreamApiV1ConsumerListParams,
    JetstreamApiV1ConsumerListRequest,
)
from ..models.jetstream.api.consumer_names import (
    LIST_CONSUMER_NAMES,
    ConsumerNamesResponse,
    JetStreamApiV1ConsumerNamesParams,
    JetstreamApiV1ConsumerNamesRequest,
)
from ..models.jetstream.api.meta_leader_stepdown import (
    STEPDOWN_LEADER,
    JetstreamApiV1MetaLeaderStepdownRequest,
    MetaLeaderStepdownResponse,
)
from ..models.jetstream.api.meta_server_remove import (
    REMOVE_SERVER,
    JetstreamApiV1MetaServerRemoveRequest,
    MetaServerRemoveResponse,
)
from ..models.jetstream.api.pub_ack_response import (
    JetstreamApiV1PubAckResponse,
    PubAckResponse,
)
from ..models.jetstream.api.stream_create import (
    CREATE_STREAM,
    JetstreamApiV1StreamCreateParams,
    StreamCreateResponse,
)
from ..models.jetstream.api.stream_delete import (
    DELETE_STREAM,
    JetStreamApiV1StreamDeleteParams,
    StreamDeleteResponse,
)
from ..models.jetstream.api.stream_info import (
    GET_STREAM_INFO,
    JetStreamApiV1StreamInfoParams,
    JetStreamApiV1StreamInfoRequest,
    StreamInfoResponse,
)
from ..models.jetstream.api.stream_leader_stepdown import (
    STEPDOWN_STREAM_LEADER,
    JetStreamApiV1StreamLeaderStepdownParams,
    StreamLeaderStepdownResponse,
)
from ..models.jetstream.api.stream_list import (
    LIST_STREAMS,
    JetstreamApiV1StreamListRequest,
    StreamListResponse,
)
from ..models.jetstream.api.stream_msg_delete import (
    DELETE_STREAM_MSG,
    JetStreamApiV1StreamMsgDeleteParams,
    JetStreamApiV1StreamMsgDeleteRequest,
    StreamMsgDeleteResponse,
)
from ..models.jetstream.api.stream_msg_get import (
    DIRECT_GET_STREAM_LAST_MSG_FOR_SUBJECT,
    DIRECT_GET_STREAM_MSG,
    GET_STREAM_MSG,
    JetStreamApiV1StreamDirectGetLastMsgForSubjectParams,
    JetStreamApiV1StreamDirectMsgGetParams,
    JetStreamApiV1StreamMsgGetParams,
    JetStreamApiV1StreamMsgGetRequest,
    StreamMsgGetResponse,
)
from ..models.jetstream.api.stream_names import (
    LIST_STREAM_NAMES,
    JetstreamApiV1StreamNamesRequest,
    StreamNamesResponse,
)
from ..models.jetstream.api.stream_purge import (
    PURGE_STREAM,
    JetStreamApiV1StreamPurgeParams,
    JetStreamApiV1StreamPurgeRequest,
    StreamPurgeResponse,
)
from ..models.jetstream.api.stream_remove_peer import (
    STREAM_PEER_REMOVE,
    JetStreamApiV1StreamRemovePeerParams,
    JetStreamApiV1StreamRemovePeerRequest,
    StreamRemovePeerResponse,
)
from ..models.jetstream.api.stream_restore import (
    RESTORE_STREAM,
    JetStreamApiV1StreamRestoreParams,
    JetStreamApiV1StreamRestoreRequest,
    StreamRestoreResponse,
)
from ..models.jetstream.api.stream_snapshot import (
    SNAPSHOT_STREAM,
    JetStreamApiV1StreamSnapshotParams,
    JetStreamApiV1StreamSnapshotRequest,
    StreamSnapshotResponse,
)
from ..models.jetstream.api.stream_template_create import (
    CREATE_STREAM_TEMPLATE,
    JetStreamApiV1StreamTemplateCreateParams,
    JetStreamApiV1StreamTemplateCreateRequest,
    StreamTemplateCreateResponse,
)
from ..models.jetstream.api.stream_template_delete import (
    DELETE_STREAM_TEMPLATE,
    JetStreamApiV1StreamTemplateDeleteParams,
    StreamTemplateDeleteResponse,
)
from ..models.jetstream.api.stream_template_info import (
    GET_STREAM_TEMPLATE_INFO,
    JetStreamApiV1StreamTemplateInfoParams,
    StreamTemplateInfoResponse,
)
from ..models.jetstream.api.stream_template_names import (
    LIST_STREAM_TEMPLATE_NAMES,
    JetStreamApiV1StreamTemplateNamesRequest,
    StreamTemplateNamesResponse,
)
from ..models.jetstream.api.stream_update_response import (
    UPDATE_STREAM,
    JetStreamApiV1StreamUpdateParams,
    StreamUpdateResponse,
)

T = TypeVar("T")


class JetStreamClient:
    """Low-level JetStream client.

    This class provides a low-level interface to the JetStream API. It is not intended
    to be used directly, but rather to be used by higher-level abstractions.
    """

    def __init__(
        self,
        connection: NatsConnection,
        api_prefix: str = "$JS.API.",
    ) -> None:
        self.connection = connection.typed()
        self.js_api_prefix = api_prefix

    def _raise_jetstream_error(self, error: Error) -> NoReturn:
        raise Exception(error.code)

    def _unwrap_reply(
        self,
        reply: TypedReply[Any, T, str] | TypedReply[Any, T | JetStreamApiV1Error, str],
    ) -> T:
        if data := reply.get_data():
            if isinstance(data, JetStreamApiV1Error):
                self._raise_jetstream_error(data.error)
            return data
        raise Exception(reply.error())

    async def get_account_info(self) -> AccountInfoResponse:
        """Get information about the current JetStream account.

        Returns:
            A response containing information about the current JetStream account,
                such as the account limits and usage.
        """
        reply = await self.connection.request_command(
            GET_ACCOUNT_INFO,
            params=None,
            payload=None,
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def purge_account(self) -> AccountPurgeResponse:
        """Purge all data from the current JetStream account.

        Returns:
            A response containing a boolean indicating whether the purge was successfully initiated.
        """
        reply = await self.connection.request_command(
            PURGE_ACCOUNT,
            params=None,
            payload=None,
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def list_streams(
        self,
        subject: str | None = None,
        offset: int | None = None,
    ) -> StreamListResponse:
        """List all streams in the current JetStream account.

        Args:
            subject: Filter streams by subject.
            offset: Offset into the list of streams.

        Returns:
            A response containing a list of streams.
        """
        reply = await self.connection.request_command(
            LIST_STREAMS,
            params=None,
            payload=JetstreamApiV1StreamListRequest(
                subject=subject,
                offset=offset,
            ),
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def list_stream_names(
        self,
        subject: str | None = None,
        offset: int | None = None,
    ) -> StreamNamesResponse:
        """List the names of all streams in the current JetStream account.

        Args:
            subject: Filter streams by subject.
            offset: Offset into the list of streams.

        Returns:
            A response containing a list of stream names.
        """
        reply = await self.connection.request_command(
            LIST_STREAM_NAMES,
            params=None,
            payload=JetstreamApiV1StreamNamesRequest(
                subject=subject,
                offset=offset,
            ),
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def list_stream_template_names(
        self,
        offset: int | None = None,
    ) -> StreamTemplateNamesResponse:
        """List the names of all stream templates in the current JetStream account.

        Args:
            offset: Offset into the list of stream templates.

        Returns:
            A response containing a list of stream template names.
        """
        reply = await self.connection.request_command(
            LIST_STREAM_TEMPLATE_NAMES,
            params=None,
            payload=JetStreamApiV1StreamTemplateNamesRequest(
                offset=offset or 0,
            ),
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def create_stream_template(
        self,
        template_name: str,
        stream_config: StreamConfiguration,
        max_streams: int | None = None,
    ) -> StreamTemplateCreateResponse:
        """Create a new stream template.

        Args:
            template_name: The name of the template to create.
            stream_config: The stream configuration to create streams with for this template.
            max_streams: The maximum number of streams allowed to be created from this template.

        Returns:
            A response containing the template configuration.
        """
        reply = await self.connection.request_command(
            CREATE_STREAM_TEMPLATE,
            params=JetStreamApiV1StreamTemplateCreateParams(
                template_name=template_name,
            ),
            payload=JetStreamApiV1StreamTemplateCreateRequest(
                name=template_name,
                config=stream_config,
                max_streams=max_streams or -1,
            ),
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def delete_stream_template(
        self,
        template_name: str,
    ) -> StreamTemplateDeleteResponse:
        """Delete the specified stream template.

        Args:
            template_name: The name of the template to delete.

        Returns:
            A response containing a boolean indicating that the template was successfully deleted.
        """
        reply = await self.connection.request_command(
            DELETE_STREAM_TEMPLATE,
            params=JetStreamApiV1StreamTemplateDeleteParams(
                template_name=template_name
            ),
            payload=None,
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def get_stream_template_info(
        self,
        template_name: str,
    ) -> StreamTemplateInfoResponse:
        """Get information about the specified stream template.

        Args:
            template_name: The name of the template to get info for.

        Returns:
            A response holding stream template info.
        """
        reply = await self.connection.request_command(
            GET_STREAM_TEMPLATE_INFO,
            params=JetStreamApiV1StreamTemplateInfoParams(template_name=template_name),
            payload=None,
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def get_stream_info(
        self,
        stream_name: str,
        deleted_details: bool | None = None,
        subjects_filter: str | None = None,
        offset: int | None = None,
    ) -> StreamInfoResponse:
        """Get information about the specified stream.

        Args:
            stream_name: the name of the stream to get info for
            deleted_details: include information about deleted messages
            subjects_filter: filter by subjects
            offset: offset into the list of messages

        Returns:
            A response holding stream info.
        """
        reply = await self.connection.request_command(
            GET_STREAM_INFO,
            params=JetStreamApiV1StreamInfoParams(stream_name=stream_name),
            payload=JetStreamApiV1StreamInfoRequest(
                deleted_details=deleted_details,
                subjects_filter=subjects_filter,
                offset=offset,
            ),
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def direct_get_last_stream_msg_for_subject(
        self,
        stream_name: str,
        subject: str,
    ) -> bytes:
        """Get the last message for the specified subject from the specified stream.

        Args:
            stream_name: the name of the stream to get the message from
            subject: get the last message for this subject

        Returns:
            A response holding the message. This is not the same python type as a message
            received from a subscription.
        """
        reply = await self.connection.request_command(
            DIRECT_GET_STREAM_LAST_MSG_FOR_SUBJECT,
            params=JetStreamApiV1StreamDirectGetLastMsgForSubjectParams(
                stream_name=stream_name,
                subject=subject,
            ),
            payload=None,
            prefix=self.js_api_prefix,
        )
        # Check response status
        status = reply.headers.pop("Status", None)
        if status:
            raise Exception(status)
        return reply.data()

    async def direct_get_stream_msg(
        self,
        stream_name: str,
        sequence: int | None = None,
        last_by_subject: str | None = None,
        next_by_subject: str | None = None,
    ) -> bytes:
        """Get the specified message from the specified stream.

        Args:
            stream_name: the name of the stream to get the message from
            sequence: get the message with this sequence number

        Returns:
            A response holding the message. This is not the same python type as a message
            received from a subscription.
        """
        reply = await self.connection.request_command(
            DIRECT_GET_STREAM_MSG,
            params=JetStreamApiV1StreamDirectMsgGetParams(stream_name=stream_name),
            payload=JetStreamApiV1StreamMsgGetRequest(
                seq=sequence,
                last_by_subj=last_by_subject,
                next_by_subj=next_by_subject,
            ),
            prefix=self.js_api_prefix,
        )
        # Check response status
        status = reply.headers.pop("Status", None)
        if status:
            raise Exception(status)
        # # Check subject
        # subject = reply.headers.pop("Nats-Subject", None)
        # if not subject:
        #     raise RuntimeError("Expected subject header")
        # # Check sequence
        # raw_seq = reply.headers.pop("Nats-Sequence", None)
        # if not raw_seq:
        #     raise RuntimeError("Expected sequence header")
        # sequence = int(raw_seq)
        # # Check timestamp
        # raw_timestamp = reply.headers.pop("Nats-Time-Stamp", None)
        # if not raw_timestamp:
        #     raise RuntimeError("Expected timestamp header")
        # timestamp = datetime.datetime.fromisoformat(raw_timestamp)
        return reply.data()

    async def get_stream_msg(
        self,
        stream_name: str,
        sequence: int | None = None,
        last_by_subject: str | None = None,
        next_by_subject: str | None = None,
    ) -> StreamMsgGetResponse:
        """Get the specified message from the specified stream.

        - `sequence` and `last_by_subject` are mutually exclusive.

        - When `next_by_subject` is specified, `sequence` must also be specified,
        and `last_by_subject` must not be specified.

        Args:
            stream_name: the name of the stream to get the message from
            sequence: get the message with this sequence number (unless `next_by_subj` is specified)
            last_by_subject: get the last message for this subject
            next_by_subject: get the next message for this subject wit sequence greater than `seq`

        Returns:
            A response holding the message. This is not the same python type as a message
            received from a subscription.
        """
        reply = await self.connection.request_command(
            GET_STREAM_MSG,
            params=JetStreamApiV1StreamMsgGetParams(stream_name=stream_name),
            payload=JetStreamApiV1StreamMsgGetRequest(
                seq=sequence,
                last_by_subj=last_by_subject,
                next_by_subj=next_by_subject,
            ),
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def create_stream(
        self, stream_config: StreamConfiguration
    ) -> StreamCreateResponse:
        """Create a stream.

        Args:
            stream_config: The stream configuration.

        Raises:
            ValueError: If the stream name is not set in the config.

        Returns:
            A response containing the stream configuration and state.
        """
        if not stream_config.name:
            raise ValueError("name must be set in config")
        reply = await self.connection.request_command(
            CREATE_STREAM,
            params=JetstreamApiV1StreamCreateParams(stream_name=stream_config.name),
            payload=stream_config,
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def update_stream(
        self, stream_config: StreamConfiguration
    ) -> StreamUpdateResponse:
        """Update a stream.

        Args:
            stream_config: The stream configuration.

        Raises:
            ValueError: If the stream name is not set in the config.

        Returns:
            A response containing the updated stream configuration and state.
        """
        if not stream_config.name:
            raise ValueError("name must be set in config")
        reply = await self.connection.request_command(
            UPDATE_STREAM,
            params=JetStreamApiV1StreamUpdateParams(stream_name=stream_config.name),
            payload=stream_config,
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def purge_stream(
        self,
        stream_name: str,
        subject: str | None = None,
        until_sequence: int | None = None,
        keep: int | None = None,
    ) -> StreamPurgeResponse:
        """Purge all data from the specified stream.

        Args:
            stream_name: The name of the stream to purge.
            subject: Only purge messages on this subject.
            until_sequence: Purge messages up to this sequence number.
            keep: Keep this number of messages.
        """
        reply = await self.connection.request_command(
            PURGE_STREAM,
            params=JetStreamApiV1StreamPurgeParams(stream_name=stream_name),
            payload=JetStreamApiV1StreamPurgeRequest(
                filter=subject,
                seq=until_sequence,
                keep=keep,
            ),
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def delete_stream(self, stream_name: str) -> StreamDeleteResponse:
        """Delete the specified stream.

        Args:
            stream_name: The name of the stream to delete.

        Returns:
            A response containing a boolean indicating that the stream was successfully deleted.
        """
        reply = await self.connection.request_command(
            DELETE_STREAM,
            params=JetStreamApiV1StreamDeleteParams(stream_name=stream_name),
            payload=None,
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def delete_stream_msg(
        self,
        stream_name: str,
        sequence: int,
        no_erase: bool | None = None,
    ) -> StreamMsgDeleteResponse:
        """Delete the specified message from the specified stream.

        Args:
            stream_name: The name of the stream to delete the message from.
            sequence: The sequence number of the message to delete.
            no_erase: If true, do not erase the message from disk.

        Returns:
            A response containing a boolean indicating that the message was successfully deleted.
        """
        reply = await self.connection.request_command(
            DELETE_STREAM_MSG,
            params=JetStreamApiV1StreamMsgDeleteParams(stream_name=stream_name),
            payload=JetStreamApiV1StreamMsgDeleteRequest(
                seq=sequence, no_erase=no_erase
            ),
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def restore_stream(
        self,
        stream_name: str,
        stream_config: StreamConfiguration,
        stream_state: StreamState,
    ) -> StreamRestoreResponse:
        """Request a stream restore.

        Args:
            stream_name: The name of the stream to restore.
            stream_config: The stream configuration.
            stream_state: The stream state.

        Returns:
            A response containing the deliver subject where the chunks to restore should be published.
        """
        reply = await self.connection.request_command(
            RESTORE_STREAM,
            params=JetStreamApiV1StreamRestoreParams(stream_name=stream_name),
            payload=JetStreamApiV1StreamRestoreRequest(
                config=stream_config,
                state=stream_state,
            ),
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def snapshot_stream(
        self,
        stream_name: str,
        deliver_subject: str,
        no_consumers: bool | None = None,
        chunk_size: int | None = None,
        jsck: bool | None = None,
    ) -> StreamSnapshotResponse:
        """Request a stream snapshot.

        Args:
            stream_name: The name of the stream to snapshot.
            deliver_subject: The subject where the snapshot chunks should be delivered.
            no_consumers: If true, do not snapshot consumer state.
            chunk_size: The maximum size of each snapshot chunk.
            jsck: Need to document this feature ??

        Returns:
            A response containing the stream config and stream state that will be snapshotted.
        """
        reply = await self.connection.request_command(
            SNAPSHOT_STREAM,
            params=JetStreamApiV1StreamSnapshotParams(stream_name=stream_name),
            payload=JetStreamApiV1StreamSnapshotRequest(
                deliver_subject=deliver_subject,
                no_consumers=no_consumers,
                chunk_size=chunk_size,
                jsck=jsck,
            ),
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def list_consumers(
        self,
        stream_name: str,
        offset: int = 0,
    ) -> ConsumerListResponse:
        """List all consumers in the specified stream.

        Args:
            stream_name: The name of the stream to list consumers for.
            offset: Offset into the list of consumers.

        Returns:
            A response containing a list of consumers.
        """
        reply = await self.connection.request_command(
            LIST_CONSUMERS,
            params=JetStreamApiV1ConsumerListParams(stream_name=stream_name),
            payload=JetstreamApiV1ConsumerListRequest(offset=offset),
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def list_consumer_names(
        self,
        stream_name: str,
        offset: int = 0,
    ) -> ConsumerNamesResponse:
        """List the names of all consumers in the specified stream.

        Args:
            stream_name: The name of the stream to list consumers for.
            offset: Offset into the list of consumers.

        Returns:
            A response containing a list of consumer names.
        """
        reply = await self.connection.request_command(
            LIST_CONSUMER_NAMES,
            params=JetStreamApiV1ConsumerNamesParams(stream_name=stream_name),
            payload=JetstreamApiV1ConsumerNamesRequest(offset=offset),
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def get_consumer_info(
        self,
        stream_name: str,
        consumer_name: str,
    ) -> ConsumerInfoResponse:
        """Get information about the specified consumer in the specified stream.

        Args:
            stream_name: The name of the stream the consumer is in.
            consumer_name: The name of the consumer to get info for.

        Returns:
            A response containing information about the consumer.
        """
        reply = await self.connection.request_command(
            GET_CONSUMER_INFO,
            params=JetStreamApiV1ConsumerInfoParams(
                stream_name=stream_name,
                consumer_name=consumer_name,
            ),
            payload=None,
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def create_ephemeral_consumer(
        self,
        stream_name: str,
        consumer_config: ConsumerConfig,
    ) -> ConsumerCreateResponse:
        """Create a consumer in the specified stream.

        Args:
            stream_name: The name of the stream to create the consumer in.
            consumer_config: The consumer configuration.

        Returns:
            A response containing the consumer configuration and state.
        """
        reply = await self.connection.request_command(
            CREATE_EPHEMERAL_CONSUMER,
            params=JetstreamApiV1ConsumerCreateParams(stream_name=stream_name),
            payload=JetstreamApiV1ConsumerCreateRequest(
                stream_name=stream_name,
                config=consumer_config,
            ),
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def create_durable_consumer(
        self,
        stream_name: str,
        consumer_config: ConsumerConfig,
    ) -> ConsumerCreateResponse:
        """Create a durable consumer in the specified stream.

        Args:
            stream_name: The name of the stream to create the consumer in.
            consumer_config: The consumer configuration.

        Returns:
            A response containing the consumer configuration and state.
        """
        if not consumer_config.durable_name:
            raise ValueError("durable_name must be set in config")
        reply = await self.connection.request_command(
            CREATE_DURABLE_CONSUMER,
            params=JetstreamApiV1ConsumerDurableCreateParams(
                stream_name=stream_name,
                durable_name=consumer_config.durable_name,
            ),
            payload=JetstreamApiV1ConsumerCreateRequest(
                stream_name=stream_name,
                config=consumer_config,
            ),
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def create_filtered_durable_consumer(
        self,
        stream_name: str,
        consumer_config: ConsumerConfig,
    ) -> ConsumerCreateResponse:
        """Create a filtered durable consumer in the specified stream.

        Args:
            stream_name: The name of the stream to create the consumer in.
            consumer_config: The consumer configuration.

        Returns:
            A response containing the consumer configuration and state.
        """
        if not consumer_config.durable_name:
            raise ValueError("durable_name must be set in config")
        if not consumer_config.filter_subject:
            raise ValueError("filter_subject must be set in config")
        if consumer_config.filter_subjects:
            raise ValueError("filter_subjects must not be set in config")

        reply = await self.connection.request_command(
            CREATE_FILTERED_DURABLE_CONSUMER,
            params=JetstreamApiV1ConsumerFilteredDurableCreateParams(
                stream_name=stream_name,
                durable_name=consumer_config.durable_name,
                filter=consumer_config.filter_subject,
            ),
            payload=JetstreamApiV1ConsumerCreateRequest(
                stream_name=stream_name,
                config=consumer_config,
            ),
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def delete_consumer(
        self,
        stream_name: str,
        consumer_name: str,
    ) -> ConsumerDeleteResponse:
        """Delete the specified consumer from the specified stream.

        Args:
            stream_name: The name of the stream the consumer is in.
            consumer_name: The name of the consumer to delete.

        Returns:
            A response containing a boolean indicating that the consumer was successfully deleted.
        """
        reply = await self.connection.request_command(
            DELETE_CONSUMER,
            params=JetStreamApiV1ConsumerDeleteParams(
                stream_name=stream_name,
                consumer_name=consumer_name,
            ),
            payload=None,
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def request_next_message_for_consumer(
        self,
        reply_subject: str,
        stream_name: str,
        consumer_name: str,
        batch: int = 1,
        expires: int | None = None,
        max_bytes: int | None = None,
        no_wait: bool | None = None,
        idle_heartbeat: int | None = None,
    ) -> None:
        """Consume the next message from the specified consumer in the specified stream.

        This method does not return the message fetched from stream, but rather accepts
        a reply subect (through the `reply_subject` argument) where the message will be
        delivered to.

        Args:
            reply_subject: The subject where the message will be delivered to.
            stream_name: The name of the stream the consumer is in.
            consumer_name: The name of the consumer to get the next message for.
            batch: The number of messages to fetch.
            expires: The number of seconds to wait for a message.
            max_bytes: The maximum number of bytes to fetch.
            no_wait: If true, do not wait for a message. When set, the server will send an empty message with a header if no message is available.
            idle_heartbeat: The number of seconds between heartbeats. When set, the server will send a heartbeat if no message is available.

        Returns:
            None. The message will be delivered to the reply subject. It's also possible
                that the message will never be delivered to the reply subject if the
                request never reaches the server.
        """
        await self.connection.publish_command(
            GET_CONSUMER_NEXT_MSG,
            params=JetStreamApiV1ConsumerGetnextParams(
                stream_name=stream_name,
                consumer_name=consumer_name,
            ),
            payload=JetStreamApiV1ConsumerGetnextRequest(
                batch=batch,
                expires=expires,
                max_bytes=max_bytes,
                no_wait=no_wait,
                idle_heartbeat=idle_heartbeat,
            ),
            prefix=self.js_api_prefix,
            reply_subject=reply_subject,
        )

    async def stepdown_consumer_leader(
        self,
        stream_name: str,
        consumer_name: str,
    ) -> ConsumerLeaderStepdownResponse:
        """Force the current consumer leader to step down.

        Args:
            stream_name: The name of the stream the consumer is in.
            consumer_name: The name of the consumer to get the next message for.

        Returns:
            A response containing a boolean indicating that the consumer leader was successfully stepped down.
        """
        reply = await self.connection.request_command(
            STEPDOWN_CONSUMER_LEADER,
            params=JetStreamApiV1ConsumerLeaderStepdownParams(
                stream_name=stream_name,
                consumer_name=consumer_name,
            ),
            payload=None,
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def stepdown_stream_leader(
        self,
        stream_name: str,
    ) -> StreamLeaderStepdownResponse:
        """Force the current stream leader to step down.

        Args:
            stream_name: The name of the stream to step down the leader for.

        Returns:
            A response containing a boolean indicating that the stream leader was successfully stepped down.
        """
        reply = await self.connection.request_command(
            STEPDOWN_STREAM_LEADER,
            params=JetStreamApiV1StreamLeaderStepdownParams(stream_name=stream_name),
            payload=None,
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def remove_stream_peer(
        self, stream_name: str, peer: str
    ) -> StreamRemovePeerResponse:
        """Remove the specified peer from the stream.

        Args:
            stream_name: The name of the stream to remove the peer from.
            peer: The peer (NATS server name or ID ?) to remove.

        Returns:
            A response containing a boolean indicating that the peer was successfully removed.
        """
        reply = await self.connection.request_command(
            STREAM_PEER_REMOVE,
            params=JetStreamApiV1StreamRemovePeerParams(stream_name=stream_name),
            payload=JetStreamApiV1StreamRemovePeerRequest(peer=peer),
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def stepdown_leader(self) -> MetaLeaderStepdownResponse:
        """Force the current metadata leader to step down.

        Returns:
            A response containing a boolean indicating that the metadata leader was successfully stepped down.
        """
        reply = await self.connection.request_command(
            STEPDOWN_LEADER,
            params=None,
            payload=JetstreamApiV1MetaLeaderStepdownRequest(),
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def remove_server(
        self,
        peer: str | None = None,
        peer_id: str | None = None,
    ) -> MetaServerRemoveResponse:
        """Remove the specified server from the metadata cluster.

        Args:
            peer: The peer (NATS server name) to remove.
            peer_id: The peer ID (NATS server ID) to remove.

        Returns:
            A response containing a boolean indicating that the server was successfully removed.
        """
        reply = await self.connection.request_command(
            REMOVE_SERVER,
            params=None,
            payload=JetstreamApiV1MetaServerRemoveRequest(
                peer=peer,
                peer_id=peer_id,
            ),
            prefix=self.js_api_prefix,
        )
        return self._unwrap_reply(reply)

    async def publish(
        self,
        subject: str,
        payload: bytes | None = None,
        headers: dict[str, Any] | None = None,
        msg_id: str | None = None,
        expected_stream: str | None = None,
        expected_last_msg_id: str | None = None,
        expected_last_sequence: int | None = None,
        expected_last_subject_sequence: int | None = None,
        purge: Literal["sub", "all"] | None = None,
    ) -> PubAckResponse:
        """Publish a message to a subject backed by a stream.

        Args:
            subject: The subject to publish to.
            payload: The message payload.
            headers: The message headers.
            msg_id: The message ID.
            expected_stream: The stream to publish to (optional).
            expected_last_msg_id: The last message ID (optional).
            expected_last_sequence: The last sequence number (optional).
            expected_last_subject_sequence: The last sequence number for the subject (optional).
            purge: Used to apply a purge of all prior messages in the stream or at the subject-level before publishing.

        Raises:
            BadStreamError: If the stream does not match the expected stream.
            BadLastMsgIdError: If the last message ID does not match the expected last message ID.
            BadLastSequenceError: If the last sequence number does not match the expected last sequence number.
            BadLastSubjectSequenceError: If the last sequence number for the subject does not match the expected last sequence number for the subject.

        Returns:
            The publish acknowledgement response containg the sequence of the published message.
        """
        headers = headers or {}
        if expected_stream:
            headers["Nats-Expected-Stream"] = expected_stream
        if msg_id:
            headers["Nats-Msg-Id"] = msg_id
        if expected_last_msg_id:
            headers["Nats-Expected-Last-Msg-Id"] = expected_last_msg_id
        if expected_last_sequence:
            headers["Nats-Expected-Last-Sequence"] = expected_last_sequence
        if expected_last_subject_sequence:
            headers[
                "Nats-Expected-Last-Subject-Sequence"
            ] = expected_last_subject_sequence
        if purge:
            headers["Nats-Rollup"] = purge
        reply = await self.connection.connection.request(
            subject=subject,
            payload=payload,
            headers=headers,
            timeout=5,
        )
        data = json.loads(reply.payload)
        ack = JetstreamApiV1PubAckResponse(**data)
        if ack.error:
            self._raise_jetstream_error(ack.error)
        if not ack.seq:
            raise RuntimeError(
                "No sequence number in PubAckResponse. Please fill a bug report."
            )
        return PubAckResponse(
            stream=ack.stream,
            seq=ack.seq,
            duplicate=ack.duplicate,
            domain=ack.domain,
        )


class Stream:
    def __init__(self, name: str, client: JetStreamClient) -> None:
        self.name = name
        self.client = client
        self.infos: StreamInfoResponse | None = None

    async def open(self) -> None:
        """Open the stream."""
        await self.refresh()

    async def close(self) -> None:
        """Close the stream."""
        self.infos = None

    async def refresh(self) -> StreamInfoResponse:
        """Refresh the stream infos."""
        self.infos = await self.client.get_stream_info(self.name)
        return self.infos

    async def get_msg(
        self,
        sequence: int | None = None,
        last_by_subject: str | None = None,
        next_by_subject: str | None = None,
    ) -> bytes:
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
        if not self.infos:
            raise RuntimeError("Stream is not open")
        # Request validation
        if sequence is None and next_by_subject:
            raise ValueError("next_by_subject requires sequence to be specified")
        # Direct bytes API
        if self.infos.config.allow_direct:
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
        response = await self.client.get_stream_msg(
            stream_name=self.name,
            sequence=sequence,
            last_by_subject=last_by_subject,
            next_by_subject=next_by_subject,
        )
        if not response.message.data:
            return b""
        return base64.b64decode(response.message.data)

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
            subject: The subject to publish to.
            payload: The message payload.
            headers: The message headers.
            msg_id: The message ID.
            expected_last_msg_id: The last message ID (optional).
            expected_last_sequence: The last sequence number (optional).
            expected_last_subject_sequence: The last sequence number for the subject (optional).
            purge: Used to apply a purge of all prior messages in the stream or at the subject-level before publishing.

        Raises:
            BadLastMsgIdError: If the last message ID does not match the expected last message ID.
            BadLastSequenceError: If the last sequence number does not match the expected last sequence number.
            BadLastSubjectSequenceError: If the last sequence number for the subject does not match the expected last sequence number for the subject.

        Returns:
            The publish acknowledgement response containg the sequence of the published message.
        """
        if not self.infos:
            raise RuntimeError("Stream is not open")
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

    async def delete(self) -> None:
        """Delete the stream.

        Returns:
            A response containing a boolean indicating that the stream was successfully deleted.
        """
        if not self.infos:
            raise RuntimeError("Stream is not open")
        await self.client.delete_stream(self.name)
        self.infos = None

    async def purge(
        self,
        subject: str | None = None,
        until_sequence: int | None = None,
        keep: int | None = None,
    ) -> int:
        """Purge all data from the stream.

        Args:
            subject: Only purge messages on this subject.
            until_sequence: Purge messages up to this sequence number.
            keep: Keep this number of messages.

        Returns:
            A response containing a boolean indicating that the purge was successfully initiated.
        """
        if not self.infos:
            raise RuntimeError("Stream is not open")
        response = await self.client.purge_stream(
            stream_name=self.name,
            subject=subject,
            until_sequence=until_sequence,
            keep=keep,
        )
        return response.purged

    async def update(
        self,
        stream_config: StreamConfiguration,
    ) -> None:
        """Update the stream.

        Args:
            stream_config: The stream configuration.

        Returns:
            A response containing the updated stream configuration and state.
        """
        if not self.infos:
            raise RuntimeError("Stream is not open")
        if stream_config.name != self.name:
            raise ValueError("stream_config.name must match stream name")
        await self.client.update_stream(stream_config)
        await self.refresh()

    async def list_consumer_names(self) -> list[str]:
        """List the names of all consumers in the stream.

        Args:
            offset: Offset into the list of consumers.

        Returns:
            A response containing a list of consumer names.
        """
        if not self.infos:
            raise RuntimeError("Stream is not open")
        names: list[str] = []
        response = await self.client.list_consumer_names(
            stream_name=self.name,
            offset=0,
        )
        names.extend(response.consumers)
        fetched = len(names)

        while fetched < response.total:
            response = await self.client.list_consumer_names(
                stream_name=self.name,
                offset=fetched,
            )
            names.extend(response.consumers)
            fetched = len(names)

        return names


class PushConsumer:
    def __init__(
        self,
        stream_name: str,
        consumer_name: str,
        client: JetStreamClient,
    ) -> None:
        self.stream_name = stream_name
        self.consumer_name = consumer_name
        self.client = client
        self.infos: ConsumerInfoResponse | None = None

    async def open(self) -> None:
        """Open the consumer."""
        await self.refresh()

    async def close(self) -> None:
        """Close the consumer."""
        self.infos = None

    async def refresh(self) -> ConsumerInfoResponse:
        """Refresh the consumer infos."""
        self.infos = await self.client.get_consumer_info(
            stream_name=self.stream_name,
            consumer_name=self.consumer_name,
        )
        return self.infos

    async def get_next_msg(
        self,
    ) -> bytes:
        raise NotImplementedError


class PullConsumer:
    def __init__(
        self,
        stream_name: str,
        consumer_name: str,
        client: JetStreamClient,
    ) -> None:
        self.stream_name = stream_name
        self.consumer_name = consumer_name
        self.client = client
        self.infos: ConsumerInfoResponse | None = None

    async def open(self) -> None:
        """Open the consumer."""
        await self.refresh()

    async def close(self) -> None:
        """Close the consumer."""
        self.infos = None

    async def refresh(self) -> ConsumerInfoResponse:
        """Refresh the consumer infos."""
        self.infos = await self.client.get_consumer_info(
            stream_name=self.stream_name,
            consumer_name=self.consumer_name,
        )
        return self.infos
