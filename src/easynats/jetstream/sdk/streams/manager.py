from __future__ import annotations

import pathlib
from typing import AsyncIterator, Callable

from ...api import Error, JetStreamApiClient, JetStreamAPIException
from ...models.api.common.stream_configuration import (
    Compression,
    Discard,
    Mirror,
    Placement,
    Republish,
    Retention,
    Source,
    Storage,
    SubjectTransform,
)
from .stream import Stream, StreamConfig, StreamMeta


class StreamManager:
    """A class to manage streams."""

    def __init__(self, client: JetStreamApiClient):
        self.client = client

    async def list(
        self,
        subject: str | None = None,
        offset: int | None = None,
    ) -> list[Stream]:
        """List all Streams.

        Args:
            subject: return only streams matching this subject
            offset: offset to start from

        Returns:
            A list of streams as python objects
        """
        response = await self.client.list_streams(
            subject=subject,
            offset=offset,
        )
        return [
            Stream.from_stream_info(client=self.client, stream_info=info)
            for info in response.streams
        ]

    async def list_names(
        self,
        subject: str | None = None,
        offset: int | None = None,
    ) -> list[str]:
        """List all Stream names.

        Args:
            subject: return only names of streams matching this subject
            offset: offset to start from

        Returns:
            A list of stream names
        """
        response = await self.client.list_streams(
            subject=subject,
            offset=offset,
        )
        return [info.config.name for info in response.streams if info.config.name]

    async def delete(self, stream_name: str) -> None:
        """Delete a Stream by name.

        Args:
            stream_name: name of the stream to delete

        Raises:
            JetStreamAPIException: if the NATS server returns an error

        Returns:
            None. The stream is guaranteed to be deleted if no exception is raised.
        """
        await self.client.delete_stream(stream_name=stream_name)

    async def get(self, stream_name: str) -> Stream:
        """Get a Stream by name.

        Args:
            stream_name: name of the stream to get

        Raises:
            JetStreamAPIException: if the NATS server returns an error

        Returns:
            The stream as a python object
        """
        stream_info_response = await self.client.get_stream_info(
            stream_name=stream_name
        )
        return Stream.from_stream_info(
            client=self.client, stream_info=stream_info_response
        )

    async def create(
        self,
        name: str,
        subjects: list[str] | None = None,
        retention: Retention | None = None,
        max_consumers: int | None = None,
        max_msgs: int | None = None,
        max_bytes: int | None = None,
        max_age: int | None = None,
        storage: Storage | None = None,
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
        mirror: Mirror | None = None,
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
        """Create a new Stream.

        Args:
            name: name of the stream
            subjects: list of subjects the stream will accept
            retention: retention policy
            max_consumers: maximum number of consumers
            max_msgs: maximum number of messages
            max_bytes: maximum number of bytes
            max_age: maximum age of messages
            storage: storage policy
            num_replicas: number of replicas
            duplicate_window: duplicate window
            description: description
            subject_transform: subject transform
            max_msgs_per_subject: maximum number of messages per subject
            max_msg_size: maximum message size
            compression: compression policy
            first_seq: first sequence
            no_ack: no acknowledgement
            discard: discard policy
            placement: placement policy
            mirror: mirror policy
            sources: list of sources
            sealed: sealed
            deny_delete: deny delete
            deny_purge: deny purge
            allow_rollup_hdrs: allow rollup headers
            allow_direct: allow direct
            mirror_direct: mirror direct
            republish: republish policy
            discard_new_per_subject: discard new per subject
            metadata: metadata

        Raises:
            ValueError: if the stream name is not set in the configuration
            JetStreamAPIException: if the NATS server returns an error

        Returns:
            The created stream as a python object
        """
        stream_config = StreamConfig.new(
            name=name,
            subjects=subjects,
            retention=retention,
            max_consumers=max_consumers,
            max_msgs=max_msgs,
            max_bytes=max_bytes,
            max_age=max_age,
            storage=storage,
            num_replicas=num_replicas,
            duplicate_window=duplicate_window,
            description=description,
            subject_transform=subject_transform,
            max_msgs_per_subject=max_msgs_per_subject,
            max_msg_size=max_msg_size,
            compression=compression,
            first_seq=first_seq,
            no_ack=no_ack,
            discard=discard,
            placement=placement,
            mirror=mirror,
            sources=sources,
            sealed=sealed,
            deny_delete=deny_delete,
            deny_purge=deny_purge,
            allow_rollup_hdrs=allow_rollup_hdrs,
            allow_direct=allow_direct,
            mirror_direct=mirror_direct,
            republish=republish,
            discard_new_per_subject=discard_new_per_subject,
            metadata=metadata,
        )
        return await self.create_from_config(stream_config=stream_config)

    async def create_from_config(self, stream_config: StreamConfig) -> Stream:
        """Create a new Stream.

        Args:
            stream_config: the stream configuration

        Raises:
            ValueError: if the stream name is not set in the configuration
            JetStreamAPIException: if the NATS server returns an error

        Returns:
            The created stream as a python object
        """
        names = await self.list_names()
        if stream_config.name in names:
            raise JetStreamAPIException(
                error=Error(
                    code=400,
                    description="name is already used by an existing stream",
                    err_code=10058,
                )
            )
        stream_create_response = await self.client.create_stream(
            stream_config=stream_config
        )
        return Stream.from_stream_info(
            client=self.client, stream_info=stream_create_response
        )

    async def configure(self, stream_config: StreamConfig) -> Stream:
        """Get, create or update a stream according to given configuration.

        Args:
            stream_config: the stream configuration

        Raises:
            ValueError: if the stream name is not set in the configuration
            JetStreamAPIException: if the NATS server returns an error

        Returns:
            The stream as a python object
        """
        if not stream_config.name:
            raise ValueError("Stream name is required")
        try:
            stream = await self.get(stream_name=stream_config.name)
        except Exception:
            return await self.create_from_config(stream_config=stream_config)
        if stream.config == stream_config:
            return stream
        stream_update_response = await self.client.update_stream(stream_config)
        return Stream.from_stream_info(
            client=self.client, stream_info=stream_update_response
        )

    async def backup(
        self,
        stream_name: str,
        chunks_writer: Callable[[bytes], None],
        chunk_size: int = 1024,
        no_consumers: bool | None = None,
    ) -> StreamMeta:
        """Backup a stream.

        This method accepts a function to write chunks of data. Data is a tar
        archive of the stream compressed using Snappy algorithm. It must not
        be modified as it is checked by the server. The function should
        write the data to a file or send it to a remote server in an efficient
        way.

        Args:
            stream_name: name of the stream to backup
            chunks_writer: a function to write chunks of data
            chunk_size: size of the chunks
            no_consumers: if True, consumers are not backed up

        Raises:
            JetStreamAPIException: if the NATS server returns an error

        Returns:
            The stream meta data. It contains the stream configuration and state.
        """
        conn = self.client.conn.core
        deliver_subject = conn.new_inbox()
        async with conn.subscribe(deliver_subject) as sub:
            resp = await self.client.snapshot_stream(
                stream_name=stream_name,
                deliver_subject=deliver_subject,
                chunk_size=chunk_size,
                no_consumers=no_consumers,
            )
            while True:
                msg = await sub.next()
                payload = msg.payload()
                if payload == b"":  # end of snapshot
                    break
                chunks_writer(payload)
                await msg.respond(b"")
            return StreamMeta(
                config=resp.config,
                state=resp.state,
            )

    async def restore(
        self,
        stream_meta: StreamMeta,
        chunks_reader: AsyncIterator[bytes],
    ) -> Stream:
        """Restore a stream.

        This method accepts an async iterator to read chunks of data. Data is a tar
        archive of the stream compressed using Snappy algorithm. It must not
        be modified as it is checked by the server. The iterator should
        read the data from a file or receive it from a remote server in an efficient
        way.

        Args:
            stream_meta: stream meta data. It contains the stream configuration and state.
            chunks_reader: an async iterator to read chunks of data

        Raises:
            JetStreamAPIException: if the NATS server returns an error

        Returns:
            The restored stream as a python object
        """
        if not stream_meta.config.name:
            raise ValueError("Stream name is required")
        resp = await self.client.restore_stream(
            stream_name=stream_meta.config.name,
            stream_config=stream_meta.config,
            stream_state=stream_meta.state,
        )
        async for chunk in chunks_reader:
            await self.client.conn.core.request(
                subject=resp.deliver_subject,
                payload=chunk,
            )
        await self.client.conn.core.request(
            subject=resp.deliver_subject,
            payload=b"",
        )
        return await self.get(stream_name=stream_meta.config.name)

    async def backup_to_directory(
        self,
        stream_name: str,
        output_directory: str | pathlib.Path,
        archive_file: str | None = None,
        meta_file: str | None = None,
        chunk_size: int = 1024,
        no_consumers: bool | None = None,
    ) -> StreamMeta:
        """Backup a stream to a directory in local filesystem.

        Args:
            stream_name: name of the stream to backup
            output_directory: directory where to store the backup
            archive_file: name of the archive file
            meta_file: name of the meta file
            chunk_size: size of the chunks
            no_consumers: if True, consumers are not backed up

        Raises:
            JetStreamAPIException: if the NATS server returns an error

        Returns:
            The stream meta data. It contains the stream configuration and state.
        """
        output_directory = pathlib.Path(output_directory).expanduser().resolve()
        output_directory.mkdir(parents=True, exist_ok=True)
        archive_filepath = output_directory / (archive_file or f"{stream_name}.tar.s2")
        meta_filepath = output_directory / (meta_file or f"{stream_name}.meta.json")
        with archive_filepath.open("wb") as chunks_file:

            def write_chunk(data: bytes) -> None:
                chunks_file.write(data)

            meta = await self.backup(
                stream_name=stream_name,
                chunks_writer=write_chunk,
                chunk_size=chunk_size,
                no_consumers=no_consumers,
            )

        meta_filepath.write_bytes(meta.to_json())
        return meta

    async def restore_from_directory(
        self,
        stream_name: str,
        directory: str | pathlib.Path,
        archive_file: str | None = None,
        meta_file: str | None = None,
        chunk_size: int = 1024,
    ) -> Stream:
        """Restore a stream from a directory in local filesystem.

        Args:
            stream_name: name of the stream to restore
            directory: directory where to find the backup
            archive_file: name of the archive file
            meta_file: name of the meta file
            chunk_size: size of the chunks

        Raises:
            JetStreamAPIException: if the NATS server returns an error

        Returns:
            The restored stream as a python object
        """
        archive_file = archive_file or f"{stream_name}.tar.s2"
        meta_file = meta_file or f"{stream_name}.meta.json"
        directory = pathlib.Path(directory).expanduser().resolve()
        archive_filepath = directory / archive_file
        meta_filepath = directory / meta_file
        if not archive_filepath.exists():
            raise FileNotFoundError(f"Archive file not found: {archive_filepath}")
        if not meta_filepath.exists():
            raise FileNotFoundError(f"Meta file not found: {meta_filepath}")

        with archive_filepath.open("rb") as chunks_file:

            async def reader() -> AsyncIterator[bytes]:
                while True:
                    data = chunks_file.read(chunk_size)
                    if not data:
                        return
                    yield data

            return await self.restore(
                stream_meta=StreamMeta.from_json(meta_filepath.read_text()),
                chunks_reader=reader(),
            )
