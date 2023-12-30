import pathlib
from tempfile import TemporaryDirectory

import pytest
import pytest_asyncio

from easynats.connection import NatsConnection
from easynats.jetstream.api import Error, JetStreamAPIException, JetStreamClient
from easynats.jetstream.entities import (
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
)
from easynats.jetstream.manager import StreamManager


@pytest.mark.asyncio
class BaseTestStreamManager:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        self.conn = NatsConnection()
        self.js_client = JetStreamClient(self.conn)
        self.manager = StreamManager(self.js_client)
        async with self.conn:
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
        await self.manager.create(config)
        streams = await self.manager.list()
        assert len(streams) == 1
        assert streams[0].name == "test-stream"
        assert streams[0].config == config

    async def test_list_streams_multiple_streams(self):
        config1 = StreamConfig.new("test-stream-1", subjects=["test-1.*"])
        config2 = StreamConfig.new("test-stream-2", subjects=["test-2.*"])
        await self.manager.create(config1)
        await self.manager.create(config2)
        streams = await self.manager.list()
        assert len(streams) == 2
        assert streams[0].name == "test-stream-1"
        assert streams[0].config == config1
        assert streams[1].name == "test-stream-2"
        assert streams[1].config == config2

    async def test_list_streams_filtered_by_subject(self):
        config1 = StreamConfig.new("test-stream-1", subjects=["test-1.*"])
        config2 = StreamConfig.new("test-stream-2", subjects=["test-2.*"])
        await self.manager.create(config1)
        await self.manager.create(config2)
        streams = await self.manager.list(subject="test-1.*")
        assert len(streams) == 1
        assert streams[0].name == "test-stream-1"
        assert streams[0].config == config1

    async def test_list_streams_filtered_by_offset(self):
        config1 = StreamConfig.new("test-stream-1", subjects=["test-1.*"])
        config2 = StreamConfig.new("test-stream-2", subjects=["test-2.*"])
        await self.manager.create(config1)
        await self.manager.create(config2)
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
        await self.manager.create(config)
        streams = await self.manager.list_names()
        assert len(streams) == 1
        assert streams == ["test-stream"]

    async def test_list_streams_multiple_streams(self):
        config1 = StreamConfig.new("test-stream-1", subjects=["test-1.*"])
        config2 = StreamConfig.new("test-stream-2", subjects=["test-2.*"])
        await self.manager.create(config1)
        await self.manager.create(config2)
        streams = await self.manager.list_names()
        assert len(streams) == 2
        assert streams == ["test-stream-1", "test-stream-2"]

    async def test_list_streams_filtered_by_subject(self):
        config1 = StreamConfig.new("test-stream-1", subjects=["test-1.*"])
        config2 = StreamConfig.new("test-stream-2", subjects=["test-2.*"])
        await self.manager.create(config1)
        await self.manager.create(config2)
        streams = await self.manager.list_names(subject="test-1.*")
        assert len(streams) == 1
        assert streams == ["test-stream-1"]

    async def test_list_stream_names_filtered_by_offset(self):
        config1 = StreamConfig.new("test-stream-1", subjects=["test-1.*"])
        config2 = StreamConfig.new("test-stream-2", subjects=["test-2.*"])
        await self.manager.create(config1)
        await self.manager.create(config2)
        streams = await self.manager.list_names(offset=1)
        assert len(streams) == 1
        assert streams == ["test-stream-2"]


class TestStreamManagerCreateStream(BaseTestStreamManager):
    async def test_create_stream_with_defaults(self):
        config = StreamConfig.new("test-stream", subjects=["test.*"])
        stream = await self.manager.create(config)
        assert stream.name == "test-stream"
        assert stream.config == config
        stream_ = await self.manager.get("test-stream")
        assert stream_.config == stream.config

    async def test_create_stream_with_existing_name_raises_error(self):
        config = StreamConfig.new("test-stream", subjects=["test.*"])
        await self.manager.create(config)
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.manager.create(config)
        assert exc_info.value.error == Error(
            code=400,
            description="name is already used by an existing stream",
            err_code=10058,
        )

    async def test_create_stream_with_overlaping_subjects_raises_error(self):
        config1 = StreamConfig.new("test-stream-1", subjects=["test.*"])
        config2 = StreamConfig.new("test-stream-2", subjects=["test.*"])
        await self.manager.create(config1)
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.manager.create(config2)
        assert exc_info.value.error == Error(
            code=400,
            description="subjects overlap with an existing stream",
            err_code=10065,
        )


class TestStreamManagerGetStream(BaseTestStreamManager):
    async def test_get_stream(self):
        config = StreamConfig.new("test-stream", subjects=["test.*"])
        await self.manager.create(config)
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
        await self.manager.create(config)
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
        await self.manager.create(config)
        stream = await self.manager.configure(config)
        assert stream.name == "test-stream"
        assert stream.config == config

    async def test_configure_stream_updates_stream(self):
        config = StreamConfig.new("test-stream", subjects=["test.*"])
        await self.manager.create(config)
        new_config = StreamConfig.new("test-stream", subjects=["test-1.*"])
        stream = await self.manager.configure(new_config)
        assert stream.name == "test-stream"
        assert stream.config == new_config


class TestStreamManagerBackupAndRestoreStream(BaseTestStreamManager):
    async def test_backup_and_restore_stream(self):
        config = StreamConfig.new("test-stream", subjects=["test.>"])
        stream = await self.manager.create(config)
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


class TestStreamPurge(BaseTestStreamManager):
    async def test_purge_stream(self):
        config = StreamConfig.new("test-stream", subjects=["test.>"])
        stream = await self.manager.create(config)
        await stream.publish("test.1")
        await stream.publish("test.2")
        stream_state = await stream.state()
        assert stream_state.messages == 2
        await stream.purge()
        stream_state = await stream.state()
        assert stream_state.messages == 0

    async def test_purge_stream_with_subject(self):
        config = StreamConfig.new("test-stream", subjects=["test.>"])
        stream = await self.manager.create(config)
        await stream.publish("test.1")
        await stream.publish("test.2")
        stream_state = await stream.state()
        assert stream_state.messages == 2
        await stream.purge(subject="test.1")
        stream_state = await stream.state()
        assert stream_state.messages == 1

    async def test_purge_until_sequence(self):
        config = StreamConfig.new("test-stream", subjects=["test.>"])
        stream = await self.manager.create(config)
        await stream.publish("test.1")
        await stream.publish("test.2")
        await stream.publish("test.3")
        stream_state = await stream.state()
        assert stream_state.messages == 3
        await stream.purge(until_sequence=2)
        stream_state = await stream.state()
        assert stream_state.messages == 2

    async def test_purge_keep(self):
        config = StreamConfig.new("test-stream", subjects=["test.>"])
        stream = await self.manager.create(config)
        await stream.publish("test.1")
        await stream.publish("test.2")
        await stream.publish("test.3")
        stream_state = await stream.state()
        assert stream_state.messages == 3
        await stream.purge(keep=1)
        stream_state = await stream.state()
        assert stream_state.messages == 1


@pytest.mark.parametrize("allow_direct", [True, False])
class TestStreamGetMsg(BaseTestStreamManager):
    @pytest_asyncio.fixture(autouse=True)
    async def setup_stream(self, allow_direct: bool):
        self.allow_direct = allow_direct
        config = StreamConfig.new(
            "test-stream",
            subjects=["test.>"],
            allow_direct=allow_direct,
        )
        self.stream = await self.manager.create(config)

    async def test_get_msg_from_stream(self):
        await self.stream.publish("test.1")
        msg = await self.stream.get_msg()
        assert msg.subject == "test.1"
        assert msg.payload == b""

    async def test_get_msg_from_stream_not_found(self):
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.get_msg()
        if self.allow_direct:
            assert exc_info.value.error == Error(
                code=404,
                description="Message Not Found",
                err_code=None,
            )
        else:
            assert exc_info.value.error == Error(
                code=404,
                description="no message found",
                err_code=10037,
            )

    async def test_get_msg_from_stream_with_payload(self):
        await self.stream.publish("test.1", payload=b"hello world")
        msg = await self.stream.get_msg()
        assert msg.subject == "test.1"
        assert msg.payload == b"hello world"

    async def test_get_msg_from_stream_with_headers(self):
        await self.stream.publish("test.1", headers={"foo": "bar"})
        msg = await self.stream.get_msg()
        assert msg.subject == "test.1"
        assert msg.payload == b""
        assert msg.headers == {
            "foo": "bar",
            "Nats-Expected-Stream": "test-stream",
        }

    async def test_get_msg_from_stream_using_sequence(self):
        await self.stream.publish("test.1")
        await self.stream.publish("test.2")
        await self.stream.publish("test.3")
        msg = await self.stream.get_msg(sequence=2)
        assert msg.subject == "test.2"
        assert msg.payload == b""
        msg = await self.stream.get_msg(sequence=3)
        assert msg.subject == "test.3"
        assert msg.payload == b""

    async def test_get_msg_from_stream_using_last_by_subject(self):
        await self.stream.publish("test.1")
        await self.stream.publish("test.2")
        await self.stream.publish("test.2", payload=b"test")
        await self.stream.publish("test.3")
        msg = await self.stream.get_msg(last_by_subject="test.2")
        assert msg.subject == "test.2"
        assert msg.payload == b"test"

    async def test_get_msg_from_stream_using_next_by_subject(self):
        await self.stream.publish("test.1")
        await self.stream.publish("test.2")
        await self.stream.publish("test.2", payload=b"test")
        await self.stream.publish("test.1", payload=b"test")
        msg = await self.stream.get_msg(next_by_subject="test.2", sequence=1)
        assert msg.subject == "test.2"
        assert msg.payload == b""
        msg = await self.stream.get_msg(next_by_subject="test.2", sequence=3)
        assert msg.subject == "test.2"
        assert msg.payload == b"test"
        msg = await self.stream.get_msg(next_by_subject="test.1", sequence=2)
        assert msg.subject == "test.1"
        assert msg.payload == b"test"


class TestStreamDeleteMsg(BaseTestStreamManager):
    @pytest_asyncio.fixture(autouse=True)
    async def setup_stream(self):
        config = StreamConfig.new(
            "test-stream",
            subjects=["test.>"],
        )
        self.stream = await self.manager.create(config)

    async def test_delete_msg_from_stream(self):
        await self.stream.publish("test.1")
        await self.stream.publish("test.2")
        await self.stream.publish("test.3")
        await self.stream.delete_msg(sequence=2)
        msg = await self.stream.get_msg(1)
        assert msg.subject == "test.1"
        assert msg.payload == b""
        msg = await self.stream.get_msg(3)
        assert msg.subject == "test.3"
        assert msg.payload == b""
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.get_msg(2)
        assert exc_info.value.error == Error(
            code=404,
            description="no message found",
            err_code=10037,
        )
        # Technically it's not related to the stream manager, but it's a good
        # place to test it.
        state = await self.stream.state()
        assert state.messages == 2

    async def test_delete_msg_from_stream_store_eof(self):
        await self.stream.publish("test.1")
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.delete_msg(sequence=2)
        assert exc_info.value.error == Error(
            code=500,
            description="stream store EOF",
            err_code=10057,
        )

    async def test_delete_msg_from_stream_already_deleted(self):
        await self.stream.publish("test.1")
        await self.stream.delete_msg(sequence=1)
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.delete_msg(sequence=1)
        assert exc_info.value.error == Error(
            code=500,
            description="no message found",
            err_code=10057,
        )

    async def test_delete_msg_with_no_erase(self):
        await self.stream.publish("test.1")
        await self.stream.delete_msg(sequence=1, no_erase=True)
        with pytest.raises(JetStreamAPIException):
            await self.stream.get_msg(1)


class TestStreamUpdate(BaseTestStreamManager):
    @pytest_asyncio.fixture(autouse=True)
    async def setup_stream(self):
        config = StreamConfig.new("test-stream", subjects=["test.>"])
        self.stream = await self.manager.create(config)
        for _ in range(50):
            await self.stream.publish("test.1")

    async def test_update_stream_subjects(self):
        await self.stream.update(subjects=["test.1.>", "test.2.>"])
        assert self.stream.config.subjects == ["test.1.>", "test.2.>"]
        updated = await self.manager.get("test-stream")
        assert updated.config.subjects == ["test.1.>", "test.2.>"]

    async def test_update_stream_retention(self):
        await self.stream.update(retention=Retention.interest)
        assert self.stream.config.retention == Retention.interest
        updated = await self.manager.get("test-stream")
        assert updated.config.retention == Retention.interest

    async def test_update_stream_max_msgs(self):
        await self.stream.update(max_msgs=100)
        assert self.stream.config.max_msgs == 100
        updated = await self.manager.get("test-stream")
        assert updated.config.max_msgs == 100

    async def test_update_stream_max_bytes(self):
        await self.stream.update(max_bytes=100)
        assert self.stream.config.max_bytes == 100
        updated = await self.manager.get("test-stream")
        assert updated.config.max_bytes == 100

    async def test_update_stream_max_age(self):
        await self.stream.update(max_age=3600_000_000_000_000)
        assert self.stream.config.max_age == 3600_000_000_000_000
        updated = await self.manager.get("test-stream")
        assert updated.config.max_age == 3600_000_000_000_000

    async def test_update_num_replicas(self):
        await self.stream.update(num_replicas=3)
        assert self.stream.config.num_replicas == 3
        updated = await self.manager.get("test-stream")
        assert updated.config.num_replicas == 3

    async def test_update_duplicate_window(self):
        await self.stream.update(duplicate_window=20_000_000_000_000)
        assert self.stream.config.duplicate_window == 20_000_000_000_000
        updated = await self.manager.get("test-stream")
        assert updated.config.duplicate_window == 20_000_000_000_000

    async def test_update_description(self):
        await self.stream.update(description="some description")
        assert self.stream.config.description == "some description"
        updated = await self.manager.get("test-stream")
        assert updated.config.description == "some description"

    async def test_update_subject_transform(self):
        await self.stream.update(
            subject_transform=SubjectTransform(
                src="test.A",
                dest="test.B",
            )
        )
        assert self.stream.config.subject_transform == SubjectTransform(
            src="test.A",
            dest="test.B",
        )
        updated = await self.manager.get("test-stream")
        assert updated.config.subject_transform == SubjectTransform(
            src="test.A",
            dest="test.B",
        )

    async def test_update_max_msgs_per_subject(self):
        await self.stream.update(max_msgs_per_subject=100)
        assert self.stream.config.max_msgs_per_subject == 100
        updated = await self.manager.get("test-stream")
        assert updated.config.max_msgs_per_subject == 100

    async def test_update_max_msg_size(self):
        await self.stream.update(max_msg_size=100)
        assert self.stream.config.max_msg_size == 100
        updated = await self.manager.get("test-stream")
        assert updated.config.max_msg_size == 100

    async def test_update_compression(self):
        await self.stream.update(compression=Compression.s2)
        assert self.stream.config.compression == Compression.s2
        updated = await self.manager.get("test-stream")
        assert updated.config.compression == Compression.s2

    async def test_update_first_seq(self):
        """NOTE: I don't have any idea what this is for."""
        await self.stream.update(first_seq=100)
        assert self.stream.config.first_seq == 100
        updated = await self.manager.get("test-stream")
        assert updated.config.first_seq == 100
        stream = await self.manager.get("test-stream")
        assert stream.config.first_seq == 100

    async def test_update_no_ack(self):
        await self.stream.update(no_ack=True)
        assert self.stream.config.no_ack is True
        updated = await self.manager.get("test-stream")
        assert updated.config.no_ack is True

    async def test_update_discard(self):
        await self.stream.update(discard=Discard.new)
        assert self.stream.config.discard is Discard.new
        updated = await self.manager.get("test-stream")
        assert updated.config.discard is Discard.new

    async def test_update_placement(self):
        await self.stream.update(placement=Placement(tags=["testing"]))
        assert self.stream.config.placement == Placement(tags=["testing"])
        updated = await self.manager.get("test-stream")
        assert updated.config.placement == Placement(tags=["testing"])

    async def test_update_stream_sources(self):
        """NOTE: I don't have any idea what this is for,
        because it does not seem to sync streams when updating
        the sources."""
        other = await self.manager.create(
            StreamConfig.new("other", subjects=["other.>"])
        )
        await other.publish("other.1")
        self.stream.config.sources = [Source("other")]
        await self.stream.update(
            sources=[Source("other")],
        )
        assert self.stream.config.sources == [Source("other")]
        updated = await self.manager.get("test-stream")
        assert updated.config.sources == [Source("other")]

    async def test_update_sealed(self):
        await self.stream.update(sealed=True)
        assert self.stream.config.sealed is True
        updated = await self.manager.get("test-stream")
        assert updated.config.sealed is True

    async def test_update_deny_delete(self):
        await self.stream.update(deny_delete=True)
        assert self.stream.config.deny_delete is True
        updated = await self.manager.get("test-stream")
        assert updated.config.deny_delete is True

    async def test_update_deny_purge(self):
        await self.stream.update(deny_purge=True)
        assert self.stream.config.deny_purge is True
        updated = await self.manager.get("test-stream")
        assert updated.config.deny_purge is True

    async def test_update_allow_rollup_hdrs(self):
        await self.stream.update(allow_rollup_hdrs=True)
        assert self.stream.config.allow_rollup_hdrs is True
        updated = await self.manager.get("test-stream")
        assert updated.config.allow_rollup_hdrs is True

    async def test_update_allow_rollup_hdrs_revert(self):
        await self.stream.update(allow_rollup_hdrs=True)
        await self.stream.update(allow_rollup_hdrs=False)
        assert self.stream.config.allow_rollup_hdrs is False
        updated = await self.manager.get("test-stream")
        assert updated.config.allow_rollup_hdrs is False

    async def test_update_allow_direct(self):
        await self.stream.update(allow_direct=True)
        assert self.stream.config.allow_direct is True
        updated = await self.manager.get("test-stream")
        assert updated.config.allow_direct is True

    async def test_update_allow_direct_revert(self):
        await self.stream.update(allow_direct=True)
        await self.stream.update(allow_direct=False)
        assert self.stream.config.allow_direct is False
        updated = await self.manager.get("test-stream")
        assert updated.config.allow_direct is False

    async def test_update_mirror_direct(self):
        await self.stream.update(mirror_direct=True)
        assert self.stream.config.mirror_direct is True
        updated = await self.manager.get("test-stream")
        assert updated.config.mirror_direct is True

    async def test_update_mirror_direct_revert(self):
        await self.stream.update(mirror_direct=True)
        await self.stream.update(mirror_direct=False)
        assert self.stream.config.mirror_direct is False
        updated = await self.manager.get("test-stream")
        assert updated.config.mirror_direct is False

    async def test_update_republish(self):
        await self.stream.update(
            republish=Republish(
                src="test.A",
                dest="other.B",
            )
        )
        assert self.stream.config.republish == Republish(
            src="test.A",
            dest="other.B",
        )
        updated = await self.manager.get("test-stream")
        assert updated.config.republish == Republish(
            src="test.A",
            dest="other.B",
        )

    async def test_update_discard_new_per_subject(self):
        await self.stream.update(
            discard=Discard.new, max_msgs_per_subject=10, discard_new_per_subject=True
        )
        assert self.stream.config.discard_new_per_subject is True
        updated = await self.manager.get("test-stream")
        assert updated.config.discard_new_per_subject is True

    async def test_update_discard_new_per_subject_revert(self):
        await self.stream.update(
            discard=Discard.new, max_msgs_per_subject=10, discard_new_per_subject=True
        )
        await self.stream.update(discard_new_per_subject=False)
        assert self.stream.config.discard_new_per_subject is False
        updated = await self.manager.get("test-stream")
        assert updated.config.discard_new_per_subject is False

    async def test_update_metadata(self):
        await self.stream.update(metadata={"foo": "bar"})
        assert self.stream.config.metadata == {"foo": "bar"}
        updated = await self.manager.get("test-stream")
        assert updated.config.metadata == {"foo": "bar"}


class TestBadStreamUpdate(BaseTestStreamManager):
    @pytest_asyncio.fixture(autouse=True)
    async def setup_stream(self):
        config = StreamConfig.new(
            "test-stream",
            subjects=["test.>"],
        )
        self.stream = await self.manager.create(config)

    async def test_bad_update_stream_max_consumers(self):
        self.stream.config.max_consumers = 10
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.update()
        assert exc_info.value.error == Error(
            code=500,
            description="stream configuration update can not change MaxConsumers",
            err_code=10052,
        )

    async def test_bad_update_stream_storage(self):
        self.stream.config.storage = Storage.memory
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.update()
        assert exc_info.value.error == Error(
            code=500,
            description="stream configuration update can not change storage type",
            err_code=10052,
        )

    async def test_bad_update_mirror(self):
        self.stream.config.mirror = Mirror(name="test")
        self.stream.config.subjects = []
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.update()
        assert exc_info.value.error == Error(
            code=400,
            description="stream mirror configuration can not be updated",
            err_code=10055,
        )

    async def test_bad_update_sealed_revert(self):
        await self.stream.update(sealed=True)
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.update(sealed=False)
        assert exc_info.value.error == Error(
            code=(500),
            description="stream configuration update can not unseal a sealed stream",
            err_code=10052,
        )

    async def test_bad_update_deny_delete_revert(self):
        await self.stream.update(deny_delete=True)
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.update(deny_delete=False)
        assert exc_info.value.error == Error(
            code=(500),
            description="stream configuration update can not cancel deny message deletes",
            err_code=10052,
        )

    async def test_bad_update_deny_purge_revert(self):
        await self.stream.update(deny_purge=True)
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.update(deny_purge=False)
        assert exc_info.value.error == Error(
            code=(500),
            description="stream configuration update can not cancel deny purge",
            err_code=10052,
        )
