import pathlib
from tempfile import TemporaryDirectory

import pytest
import pytest_asyncio

from easynats.connection import Connection
from easynats.jetstream.api import Error, JetStreamAPIException
from easynats.jetstream.sdk import StreamConfig


@pytest.mark.asyncio
class BaseTestStreamManager:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        async with Connection() as self.conn:
            self.manager = self.conn.jetstream.streams
            try:
                yield
            finally:
                await self.cleanup()

    async def cleanup(self):
        # Clean up all streams
        for stream_name in await self.manager.list_names():
            await self.manager.delete(stream_name)


class TestStreamManagerListStreams(BaseTestStreamManager):
    async def test_list_streams_no_stream(self):
        streams = await self.manager.list()
        assert streams == []

    async def test_list_streams_single_stream(self):
        config = StreamConfig.new("test-stream", subjects=["test.*"])
        await self.manager.create_from_config(config)
        streams = await self.manager.list()
        assert len(streams) == 1
        assert streams[0].name == "test-stream"
        assert streams[0].config == config

    async def test_list_streams_multiple_streams(self):
        config1 = StreamConfig.new("test-stream-1", subjects=["test-1.*"])
        config2 = StreamConfig.new("test-stream-2", subjects=["test-2.*"])
        await self.manager.create_from_config(config1)
        await self.manager.create_from_config(config2)
        streams = await self.manager.list()
        assert len(streams) == 2
        assert streams[0].name == "test-stream-1"
        assert streams[0].config == config1
        assert streams[1].name == "test-stream-2"
        assert streams[1].config == config2

    async def test_list_streams_filtered_by_subject(self):
        config1 = StreamConfig.new("test-stream-1", subjects=["test-1.*"])
        config2 = StreamConfig.new("test-stream-2", subjects=["test-2.*"])
        await self.manager.create_from_config(config1)
        await self.manager.create_from_config(config2)
        streams = await self.manager.list(subject="test-1.*")
        assert len(streams) == 1
        assert streams[0].name == "test-stream-1"
        assert streams[0].config == config1

    async def test_list_streams_filtered_by_offset(self):
        config1 = StreamConfig.new("test-stream-1", subjects=["test-1.*"])
        config2 = StreamConfig.new("test-stream-2", subjects=["test-2.*"])
        await self.manager.create_from_config(config1)
        await self.manager.create_from_config(config2)
        streams = await self.manager.list(offset=1)
        assert len(streams) == 1
        assert streams[0].name == "test-stream-2"
        assert streams[0].config == config2


class TestStreamManagerListStreamNames(BaseTestStreamManager):
    async def test_list_streams_no_stream(self):
        streams = await self.manager.list_names()
        assert streams == []

    async def test_list_streams_single_stream(self):
        config = StreamConfig.new("test-stream", subjects=["test.*"])
        await self.manager.create_from_config(config)
        streams = await self.manager.list_names()
        assert len(streams) == 1
        assert streams == ["test-stream"]

    async def test_list_streams_multiple_streams(self):
        config1 = StreamConfig.new("test-stream-1", subjects=["test-1.*"])
        config2 = StreamConfig.new("test-stream-2", subjects=["test-2.*"])
        await self.manager.create_from_config(config1)
        await self.manager.create_from_config(config2)
        streams = await self.manager.list_names()
        assert len(streams) == 2
        assert streams == ["test-stream-1", "test-stream-2"]

    async def test_list_streams_filtered_by_subject(self):
        config1 = StreamConfig.new("test-stream-1", subjects=["test-1.*"])
        config2 = StreamConfig.new("test-stream-2", subjects=["test-2.*"])
        await self.manager.create_from_config(config1)
        await self.manager.create_from_config(config2)
        streams = await self.manager.list_names(subject="test-1.*")
        assert len(streams) == 1
        assert streams == ["test-stream-1"]

    async def test_list_stream_names_filtered_by_offset(self):
        config1 = StreamConfig.new("test-stream-1", subjects=["test-1.*"])
        config2 = StreamConfig.new("test-stream-2", subjects=["test-2.*"])
        await self.manager.create_from_config(config1)
        await self.manager.create_from_config(config2)
        streams = await self.manager.list_names(offset=1)
        assert len(streams) == 1
        assert streams == ["test-stream-2"]


class TestStreamManagerCreateStream(BaseTestStreamManager):
    async def test_create_stream_with_defaults(self):
        config = StreamConfig.new("test-stream", subjects=["test.*"])
        stream = await self.manager.create_from_config(config)
        assert stream.name == "test-stream"
        assert stream.config == config
        stream_ = await self.manager.get("test-stream")
        assert stream_.config == stream.config

    async def test_create_stream_with_existing_name_raises_error(self):
        config = StreamConfig.new("test-stream", subjects=["test.*"])
        await self.manager.create_from_config(config)
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.manager.create_from_config(config)
        assert exc_info.value.error == Error(
            code=400,
            description="name is already used by an existing stream",
            err_code=10058,
        )

    async def test_create_stream_with_overlaping_subjects_raises_error(self):
        config1 = StreamConfig.new("test-stream-1", subjects=["test.*"])
        config2 = StreamConfig.new("test-stream-2", subjects=["test.*"])
        await self.manager.create_from_config(config1)
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.manager.create_from_config(config2)
        assert exc_info.value.error == Error(
            code=400,
            description="subjects overlap with an existing stream",
            err_code=10065,
        )


class TestStreamManagerGetStream(BaseTestStreamManager):
    async def test_get_stream(self):
        config = StreamConfig.new("test-stream", subjects=["test.*"])
        await self.manager.create_from_config(config)
        stream = await self.manager.get("test-stream")
        assert stream.name == "test-stream"
        assert stream.config == config

    async def test_get_stream_non_existent(self):
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.manager.get("test-stream")
        assert exc_info.value.error == Error(
            code=404,
            description="stream not found",
            err_code=10059,
        )


class TestStreamManagerDeleteStream(BaseTestStreamManager):
    async def test_delete_stream(self):
        config = StreamConfig.new("test-stream", subjects=["test.*"])
        await self.manager.create_from_config(config)
        await self.manager.delete("test-stream")
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.manager.get("test-stream")
        assert exc_info.value.error == Error(
            code=404,
            description="stream not found",
            err_code=10059,
        )

    async def test_delete_stream_non_existent(self):
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.manager.delete("test-stream")
        assert exc_info.value.error == Error(
            code=404,
            description="stream not found",
            err_code=10059,
        )


class TestStreamManagerConfigureStream(BaseTestStreamManager):
    async def test_configure_stream_creates_stream(self):
        config = StreamConfig.new("test-stream", subjects=["test.*"])
        stream = await self.manager.configure(config)
        assert stream.name == "test-stream"
        assert stream.config == config

    async def test_configure_stream_gets_stream(self):
        config = StreamConfig.new("test-stream", subjects=["test.*"])
        await self.manager.create_from_config(config)
        stream = await self.manager.configure(config)
        assert stream.name == "test-stream"
        assert stream.config == config

    async def test_configure_stream_updates_stream(self):
        config = StreamConfig.new("test-stream", subjects=["test.*"])
        await self.manager.create_from_config(config)
        new_config = StreamConfig.new("test-stream", subjects=["test-1.*"])
        stream = await self.manager.configure(new_config)
        assert stream.name == "test-stream"
        assert stream.config == new_config


class TestStreamManagerBackupAndRestoreStream(BaseTestStreamManager):
    async def test_backup_and_restore_stream(self):
        config = StreamConfig.new("test-stream", subjects=["test.>"])
        stream = await self.manager.create_from_config(config)
        await stream.publish("test.1")
        await stream.publish("test.2")
        await stream.publish("test.3")
        with TemporaryDirectory() as tmpdir:
            target = pathlib.Path(tmpdir) / "backup"
            await self.manager.backup_to_directory(
                stream.name,
                target,
            )
            await self.manager.delete(stream.name)
            await self.manager.restore_from_directory(
                stream.name,
                target,
            )
        stream_state = await stream.state()
        assert stream_state.messages == 3
