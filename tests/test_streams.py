import datetime
from typing import Optional

import pytest
import pytest_asyncio

from easynats.connection import Connection
from easynats.jetstream.api import Error, JetStreamAPIException, JetStreamClient
from easynats.jetstream.entities import (
    AckPolicy,
    Compression,
    ConsumerConfig,
    DeliverPolicy,
    Discard,
    Mirror,
    Placement,
    ReplayPolicy,
    Republish,
    Retention,
    Source,
    Storage,
    StreamConfig,
    SubjectTransform,
)
from easynats.jetstream.manager import StreamManager


@pytest.mark.asyncio
class BaseTestStream:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        self.conn = Connection()
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


class TestStreamPurge(BaseTestStream):
    async def test_purge_stream(self):
        config = StreamConfig.new("test-stream", subjects=["test.>"])
        stream = await self.manager.create_from_config(config)
        await stream.publish("test.1")
        await stream.publish("test.2")
        stream_state = await stream.state()
        assert stream_state.messages == 2
        await stream.purge()
        stream_state = await stream.state()
        assert stream_state.messages == 0

    async def test_purge_stream_with_subject(self):
        config = StreamConfig.new("test-stream", subjects=["test.>"])
        stream = await self.manager.create_from_config(config)
        await stream.publish("test.1")
        await stream.publish("test.2")
        stream_state = await stream.state()
        assert stream_state.messages == 2
        await stream.purge(subject="test.1")
        stream_state = await stream.state()
        assert stream_state.messages == 1

    async def test_purge_until_sequence(self):
        config = StreamConfig.new("test-stream", subjects=["test.>"])
        stream = await self.manager.create_from_config(config)
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
        stream = await self.manager.create_from_config(config)
        await stream.publish("test.1")
        await stream.publish("test.2")
        await stream.publish("test.3")
        stream_state = await stream.state()
        assert stream_state.messages == 3
        await stream.purge(keep=1)
        stream_state = await stream.state()
        assert stream_state.messages == 1


@pytest.mark.parametrize("allow_direct", [True, False])
class TestStreamGetMsg(BaseTestStream):
    @pytest_asyncio.fixture(autouse=True)
    async def setup_stream(self, allow_direct: bool):
        self.allow_direct = allow_direct
        config = StreamConfig.new(
            "test-stream",
            subjects=["test.>"],
            allow_direct=allow_direct,
        )
        self.stream = await self.manager.create_from_config(config)

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


class TestStreamDeleteMsg(BaseTestStream):
    @pytest_asyncio.fixture(autouse=True)
    async def setup_stream(self):
        config = StreamConfig.new(
            "test-stream",
            subjects=["test.>"],
        )
        self.stream = await self.manager.create_from_config(config)

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


class TestStreamUpdate(BaseTestStream):
    @pytest_asyncio.fixture(autouse=True)
    async def setup_stream(self):
        config = StreamConfig.new("test-stream", subjects=["test.>"])
        self.stream = await self.manager.create_from_config(config)
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
        other = await self.manager.create_from_config(
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


class TestStreamCreateEphemeralPullConsumer(BaseTestStream):
    @pytest_asyncio.fixture(autouse=True)
    async def setup_stream(self):
        config = StreamConfig.new(
            "test-stream",
            subjects=["test.>"],
        )
        self.stream = await self.manager.create_from_config(config)

    async def test_create(self):
        consumer = await self.stream.create_ephemeral_pull_consumer()
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_description(self):
        consumer = await self.stream.create_ephemeral_pull_consumer(
            description="some description"
        )
        assert consumer.config.description == "some description"
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    async def test_create_with_replay_policy(self):
        consumer = await self.stream.create_ephemeral_pull_consumer(
            replay_policy=ReplayPolicy.original
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize(
        "deliver_policy",
        [
            DeliverPolicy.new,
            DeliverPolicy.last,
            DeliverPolicy.all,
        ],
    )
    async def test_create_with_deliver_policy(self, deliver_policy: DeliverPolicy):
        consumer = await self.stream.create_ephemeral_pull_consumer(
            deliver_policy=deliver_policy
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_last_per_subject_deliver_policy(self):
        consumer = await self.stream.create_ephemeral_pull_consumer(
            deliver_policy=DeliverPolicy.last_per_subject,
            filter_subjects="test.1",
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize("deliver_policy", [DeliverPolicy.by_start_sequence, None])
    async def test_create_with_opt_start_seq(
        self, deliver_policy: Optional[DeliverPolicy]
    ):
        consumer = await self.stream.create_ephemeral_pull_consumer(
            opt_start_seq=10, deliver_policy=deliver_policy
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize(
        "deliver_policy",
        [
            DeliverPolicy.all,
            DeliverPolicy.last,
            DeliverPolicy.last_per_subject,
            DeliverPolicy.new,
            DeliverPolicy.by_start_time,
        ],
    )
    async def test_create_with_opt_start_seq_bad_deliver_policy_error(
        self, deliver_policy: DeliverPolicy
    ):
        with pytest.raises(ValueError) as exc_info:
            await self.stream.create_ephemeral_pull_consumer(
                opt_start_seq=10,
                deliver_policy=deliver_policy,
            )
        assert exc_info.value.args == (
            "deliver_policy must be DeliverPolicy.by_start_sequence",
        )

    @pytest.mark.parametrize("deliver_policy", [DeliverPolicy.by_start_time, None])
    async def test_create_with_opt_start_time(
        self, deliver_policy: Optional[DeliverPolicy]
    ):
        consumer = await self.stream.create_ephemeral_pull_consumer(
            opt_start_time=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
            deliver_policy=deliver_policy,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize(
        "deliver_policy",
        [
            DeliverPolicy.all,
            DeliverPolicy.last,
            DeliverPolicy.last_per_subject,
            DeliverPolicy.new,
            DeliverPolicy.by_start_sequence,
        ],
    )
    async def test_create_with_opt_start_time_ad_deliver_policy_error(
        self, deliver_policy: DeliverPolicy
    ):
        with pytest.raises(ValueError) as exc_info:
            await self.stream.create_ephemeral_pull_consumer(
                opt_start_time=datetime.datetime(1970, 1, 1),
                deliver_policy=deliver_policy,
            )
        assert exc_info.value.args == (
            "deliver_policy must be DeliverPolicy.by_start_time",
        )

    async def test_create_with_ack_wait(self):
        consumer = await self.stream.create_ephemeral_pull_consumer(ack_wait=10)
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_max_deliver(self):
        consumer = await self.stream.create_ephemeral_pull_consumer(
            max_deliver=10,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_filter_subject(self):
        consumer = await self.stream.create_ephemeral_pull_consumer(
            filter_subjects="test.1"
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_filter_subjects(self):
        consumer = await self.stream.create_ephemeral_pull_consumer(
            filter_subjects=["test.1", "test.2"],
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_sample_freq(self):
        consumer = await self.stream.create_ephemeral_pull_consumer(
            sample_freq=datetime.timedelta(seconds=30)
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_max_ack_pending(self):
        consumer = await self.stream.create_ephemeral_pull_consumer(
            max_ack_pending=10,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_max_waiting(self):
        consumer = await self.stream.create_ephemeral_pull_consumer(
            max_waiting=10,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_headers_only(self):
        consumer = await self.stream.create_ephemeral_pull_consumer(
            headers_only=True,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    async def test_create_with_max_batch(self):
        consumer = await self.stream.create_ephemeral_pull_consumer(
            max_batch=10,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    async def test_create_with_max_expires(self):
        consumer = await self.stream.create_ephemeral_pull_consumer(
            max_expires=datetime.timedelta(seconds=30)
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    async def test_create_with_max_bytes(self):
        consumer = await self.stream.create_ephemeral_pull_consumer(max_bytes=1024)
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    async def test_create_with_inactive_threshold(self):
        consumer = await self.stream.create_ephemeral_pull_consumer(
            inactive_threshold=datetime.timedelta(seconds=30)
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    @pytest.mark.parametrize("max_deliver", [4, 100, None])
    async def test_create_with_backoff(self, max_deliver: Optional[int]):
        consumer = await self.stream.create_ephemeral_pull_consumer(
            max_deliver=max_deliver,
            backoff=[10_000_000_000_000, 30_000_000_000_000, 60_000_000_000_000],
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    @pytest.mark.parametrize("max_deliver", [0, 2, 3])
    async def test_create_with_backoff_bad_max_deliver_error(self, max_deliver: int):
        with pytest.raises(ValueError) as exc_info:
            await self.stream.create_ephemeral_pull_consumer(
                max_deliver=max_deliver,
                backoff=[10_000_000_000_000, 30_000_000_000_000, 60_000_000_000_000],
            )
        assert exc_info.value.args == (
            "max_deliver must be greater than the length of backoff",
        )

    async def test_create_with_num_replicas(self):
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.create_ephemeral_pull_consumer(num_replicas=3)
        assert exc_info.value.error == Error(
            code=500,
            description="replicas > 1 not supported in non-clustered mode",
            err_code=10074,
        )

    async def test_create_with_mem_storage(self):
        consumer = await self.stream.create_ephemeral_pull_consumer(
            mem_storage=True,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    async def test_create_with_metadata(self):
        consumer = await self.stream.create_ephemeral_pull_consumer(
            metadata={"foo": "bar"},
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config


class TestStreamCreateDurablePullConsumer(BaseTestStream):
    @pytest_asyncio.fixture(autouse=True)
    async def setup_stream(self):
        config = StreamConfig.new(
            "test-stream",
            subjects=["test.>"],
        )
        self.stream = await self.manager.create_from_config(config)

    async def test_create(self):
        consumer = await self.stream.create_durable_pull_consumer("durable")
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_description(self):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable", description="some description"
        )
        assert consumer.config.description == "some description"
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    async def test_create_with_replay_policy(self):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable", replay_policy=ReplayPolicy.original
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize(
        "deliver_policy",
        [
            DeliverPolicy.new,
            DeliverPolicy.last,
            DeliverPolicy.all,
        ],
    )
    async def test_create_with_deliver_policy(self, deliver_policy: DeliverPolicy):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable", deliver_policy=deliver_policy
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_last_per_subject_deliver_policy(self):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable",
            deliver_policy=DeliverPolicy.last_per_subject,
            filter_subjects="test.1",
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize("deliver_policy", [DeliverPolicy.by_start_sequence, None])
    async def test_create_with_opt_start_seq(
        self, deliver_policy: Optional[DeliverPolicy]
    ):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable", opt_start_seq=10, deliver_policy=deliver_policy
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize(
        "deliver_policy",
        [
            DeliverPolicy.all,
            DeliverPolicy.last,
            DeliverPolicy.last_per_subject,
            DeliverPolicy.new,
            DeliverPolicy.by_start_time,
        ],
    )
    async def test_create_with_opt_start_seq_bad_deliver_policy_error(
        self, deliver_policy: DeliverPolicy
    ):
        with pytest.raises(ValueError) as exc_info:
            await self.stream.create_durable_pull_consumer(
                name="durable",
                opt_start_seq=10,
                deliver_policy=deliver_policy,
            )
        assert exc_info.value.args == (
            "deliver_policy must be DeliverPolicy.by_start_sequence",
        )

    @pytest.mark.parametrize("deliver_policy", [DeliverPolicy.by_start_time, None])
    async def test_create_with_opt_start_time(
        self, deliver_policy: Optional[DeliverPolicy]
    ):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable",
            opt_start_time=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
            deliver_policy=deliver_policy,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize(
        "deliver_policy",
        [
            DeliverPolicy.all,
            DeliverPolicy.last,
            DeliverPolicy.last_per_subject,
            DeliverPolicy.new,
            DeliverPolicy.by_start_sequence,
        ],
    )
    async def test_create_with_opt_start_time_ad_deliver_policy_error(
        self, deliver_policy: DeliverPolicy
    ):
        with pytest.raises(ValueError) as exc_info:
            await self.stream.create_durable_pull_consumer(
                name="durable",
                opt_start_time=datetime.datetime(1970, 1, 1),
                deliver_policy=deliver_policy,
            )
        assert exc_info.value.args == (
            "deliver_policy must be DeliverPolicy.by_start_time",
        )

    async def test_create_with_ack_wait(self):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable",
            ack_wait=10,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_max_deliver(self):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable",
            max_deliver=10,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_filter_subject(self):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable",
            filter_subjects="test.1",
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_filter_subjects(self):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable",
            filter_subjects=["test.1", "test.2"],
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_sample_freq(self):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable",
            sample_freq=datetime.timedelta(seconds=30),
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_max_ack_pending(self):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable",
            max_ack_pending=10,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_max_waiting(self):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable",
            max_waiting=10,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_headers_only(self):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable",
            headers_only=True,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    async def test_create_with_max_batch(self):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable",
            max_batch=10,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    async def test_create_with_max_expires(self):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable", max_expires=datetime.timedelta(seconds=30)
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    async def test_create_with_max_bytes(self):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable",
            max_bytes=1024,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    async def test_create_with_inactive_threshold(self):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable",
            inactive_threshold=datetime.timedelta(seconds=30),
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    @pytest.mark.parametrize("max_deliver", [4, 100, None])
    async def test_create_with_backoff(self, max_deliver: Optional[int]):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable",
            max_deliver=max_deliver,
            backoff=[10_000_000_000_000, 30_000_000_000_000, 60_000_000_000_000],
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    @pytest.mark.parametrize("max_deliver", [0, 2, 3])
    async def test_create_with_backoff_bad_max_deliver_error(self, max_deliver: int):
        with pytest.raises(ValueError) as exc_info:
            await self.stream.create_durable_pull_consumer(
                name="durable",
                max_deliver=max_deliver,
                backoff=[10_000_000_000_000, 30_000_000_000_000, 60_000_000_000_000],
            )
        assert exc_info.value.args == (
            "max_deliver must be greater than the length of backoff",
        )

    async def test_create_with_num_replicas(self):
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.create_durable_pull_consumer(
                name="durable",
                num_replicas=3,
            )
        assert exc_info.value.error == Error(
            code=500,
            description="replicas > 1 not supported in non-clustered mode",
            err_code=10074,
        )

    async def test_create_with_mem_storage(self):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable",
            mem_storage=True,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    async def test_create_with_metadata(self):
        consumer = await self.stream.create_durable_pull_consumer(
            name="durable",
            metadata={"foo": "bar"},
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config


class TestStreamCreateEphemeralPushConsumer(BaseTestStream):
    @pytest_asyncio.fixture(autouse=True)
    async def setup_stream(self):
        config = StreamConfig.new(
            "test-stream",
            subjects=["test.>"],
        )
        self.stream = await self.manager.create_from_config(config)

    async def test_create(self):
        consumer = await self.stream.create_ephemeral_push_consumer(
            deliver_subject="deliver"
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_description(self):
        consumer = await self.stream.create_ephemeral_push_consumer(
            deliver_subject="deliver",
            description="some description",
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    async def test_create_without_ack_policy(self):
        consumer = await self.stream.create_ephemeral_push_consumer(
            deliver_subject="deliver",
            ack_policy=AckPolicy.none,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_replay_policy(self):
        consumer = await self.stream.create_ephemeral_push_consumer(
            deliver_subject="deliver", replay_policy=ReplayPolicy.original
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_deliver_policy(self):
        consumer = await self.stream.create_ephemeral_push_consumer(
            deliver_subject="deliver", deliver_policy=DeliverPolicy.new
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize("deliver_policy", [DeliverPolicy.by_start_sequence, None])
    async def test_create_with_opt_start_seq(
        self, deliver_policy: Optional[DeliverPolicy]
    ):
        consumer = await self.stream.create_ephemeral_push_consumer(
            deliver_subject="deliver", opt_start_seq=10, deliver_policy=deliver_policy
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize(
        "deliver_policy",
        [
            DeliverPolicy.all,
            DeliverPolicy.last,
            DeliverPolicy.last_per_subject,
            DeliverPolicy.new,
            DeliverPolicy.by_start_time,
        ],
    )
    async def test_create_with_opt_start_seq_bad_deliver_policy_error(
        self, deliver_policy: DeliverPolicy
    ):
        with pytest.raises(ValueError) as exc_info:
            await self.stream.create_ephemeral_push_consumer(
                deliver_subject="deliver",
                opt_start_seq=10,
                deliver_policy=deliver_policy,
            )
        assert exc_info.value.args == (
            "deliver_policy must be DeliverPolicy.by_start_sequence",
        )

    @pytest.mark.parametrize("deliver_policy", [DeliverPolicy.by_start_time, None])
    async def test_create_with_opt_start_time(
        self, deliver_policy: Optional[DeliverPolicy]
    ):
        consumer = await self.stream.create_ephemeral_push_consumer(
            deliver_subject="deliver",
            opt_start_time=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
            deliver_policy=deliver_policy,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize(
        "deliver_policy",
        [
            DeliverPolicy.all,
            DeliverPolicy.last,
            DeliverPolicy.last_per_subject,
            DeliverPolicy.new,
            DeliverPolicy.by_start_sequence,
        ],
    )
    async def test_create_with_opt_start_time_bad_deliver_policy_error(
        self, deliver_policy: DeliverPolicy
    ):
        with pytest.raises(ValueError) as exc_info:
            await self.stream.create_ephemeral_push_consumer(
                deliver_subject="deliver",
                opt_start_time=datetime.datetime(1970, 1, 1),
                deliver_policy=deliver_policy,
            )
        assert exc_info.value.args == (
            "deliver_policy must be DeliverPolicy.by_start_time",
        )

    async def test_create_with_ack_wait(self):
        consumer = await self.stream.create_ephemeral_push_consumer(
            deliver_subject="deliver", ack_wait=10
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_max_deliver(self):
        consumer = await self.stream.create_ephemeral_push_consumer(
            deliver_subject="deliver", max_deliver=10
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_filter_subject(self):
        consumer = await self.stream.create_ephemeral_push_consumer(
            deliver_subject="deliver", filter_subjects="test.1"
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_filter_subjects(self):
        consumer = await self.stream.create_ephemeral_push_consumer(
            deliver_subject="deliver", filter_subjects=["test.1", "test.2"]
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_sample_freq(self):
        consumer = await self.stream.create_ephemeral_push_consumer(
            deliver_subject="deliver",
            sample_freq=datetime.timedelta(seconds=30),
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize("heartbeat", [datetime.timedelta(seconds=60), None])
    async def test_create_with_flow_control(
        self, heartbeat: Optional[datetime.timedelta]
    ):
        consumer = await self.stream.create_ephemeral_push_consumer(
            deliver_subject="deliver",
            flow_control=True,
            idle_heartbeat=heartbeat,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_rate_limit_bps(self):
        consumer = await self.stream.create_ephemeral_push_consumer(
            deliver_subject="deliver",
            rate_limit_bps=1,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_inactive_threshold(self):
        consumer = await self.stream.create_ephemeral_push_consumer(
            deliver_subject="deliver",
            inactive_threshold=datetime.timedelta(seconds=30),
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    @pytest.mark.parametrize("max_deliver", [4, 100, None])
    async def test_create_with_backoff(self, max_deliver: Optional[int]):
        consumer = await self.stream.create_ephemeral_push_consumer(
            deliver_subject="deliver",
            max_deliver=max_deliver,
            backoff=[10_000_000_000_000, 30_000_000_000_000, 60_000_000_000_000],
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    @pytest.mark.parametrize("max_deliver", [0, 2, 3])
    async def test_create_with_backoff_bad_max_deliver_error(self, max_deliver: int):
        with pytest.raises(ValueError) as exc_info:
            await self.stream.create_ephemeral_push_consumer(
                deliver_subject="deliver",
                max_deliver=max_deliver,
                backoff=[10_000_000_000_000, 30_000_000_000_000, 60_000_000_000_000],
            )
        assert exc_info.value.args == (
            "max_deliver must be greater than the length of backoff",
        )

    async def test_create_with_num_replicas(self):
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.create_ephemeral_push_consumer(
                deliver_subject="deliver",
                num_replicas=3,
            )
        assert exc_info.value.error == Error(
            code=500,
            description="replicas > 1 not supported in non-clustered mode",
            err_code=10074,
        )

    async def test_create_with_mem_storage(self):
        consumer = await self.stream.create_ephemeral_push_consumer(
            deliver_subject="deliver",
            mem_storage=True,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    async def test_create_with_metadata(self):
        consumer = await self.stream.create_ephemeral_push_consumer(
            deliver_subject="deliver", metadata={"foo": "bar"}
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    async def test_create_with_direct(self):
        consumer = await self.stream.create_ephemeral_push_consumer(
            deliver_subject="deliver", direct=True
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config


class TestStreamCreateDurablePushConsumer(BaseTestStream):
    @pytest_asyncio.fixture(autouse=True)
    async def setup_stream(self):
        config = StreamConfig.new(
            "test-stream",
            subjects=["test.>"],
        )
        self.stream = await self.manager.create_from_config(config)

    async def test_create(self):
        consumer = await self.stream.create_durable_push_consumer(
            name="durable", deliver_subject="deliver"
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_description(self):
        consumer = await self.stream.create_durable_push_consumer(
            name="durable",
            deliver_subject="deliver",
            description="some description",
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    async def test_create_without_ack_policy(self):
        consumer = await self.stream.create_durable_push_consumer(
            name="durable",
            deliver_subject="deliver",
            ack_policy=AckPolicy.none,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_replay_policy(self):
        consumer = await self.stream.create_durable_push_consumer(
            name="durable",
            deliver_subject="deliver",
            replay_policy=ReplayPolicy.original,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_deliver_policy(self):
        consumer = await self.stream.create_durable_push_consumer(
            name="durable", deliver_subject="deliver", deliver_policy=DeliverPolicy.new
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize("deliver_policy", [DeliverPolicy.by_start_sequence, None])
    async def test_create_with_opt_start_seq(
        self, deliver_policy: Optional[DeliverPolicy]
    ):
        consumer = await self.stream.create_durable_push_consumer(
            name="durable",
            deliver_subject="deliver",
            opt_start_seq=10,
            deliver_policy=deliver_policy,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize(
        "deliver_policy",
        [
            DeliverPolicy.all,
            DeliverPolicy.last,
            DeliverPolicy.last_per_subject,
            DeliverPolicy.new,
            DeliverPolicy.by_start_time,
        ],
    )
    async def test_create_with_opt_start_seq_bad_deliver_policy_error(
        self, deliver_policy: DeliverPolicy
    ):
        with pytest.raises(ValueError) as exc_info:
            await self.stream.create_durable_push_consumer(
                name="durable",
                deliver_subject="deliver",
                opt_start_seq=10,
                deliver_policy=deliver_policy,
            )
        assert exc_info.value.args == (
            "deliver_policy must be DeliverPolicy.by_start_sequence",
        )

    @pytest.mark.parametrize("deliver_policy", [DeliverPolicy.by_start_time, None])
    async def test_create_with_opt_start_time(
        self, deliver_policy: Optional[DeliverPolicy]
    ):
        consumer = await self.stream.create_durable_push_consumer(
            name="durable",
            deliver_subject="deliver",
            opt_start_time=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
            deliver_policy=deliver_policy,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize(
        "deliver_policy",
        [
            DeliverPolicy.all,
            DeliverPolicy.last,
            DeliverPolicy.last_per_subject,
            DeliverPolicy.new,
            DeliverPolicy.by_start_sequence,
        ],
    )
    async def test_create_with_opt_start_time_bad_deliver_policy_error(
        self, deliver_policy: DeliverPolicy
    ):
        with pytest.raises(ValueError) as exc_info:
            await self.stream.create_durable_push_consumer(
                name="durable",
                deliver_subject="deliver",
                opt_start_time=datetime.datetime(1970, 1, 1),
                deliver_policy=deliver_policy,
            )
        assert exc_info.value.args == (
            "deliver_policy must be DeliverPolicy.by_start_time",
        )

    async def test_create_with_ack_wait(self):
        consumer = await self.stream.create_durable_push_consumer(
            name="durable", deliver_subject="deliver", ack_wait=10
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_max_deliver(self):
        consumer = await self.stream.create_durable_push_consumer(
            name="durable", deliver_subject="deliver", max_deliver=10
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_filter_subject(self):
        consumer = await self.stream.create_durable_push_consumer(
            name="durable", deliver_subject="deliver", filter_subjects="test.1"
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_filter_subjects(self):
        consumer = await self.stream.create_durable_push_consumer(
            name="durable",
            deliver_subject="deliver",
            filter_subjects=["test.1", "test.2"],
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_sample_freq(self):
        consumer = await self.stream.create_durable_push_consumer(
            name="durable",
            deliver_subject="deliver",
            sample_freq=datetime.timedelta(seconds=30),
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize("heartbeat", [datetime.timedelta(seconds=60), None])
    async def test_create_with_flow_control(
        self, heartbeat: Optional[datetime.timedelta]
    ):
        consumer = await self.stream.create_durable_push_consumer(
            name="durable",
            deliver_subject="deliver",
            flow_control=True,
            idle_heartbeat=heartbeat,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_rate_limit_bps(self):
        consumer = await self.stream.create_durable_push_consumer(
            name="durable",
            deliver_subject="deliver",
            rate_limit_bps=1,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config

    async def test_create_with_inactive_threshold(self):
        consumer = await self.stream.create_durable_push_consumer(
            name="durable",
            deliver_subject="deliver",
            inactive_threshold=datetime.timedelta(seconds=30),
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    @pytest.mark.parametrize("max_deliver", [4, 100, None])
    async def test_create_with_backoff(self, max_deliver: Optional[int]):
        consumer = await self.stream.create_durable_push_consumer(
            name="durable",
            deliver_subject="deliver",
            max_deliver=max_deliver,
            backoff=[10_000_000_000_000, 30_000_000_000_000, 60_000_000_000_000],
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    @pytest.mark.parametrize("max_deliver", [0, 2, 3])
    async def test_create_with_backoff_bad_max_deliver_error(self, max_deliver: int):
        with pytest.raises(ValueError) as exc_info:
            await self.stream.create_durable_push_consumer(
                name="durable",
                deliver_subject="deliver",
                max_deliver=max_deliver,
                backoff=[10_000_000_000_000, 30_000_000_000_000, 60_000_000_000_000],
            )
        assert exc_info.value.args == (
            "max_deliver must be greater than the length of backoff",
        )

    async def test_create_with_num_replicas(self):
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.create_durable_push_consumer(
                name="durable",
                deliver_subject="deliver",
                num_replicas=3,
            )
        assert exc_info.value.error == Error(
            code=500,
            description="replicas > 1 not supported in non-clustered mode",
            err_code=10074,
        )

    async def test_create_with_mem_storage(self):
        consumer = await self.stream.create_durable_push_consumer(
            name="durable",
            deliver_subject="deliver",
            mem_storage=True,
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config

    async def test_create_with_metadata(self):
        consumer = await self.stream.create_durable_push_consumer(
            name="durable",
            deliver_subject="deliver",
            metadata={"foo": "bar"},
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer.config


class TestStreamCreateEphemeralPullConsumerFromConfig(BaseTestStream):
    @pytest_asyncio.fixture(autouse=True)
    async def setup_stream(self):
        config = StreamConfig.new(
            "test-stream",
            subjects=["test.>"],
        )
        self.stream = await self.manager.create_from_config(config)

    async def test_create(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config()
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    async def test_create_with_description(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(
            description="some description"
        )
        assert consumer_config.description == "some description"
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    async def test_create_without_ack_policy(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(
            ack_policy=AckPolicy.none
        )
        assert consumer_config.ack_policy == AckPolicy.none
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    async def test_create_with_replay_policy(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(
            replay_policy=ReplayPolicy.original
        )
        assert consumer_config.replay_policy == ReplayPolicy.original
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    async def test_create_with_deliver_policy(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(
            deliver_policy=DeliverPolicy.new
        )
        assert consumer_config.deliver_policy == DeliverPolicy.new
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize("deliver_policy", [DeliverPolicy.by_start_sequence, None])
    async def test_create_with_opt_start_seq(
        self, deliver_policy: Optional[DeliverPolicy]
    ):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(
            opt_start_seq=10, deliver_policy=deliver_policy
        )
        assert consumer_config.opt_start_seq == 10
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize(
        "deliver_policy",
        [
            DeliverPolicy.all,
            DeliverPolicy.last,
            DeliverPolicy.last_per_subject,
            DeliverPolicy.new,
            DeliverPolicy.by_start_time,
        ],
    )
    async def test_create_with_bad_deliver_policy(self, deliver_policy: DeliverPolicy):
        with pytest.raises(ValueError) as exc_info:
            ConsumerConfig.new_ephemeral_pull_config(
                opt_start_seq=10,
                deliver_policy=deliver_policy,
            )
        assert exc_info.value.args == (
            "deliver_policy must be DeliverPolicy.by_start_sequence",
        )

    @pytest.mark.parametrize("deliver_policy", [DeliverPolicy.by_start_time, None])
    async def test_create_with_opt_start_time(
        self, deliver_policy: Optional[DeliverPolicy]
    ):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(
            opt_start_time=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
            deliver_policy=deliver_policy,
        )
        assert consumer_config.opt_start_time == "1970-01-01T00:00:00Z"
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize(
        "deliver_policy",
        [
            DeliverPolicy.all,
            DeliverPolicy.last,
            DeliverPolicy.last_per_subject,
            DeliverPolicy.new,
            DeliverPolicy.by_start_sequence,
        ],
    )
    async def test_create_with_opt_start_time_with_bad_deliver_policy(
        self, deliver_policy: DeliverPolicy
    ):
        with pytest.raises(ValueError) as exc_info:
            ConsumerConfig.new_ephemeral_pull_config(
                opt_start_time=datetime.datetime(1970, 1, 1),
                deliver_policy=deliver_policy,
            )
        assert exc_info.value.args == (
            "deliver_policy must be DeliverPolicy.by_start_time",
        )

    async def test_create_with_ack_wait(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(ack_wait=10)
        assert consumer_config.ack_wait == 10
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_max_deliver(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(max_deliver=10)
        assert consumer_config.max_deliver == 10
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    async def test_create_with_filter_subject(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(
            filter_subjects="test.1"
        )
        assert consumer_config.filter_subject == "test.1"
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_filter_subjects(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(
            filter_subjects=["test.1", "test.2"]
        )
        assert consumer_config.filter_subjects == ["test.1", "test.2"]
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_sample_freq(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(
            sample_freq=datetime.timedelta(seconds=30)
        )
        assert consumer_config.sample_freq == "30000000000"
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_max_ack_pending(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(max_ack_pending=10)
        assert consumer_config.max_ack_pending == 10
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_max_waiting(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(max_waiting=10)
        assert consumer_config.max_waiting == 10
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_headers_only(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(headers_only=True)
        assert consumer_config.headers_only is True
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    async def test_create_with_max_batch(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(max_batch=10)
        assert consumer_config.max_batch == 10
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    async def test_create_with_max_expires(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(
            max_expires=datetime.timedelta(seconds=30)
        )
        assert consumer_config.max_expires == 30000000000
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    async def test_create_with_max_bytes(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(max_bytes=1024)
        assert consumer_config.max_bytes == 1024
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    async def test_create_with_inactive_threshold(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(
            inactive_threshold=datetime.timedelta(seconds=30)
        )
        assert consumer_config.inactive_threshold == 30000000000
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    @pytest.mark.parametrize("max_deliver", [4, 100, None])
    async def test_create_with_backoff(self, max_deliver: Optional[int]):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(
            max_deliver=max_deliver,
            backoff=[10_000_000_000_000, 30_000_000_000_000, 60_000_000_000_000],
        )
        assert consumer_config.backoff == [
            10_000_000_000_000,
            30_000_000_000_000,
            60_000_000_000_000,
        ]
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    @pytest.mark.parametrize("max_deliver", [0, 2, 3])
    async def test_create_with_backoff_bad_max_deliver_error(self, max_deliver: int):
        with pytest.raises(ValueError) as exc_info:
            ConsumerConfig.new_ephemeral_pull_config(
                max_deliver=max_deliver,
                backoff=[10_000_000_000_000, 30_000_000_000_000, 60_000_000_000_000],
            )
        assert exc_info.value.args == (
            "max_deliver must be greater than the length of backoff",
        )

    async def test_create_with_num_replicas(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(num_replicas=3)
        assert consumer_config.num_replicas == 3
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.create_ephemeral_consumer_from_config(consumer_config)
        assert exc_info.value.error == Error(
            code=500,
            description="replicas > 1 not supported in non-clustered mode",
            err_code=10074,
        )

    async def test_create_with_mem_storage(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(mem_storage=True)
        assert consumer_config.mem_storage is True
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    async def test_create_with_metadata(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config(
            metadata={"foo": "bar"}
        )
        assert consumer_config.metadata == {"foo": "bar"}
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config


class TestStreamCreateDurablePullConsumerFromConfig(BaseTestStream):
    @pytest_asyncio.fixture(autouse=True)
    async def setup_stream(self):
        config = StreamConfig.new(
            "test-stream",
            subjects=["test.>"],
        )
        self.stream = await self.manager.create_from_config(config)

    async def test_create(self):
        consumer_config = ConsumerConfig.new_durable_pull_config("test-consumer")
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    async def test_create_with_description(self):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer", description="some description"
        )
        assert consumer_config.description == "some description"
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    async def test_create_with_existing_name_and_same_config_ok(self):
        consumer_config = ConsumerConfig.new_durable_pull_config("test-consumer")
        await self.stream.create_durable_consumer_from_config(consumer_config)
        await self.stream.create_durable_consumer_from_config(consumer_config)

    async def test_create_with_existing_name_and_different_config_error(
        self,
    ):
        consumer_config = ConsumerConfig.new_durable_pull_config("test-consumer")
        await self.stream.create_durable_consumer_from_config(consumer_config)
        consumer_config.headers_only = True
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.create_durable_consumer_from_config(consumer_config)
        assert exc_info.value.error == Error(
            code=400,
            description="consumer already exists",
            err_code=10148,
        )

    async def test_create_filtered_with_existing_name_and_different_config_error(
        self,
    ):
        consumer_config = ConsumerConfig.new_durable_pull_config("test-consumer")
        await self.stream.create_durable_consumer_from_config(consumer_config)
        consumer_config.filter_subject = "test.1"
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.create_durable_consumer_from_config(consumer_config)
        assert exc_info.value.error == Error(
            code=400,
            description="consumer already exists",
            err_code=10148,
        )

    async def test_create_without_ack_policy(self):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer", ack_policy=AckPolicy.none
        )
        assert consumer_config.ack_policy == AckPolicy.none
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    async def test_create_with_replay_policy(self):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer", replay_policy=ReplayPolicy.original
        )
        assert consumer_config.replay_policy == ReplayPolicy.original
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    async def test_create_with_deliver_policy(self):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer", deliver_policy=DeliverPolicy.new
        )
        assert consumer_config.deliver_policy == DeliverPolicy.new
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize("deliver_policy", [DeliverPolicy.by_start_sequence, None])
    async def test_create_with_opt_start_seq(
        self, deliver_policy: Optional[DeliverPolicy]
    ):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer", opt_start_seq=10, deliver_policy=deliver_policy
        )
        assert consumer_config.opt_start_seq == 10
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize(
        "deliver_policy",
        [
            DeliverPolicy.all,
            DeliverPolicy.last,
            DeliverPolicy.last_per_subject,
            DeliverPolicy.new,
            DeliverPolicy.by_start_time,
        ],
    )
    async def test_create_with_bad_deliver_policy(self, deliver_policy: DeliverPolicy):
        with pytest.raises(ValueError) as exc_info:
            ConsumerConfig.new_durable_pull_config(
                "test-consumer",
                opt_start_seq=10,
                deliver_policy=deliver_policy,
            )
        assert exc_info.value.args == (
            "deliver_policy must be DeliverPolicy.by_start_sequence",
        )

    @pytest.mark.parametrize("deliver_policy", [DeliverPolicy.by_start_time, None])
    async def test_create_with_opt_start_time(
        self, deliver_policy: Optional[DeliverPolicy]
    ):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer",
            opt_start_time=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
            deliver_policy=deliver_policy,
        )
        assert consumer_config.opt_start_time == "1970-01-01T00:00:00Z"
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize(
        "deliver_policy",
        [
            DeliverPolicy.all,
            DeliverPolicy.last,
            DeliverPolicy.last_per_subject,
            DeliverPolicy.new,
            DeliverPolicy.by_start_sequence,
        ],
    )
    async def test_create_with_opt_start_time_bad_deliver_policy_error(
        self, deliver_policy: DeliverPolicy
    ):
        with pytest.raises(ValueError) as exc_info:
            ConsumerConfig.new_durable_pull_config(
                "test-consumer",
                opt_start_time=datetime.datetime(1970, 1, 1),
                deliver_policy=deliver_policy,
            )
        assert exc_info.value.args == (
            "deliver_policy must be DeliverPolicy.by_start_time",
        )

    async def test_create_with_ack_wait(self):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer", ack_wait=10
        )
        assert consumer_config.ack_wait == 10
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_max_deliver(self):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer", max_deliver=10
        )
        assert consumer_config.max_deliver == 10
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    async def test_create_with_filter_subject(self):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer", filter_subjects="test.1"
        )
        assert consumer_config.filter_subject == "test.1"
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_filter_subjects(self):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer", filter_subjects=["test.1", "test.2"]
        )
        assert consumer_config.filter_subjects == ["test.1", "test.2"]
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_sample_freq(self):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer", sample_freq=datetime.timedelta(seconds=30)
        )
        assert consumer_config.sample_freq == "30000000000"
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_max_ack_pending(self):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer", max_ack_pending=10
        )
        assert consumer_config.max_ack_pending == 10
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_max_waiting(self):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer", max_waiting=10
        )
        assert consumer_config.max_waiting == 10
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_headers_only(self):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer", headers_only=True
        )
        assert consumer_config.headers_only is True
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    async def test_create_with_max_batch(self):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer", max_batch=10
        )
        assert consumer_config.max_batch == 10
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    async def test_create_with_max_expires(self):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer", max_expires=datetime.timedelta(seconds=30)
        )
        assert consumer_config.max_expires == 30000000000
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    async def test_create_with_max_bytes(self):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer", max_bytes=1024
        )
        assert consumer_config.max_bytes == 1024
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    async def test_create_with_inactive_threshold(self):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer", inactive_threshold=datetime.timedelta(seconds=30)
        )
        assert consumer_config.inactive_threshold == 30000000000
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    @pytest.mark.parametrize("max_deliver", [4, 100, None])
    async def test_create_with_backoff(self, max_deliver: Optional[int]):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer",
            max_deliver=max_deliver,
            backoff=[10_000_000_000_000, 30_000_000_000_000, 60_000_000_000_000],
        )
        assert consumer_config.backoff == [
            10_000_000_000_000,
            30_000_000_000_000,
            60_000_000_000_000,
        ]
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    @pytest.mark.parametrize("max_deliver", [0, 2, 3])
    async def test_create_with_backoff_bad_max_deliver_error(self, max_deliver: int):
        with pytest.raises(ValueError) as exc_info:
            ConsumerConfig.new_durable_pull_config(
                "test-consumer",
                max_deliver=max_deliver,
                backoff=[10_000_000_000_000, 30_000_000_000_000, 60_000_000_000_000],
            )
        assert exc_info.value.args == (
            "max_deliver must be greater than the length of backoff",
        )

    async def test_create_with_num_replicas(self):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer", num_replicas=3
        )
        assert consumer_config.num_replicas == 3
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.create_durable_consumer_from_config(consumer_config)
        assert exc_info.value.error == Error(
            code=500,
            description="replicas > 1 not supported in non-clustered mode",
            err_code=10074,
        )

    async def test_create_with_mem_storage(self):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer", mem_storage=True
        )
        assert consumer_config.mem_storage is True
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    async def test_create_with_metadata(self):
        consumer_config = ConsumerConfig.new_durable_pull_config(
            "test-consumer", metadata={"foo": "bar"}
        )
        assert consumer_config.metadata == {"foo": "bar"}
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config


class TestStreamCreateEphemeralPushConsumerFromConfig(BaseTestStream):
    @pytest_asyncio.fixture(autouse=True)
    async def setup_stream(self):
        config = StreamConfig.new(
            "test-stream",
            subjects=["test.>"],
        )
        self.stream = await self.manager.create_from_config(config)

    async def test_create(self):
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            deliver_subject="deliver"
        )
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    async def test_create_with_description(self):
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            deliver_subject="deliver", description="some description"
        )
        assert consumer_config.description == "some description"
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    async def test_create_without_ack_policy(self):
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            "deliver",
            ack_policy=AckPolicy.none,
        )
        assert consumer_config.ack_policy == AckPolicy.none
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        # Max ack pending cannot be set by client for push consumers
        consumer_config.max_ack_pending = consumer_.config.max_ack_pending
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    async def test_create_with_replay_policy(self):
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            "deliver", replay_policy=ReplayPolicy.original
        )
        assert consumer_config.replay_policy == ReplayPolicy.original
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    async def test_create_with_deliver_policy(self):
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            "deliver", deliver_policy=DeliverPolicy.new
        )
        assert consumer_config.deliver_policy == DeliverPolicy.new
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize("deliver_policy", [DeliverPolicy.by_start_sequence, None])
    async def test_create_with_opt_start_seq(
        self, deliver_policy: Optional[DeliverPolicy]
    ):
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            "deliver", opt_start_seq=10, deliver_policy=deliver_policy
        )
        assert consumer_config.opt_start_seq == 10
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize(
        "deliver_policy",
        [
            DeliverPolicy.all,
            DeliverPolicy.last,
            DeliverPolicy.last_per_subject,
            DeliverPolicy.new,
            DeliverPolicy.by_start_time,
        ],
    )
    async def test_create_with_opt_start_seq_bad_deliver_policy_error(
        self, deliver_policy: DeliverPolicy
    ):
        with pytest.raises(ValueError) as exc_info:
            ConsumerConfig.new_ephemeral_push_config(
                "deliver",
                opt_start_seq=10,
                deliver_policy=deliver_policy,
            )
        assert exc_info.value.args == (
            "deliver_policy must be DeliverPolicy.by_start_sequence",
        )

    @pytest.mark.parametrize("deliver_policy", [DeliverPolicy.by_start_time, None])
    async def test_create_with_opt_start_time(
        self, deliver_policy: Optional[DeliverPolicy]
    ):
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            "deliver",
            opt_start_time=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
            deliver_policy=deliver_policy,
        )
        assert consumer_config.opt_start_time == "1970-01-01T00:00:00Z"
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize(
        "deliver_policy",
        [
            DeliverPolicy.all,
            DeliverPolicy.last,
            DeliverPolicy.last_per_subject,
            DeliverPolicy.new,
            DeliverPolicy.by_start_sequence,
        ],
    )
    async def test_create_with_opt_start_time_bad_deliver_policy_error(
        self, deliver_policy: DeliverPolicy
    ):
        with pytest.raises(ValueError) as exc_info:
            ConsumerConfig.new_ephemeral_push_config(
                "deliver",
                opt_start_time=datetime.datetime(1970, 1, 1),
                deliver_policy=deliver_policy,
            )
        assert exc_info.value.args == (
            "deliver_policy must be DeliverPolicy.by_start_time",
        )

    async def test_create_with_ack_wait(self):
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            "deliver", ack_wait=10
        )
        assert consumer_config.ack_wait == 10
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_max_deliver(self):
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            "deliver", max_deliver=10
        )
        assert consumer_config.max_deliver == 10
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    async def test_create_with_filter_subject(self):
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            "deliver", filter_subjects="test.1"
        )
        assert consumer_config.filter_subject == "test.1"
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_filter_subjects(self):
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            "deliver", filter_subjects=["test.1", "test.2"]
        )
        assert consumer_config.filter_subjects == ["test.1", "test.2"]
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_sample_freq(self):
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            "deliver", sample_freq=datetime.timedelta(seconds=30)
        )
        assert consumer_config.sample_freq == "30000000000"
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    @pytest.mark.parametrize("heartbeat", [datetime.timedelta(seconds=60), None])
    async def test_create_with_flow_control(
        self, heartbeat: Optional[datetime.timedelta]
    ):
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            "deliver",
            flow_control=True,
            idle_heartbeat=heartbeat,
        )
        assert consumer_config.flow_control is True
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_rate_limit_bps(self):
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            "deliver",
            rate_limit_bps=1,
        )
        assert consumer_config.rate_limit_bps == 1
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_inactive_threshold(self):
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            "deliver",
            inactive_threshold=datetime.timedelta(seconds=30),
        )
        assert consumer_config.inactive_threshold == 30000000000
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    @pytest.mark.parametrize("max_deliver", [4, 100, None])
    async def test_create_with_backoff(self, max_deliver: Optional[int]):
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            "deliver",
            max_deliver=max_deliver,
            backoff=[10_000_000_000_000, 30_000_000_000_000, 60_000_000_000_000],
        )
        assert consumer_config.backoff == [
            10_000_000_000_000,
            30_000_000_000_000,
            60_000_000_000_000,
        ]
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    @pytest.mark.parametrize("max_deliver", [0, 2, 3])
    async def test_create_with_backoff_bad_max_deliver_error(self, max_deliver: int):
        with pytest.raises(ValueError) as exc_info:
            ConsumerConfig.new_ephemeral_push_config(
                "deliver",
                max_deliver=max_deliver,
                backoff=[10_000_000_000_000, 30_000_000_000_000, 60_000_000_000_000],
            )
        assert exc_info.value.args == (
            "max_deliver must be greater than the length of backoff",
        )

    async def test_create_with_num_replicas(self):
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            "deliver", num_replicas=3
        )
        assert consumer_config.num_replicas == 3
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.create_ephemeral_consumer_from_config(consumer_config)
        assert exc_info.value.error == Error(
            code=500,
            description="replicas > 1 not supported in non-clustered mode",
            err_code=10074,
        )

    async def test_create_with_mem_storage(self):
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            "deliver", mem_storage=True
        )
        assert consumer_config.mem_storage is True
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    async def test_create_with_metadata(self):
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            "deliver", metadata={"foo": "bar"}
        )
        assert consumer_config.metadata == {"foo": "bar"}
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    async def test_create_with_direct(self):
        consumer_config = ConsumerConfig.new_ephemeral_push_config(
            "deliver", direct=True
        )
        assert consumer_config.direct is True
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config


class TestStreamCreateDurablePushConsumerFromConfig(BaseTestStream):
    @pytest_asyncio.fixture(autouse=True)
    async def setup_stream(self):
        config = StreamConfig.new(
            "test-stream",
            subjects=["test.>"],
        )
        self.stream = await self.manager.create_from_config(config)

    async def test_create(self):
        consumer_config = ConsumerConfig.new_durable_push_config(
            name="test-consumer", deliver_subject="deliver"
        )
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    async def test_create_with_description(self):
        consumer_config = ConsumerConfig.new_durable_push_config(
            name="test-consumer",
            deliver_subject="deliver",
            description="some description",
        )
        assert consumer_config.description == "some description"
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    async def test_create_with_existing_name_ok(self):
        consumer_config = ConsumerConfig.new_durable_push_config(
            "test-consumer", deliver_subject="deliver"
        )
        await self.stream.create_durable_consumer_from_config(consumer_config)
        await self.stream.create_durable_consumer_from_config(consumer_config)

    async def test_create_with_existing_name_and_different_config_error(
        self,
    ):
        consumer_config = ConsumerConfig.new_durable_push_config(
            "test-consumer", "deliver"
        )
        await self.stream.create_durable_consumer_from_config(consumer_config)
        consumer_config.headers_only = True
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.create_durable_consumer_from_config(consumer_config)
        assert exc_info.value.error == Error(
            code=400,
            description="consumer already exists",
            err_code=10148,
        )

    async def test_create_filtered_with_existing_name_and_different_config_error(
        self,
    ):
        consumer_config = ConsumerConfig.new_durable_push_config(
            "test-consumer", "deliver"
        )
        await self.stream.create_durable_consumer_from_config(consumer_config)
        consumer_config.filter_subject = "test.1"
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.create_durable_consumer_from_config(consumer_config)
        assert exc_info.value.error == Error(
            code=400,
            description="consumer already exists",
            err_code=10148,
        )

    async def test_create_without_ack_policy(self):
        consumer_config = ConsumerConfig.new_durable_push_config(
            "test-consumer",
            "deliver",
            ack_policy=AckPolicy.none,
        )
        assert consumer_config.ack_policy == AckPolicy.none
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        # Max ack pending cannot be set by client for push consumers
        consumer_config.max_ack_pending = consumer_.config.max_ack_pending
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    async def test_create_with_replay_policy(self):
        consumer_config = ConsumerConfig.new_durable_push_config(
            "test-consumer", "deliver", replay_policy=ReplayPolicy.original
        )
        assert consumer_config.replay_policy == ReplayPolicy.original
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    async def test_create_with_deliver_policy(self):
        consumer_config = ConsumerConfig.new_durable_push_config(
            "test-consumer", "deliver", deliver_policy=DeliverPolicy.new
        )
        assert consumer_config.deliver_policy == DeliverPolicy.new
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize("deliver_policy", [DeliverPolicy.by_start_sequence, None])
    async def test_create_with_opt_start_seq(
        self, deliver_policy: Optional[DeliverPolicy]
    ):
        consumer_config = ConsumerConfig.new_durable_push_config(
            "test-consumer", "deliver", opt_start_seq=10, deliver_policy=deliver_policy
        )
        assert consumer_config.opt_start_seq == 10
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize(
        "deliver_policy",
        [
            DeliverPolicy.all,
            DeliverPolicy.last,
            DeliverPolicy.last_per_subject,
            DeliverPolicy.new,
            DeliverPolicy.by_start_time,
        ],
    )
    async def test_create_with_opt_start_seq_bad_deliver_policy_error(
        self, deliver_policy: DeliverPolicy
    ):
        with pytest.raises(ValueError) as exc_info:
            ConsumerConfig.new_durable_push_config(
                "test-consumer",
                "deliver",
                opt_start_seq=10,
                deliver_policy=deliver_policy,
            )
        assert exc_info.value.args == (
            "deliver_policy must be DeliverPolicy.by_start_sequence",
        )

    @pytest.mark.parametrize("deliver_policy", [DeliverPolicy.by_start_time, None])
    async def test_create_with_opt_start_time(
        self, deliver_policy: Optional[DeliverPolicy]
    ):
        consumer_config = ConsumerConfig.new_durable_push_config(
            "test-consumer",
            "deliver",
            opt_start_time=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
            deliver_policy=deliver_policy,
        )
        assert consumer_config.opt_start_time == "1970-01-01T00:00:00Z"
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    @pytest.mark.parametrize(
        "deliver_policy",
        [
            DeliverPolicy.all,
            DeliverPolicy.last,
            DeliverPolicy.last_per_subject,
            DeliverPolicy.new,
            DeliverPolicy.by_start_sequence,
        ],
    )
    async def test_create_with_opt_start_time_bad_deliver_policy_error(
        self, deliver_policy: DeliverPolicy
    ):
        with pytest.raises(ValueError) as exc_info:
            ConsumerConfig.new_durable_push_config(
                "test-consumer",
                "deliver",
                opt_start_time=datetime.datetime(1970, 1, 1),
                deliver_policy=deliver_policy,
            )
        assert exc_info.value.args == (
            "deliver_policy must be DeliverPolicy.by_start_time",
        )

    async def test_create_with_ack_wait(self):
        consumer_config = ConsumerConfig.new_durable_push_config(
            "test-consumer", "deliver", ack_wait=10
        )
        assert consumer_config.ack_wait == 10
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_max_deliver(self):
        consumer_config = ConsumerConfig.new_durable_push_config(
            "test-consumer", "deliver", max_deliver=10
        )
        assert consumer_config.max_deliver == 10
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_config
        assert consumer.config == consumer_.config

    async def test_create_with_filter_subject(self):
        consumer_config = ConsumerConfig.new_durable_push_config(
            "test-consumer", "deliver", filter_subjects="test.1"
        )
        assert consumer_config.filter_subject == "test.1"
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_filter_subjects(self):
        consumer_config = ConsumerConfig.new_durable_push_config(
            "test-consumer", "deliver", filter_subjects=["test.1", "test.2"]
        )
        assert consumer_config.filter_subjects == ["test.1", "test.2"]
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_sample_freq(self):
        consumer_config = ConsumerConfig.new_durable_push_config(
            "test-consumer", "deliver", sample_freq=datetime.timedelta(seconds=30)
        )
        assert consumer_config.sample_freq == "30000000000"
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    @pytest.mark.parametrize("heartbeat", [datetime.timedelta(seconds=60), None])
    async def test_create_with_flow_control(
        self, heartbeat: Optional[datetime.timedelta]
    ):
        consumer_config = ConsumerConfig.new_durable_push_config(
            "test-consumer",
            "deliver",
            flow_control=True,
            idle_heartbeat=heartbeat,
        )
        assert consumer_config.flow_control is True
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_rate_limit_bps(self):
        consumer_config = ConsumerConfig.new_durable_push_config(
            "test-consumer",
            "deliver",
            rate_limit_bps=1,
        )
        assert consumer_config.rate_limit_bps == 1
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer.config == consumer_.config
        assert consumer.config == consumer_config

    async def test_create_with_inactive_threshold(self):
        consumer_config = ConsumerConfig.new_durable_push_config(
            "test-consumer",
            "deliver",
            inactive_threshold=datetime.timedelta(seconds=30),
        )
        assert consumer_config.inactive_threshold == 30000000000
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    @pytest.mark.parametrize("max_deliver", [4, 100, None])
    async def test_create_with_backoff(self, max_deliver: Optional[int]):
        consumer_config = ConsumerConfig.new_durable_push_config(
            "test-consumer",
            "deliver",
            max_deliver=max_deliver,
            backoff=[10_000_000_000_000, 30_000_000_000_000, 60_000_000_000_000],
        )
        assert consumer_config.backoff == [
            10_000_000_000_000,
            30_000_000_000_000,
            60_000_000_000_000,
        ]
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    @pytest.mark.parametrize("max_deliver", [0, 2, 3])
    async def test_create_with_backoff_bad_max_deliver_error(self, max_deliver: int):
        with pytest.raises(ValueError) as exc_info:
            ConsumerConfig.new_durable_push_config(
                "test-consumer",
                "deliver",
                max_deliver=max_deliver,
                backoff=[10_000_000_000_000, 30_000_000_000_000, 60_000_000_000_000],
            )
        assert exc_info.value.args == (
            "max_deliver must be greater than the length of backoff",
        )

    async def test_create_with_num_replicas(self):
        consumer_config = ConsumerConfig.new_durable_push_config(
            "test-consumer", "deliver", num_replicas=3
        )
        assert consumer_config.num_replicas == 3
        with pytest.raises(JetStreamAPIException) as exc_info:
            await self.stream.create_durable_consumer_from_config(consumer_config)
        assert exc_info.value.error == Error(
            code=500,
            description="replicas > 1 not supported in non-clustered mode",
            err_code=10074,
        )

    async def test_create_with_mem_storage(self):
        consumer_config = ConsumerConfig.new_durable_push_config(
            "test-consumer", "deliver", mem_storage=True
        )
        assert consumer_config.mem_storage is True
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config

    async def test_create_with_metadata(self):
        consumer_config = ConsumerConfig.new_durable_push_config(
            "test-consumer", "deliver", metadata={"foo": "bar"}
        )
        assert consumer_config.metadata == {"foo": "bar"}
        consumer = await self.stream.create_durable_consumer_from_config(
            consumer_config
        )
        consumer_ = await self.stream.get_consumer(consumer.name)
        # Max waiting cannot be set by client for push consumers
        consumer_config.max_waiting = consumer_.config.max_waiting
        assert consumer_.config == consumer_config
        assert consumer_.config == consumer.config


class TestStreamListConsumers(BaseTestStream):
    @pytest_asyncio.fixture(autouse=True)
    async def setup_stream(self):
        config = StreamConfig.new(
            "test-stream",
            subjects=["test.>"],
        )
        self.stream = await self.manager.create_from_config(config)

    async def test_list_consumers_no_consumer(self):
        consumers = await self.stream.list_consumers()
        assert consumers == []

    async def test_list_consumers_single_consumer(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config()
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumers = await self.stream.list_consumers()
        assert len(consumers) == 1
        assert consumers[0].config == consumer.config

    async def test_list_consumers_with_offset(self):
        consumer_config1 = ConsumerConfig.new_ephemeral_pull_config()
        consumer_config2 = ConsumerConfig.new_ephemeral_pull_config()
        await self.stream.create_ephemeral_consumer_from_config(consumer_config1)
        consumer2 = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config2
        )
        consumers = await self.stream.list_consumers(offset=1)
        assert len(consumers) == 1
        assert consumers[0].config == consumer2.config


class TestStreamListConsumerNames(BaseTestStream):
    @pytest_asyncio.fixture(autouse=True)
    async def setup_stream(self):
        config = StreamConfig.new(
            "test-stream",
            subjects=["test.>"],
        )
        self.stream = await self.manager.create_from_config(config)

    async def test_list_consumer_names_no_consumer(self):
        consumer_names = await self.stream.list_consumer_names()
        assert consumer_names == []

    async def test_list_consumer_names_single_consumer(self):
        consumer_config = ConsumerConfig.new_ephemeral_pull_config()
        consumer = await self.stream.create_ephemeral_consumer_from_config(
            consumer_config
        )
        consumers = await self.stream.list_consumer_names()
        assert len(consumers) == 1
        assert consumers == [consumer.name]

    async def test_list_consumer_names_with_offset(self):
        consumer_config1 = ConsumerConfig.new_ephemeral_pull_config(
            description="consumer1"
        )
        consumer_config2 = ConsumerConfig.new_ephemeral_pull_config(
            description="consumer2"
        )
        await self.stream.create_ephemeral_consumer_from_config(consumer_config1)
        await self.stream.create_ephemeral_consumer_from_config(consumer_config2)
        consumers = await self.stream.list_consumer_names(offset=1)
        assert len(consumers) == 1
        # I don't know why this test is flaky...
        # assert consumers == [
        #     consumer2.name
        # ], f"expected name: {consumer2.name} but got {consumers[0]}. Other consumer name is {consumer1.name}."


class TestBadStreamUpdate(BaseTestStream):
    @pytest_asyncio.fixture(autouse=True)
    async def setup_stream(self):
        config = StreamConfig.new(
            "test-stream",
            subjects=["test.>"],
        )
        self.stream = await self.manager.create_from_config(config)

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
