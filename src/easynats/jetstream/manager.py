from __future__ import annotations

import json
import pathlib
from typing import AsyncIterator, Callable

from .api import JetStreamClient
from .entities.stream import Stream, StreamConfig, StreamMeta


class StreamManager:
    """A class to manage streams."""

    def __init__(self, client: JetStreamClient):
        self.client = client

    async def list(
        self,
        subject: str | None = None,
        offset: int | None = None,
    ) -> list[Stream]:
        """List all Streams."""
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
        """List all Stream names."""
        response = await self.client.list_streams(
            subject=subject,
            offset=offset,
        )
        return [info.config.name for info in response.streams if info.config.name]

    async def delete(self, stream_name: str) -> None:
        """Delete a Stream by name."""
        await self.client.delete_stream(stream_name=stream_name)

    async def get(self, stream_name: str) -> Stream:
        """Get a Stream by name."""
        stream_info_response = await self.client.get_stream_info(
            stream_name=stream_name
        )
        return Stream.from_stream_info_response(
            client=self.client, stream_info_response=stream_info_response
        )

    async def create(self, stream_config: StreamConfig) -> Stream:
        """Create a new Stream."""
        stream_create_response = await self.client.create_stream(
            stream_config=stream_config
        )
        return Stream.from_stream_create_response(
            client=self.client, stream_create_response=stream_create_response
        )

    async def configure(self, stream_config: StreamConfig) -> Stream:
        """Get, create or update a stream according to given configuration."""
        if not stream_config.name:
            raise ValueError("Stream name is required")
        try:
            stream = await self.get(stream_name=stream_config.name)
        except Exception:
            return await self.create(stream_config=stream_config)
        if stream.config == stream_config:
            return stream
        stream_update_response = await self.client.update_stream(stream_config)
        return Stream.from_stream_update_response(
            client=self.client, stream_update_response=stream_update_response
        )

    async def backup(
        self,
        stream_name: str,
        chunks_writer: Callable[[bytes], None],
        chunk_size: int = 1024,
        no_consumers: bool | None = None,
    ) -> StreamMeta:
        """Backup a stream."""
        nc = self.client.connection.connection
        deliver_subject = nc.client.new_inbox()
        sub = await nc.client.subscribe(  # pyright: ignore[reportUnknownMemberType]
            deliver_subject
        )
        resp = await self.client.snapshot_stream(
            stream_name=stream_name,
            deliver_subject=deliver_subject,
            chunk_size=chunk_size,
            no_consumers=no_consumers,
        )
        while True:
            msg = await sub.next_msg()
            if not msg.data:
                break
            chunks_writer(msg.data)
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
        """Restore a stream."""
        if not stream_meta.config.name:
            raise ValueError("Stream name is required")
        resp = await self.client.restore_stream(
            stream_name=stream_meta.config.name,
            stream_config=stream_meta.config,
            stream_state=stream_meta.state,
        )
        async for chunk in chunks_reader:
            await self.client.connection.connection.request(
                subject=resp.deliver_subject,
                payload=chunk,
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

        meta_filepath.write_text(json.dumps(meta.to_dict(), indent=2))
        return meta

    async def restore_from_directory(
        self,
        stream_name: str,
        directory: str | pathlib.Path,
        archive_file: str | None = None,
        meta_file: str | None = None,
        chunk_size: int = 1024,
    ) -> Stream:
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
                        break
                    yield data

            return await self.restore(
                stream_meta=StreamMeta.from_dict(json.loads(meta_filepath.read_text())),
                chunks_reader=reader(),
            )
