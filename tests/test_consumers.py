import pytest
import pytest_asyncio

from easynats import Connection
from easynats.jetstream.entities import Stream


@pytest.mark.asyncio
class BaseTestConsumer:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        self.conn = Connection()
        self.js_conn = self.conn.jetstream()
        self.manager = self.js_conn.streams
        async with self.conn:
            self.stream = await self.setup_stream()
            try:
                yield
            finally:
                await self.cleanup()

    async def cleanup(self):
        # Clean up all streams
        for stream_name in await self.manager.list_names():
            await self.manager.delete(stream_name)

    async def setup_stream(self) -> Stream:
        return await self.manager.create("test-stream", subjects=["test.*"])


class TestPushConsumer(BaseTestConsumer):
    async def test_get_next_message_from_stream(self):
        # Publish message
        await self.stream.publish(subject="test.1")
        # Create consumer
        consumer = await self.stream.create_ephemeral_push_consumer()
        # Check consumer state before GET_NEXT
        state = await consumer.state()
        assert state.num_pending == 1
        assert state.num_ack_pending == 0
        async with consumer.messages() as queue:
            msg = await queue.next()
            assert msg.subject() == "test.1"
            assert msg.data() == b""
            # Check consumer state before ACK
            state = await consumer.state()
            assert state.num_ack_pending == 1
            await msg.ack()
        # Check consumer state
        state = await consumer.state()
        assert state.num_pending == 0
        assert state.num_ack_pending == 0


class TestPullConsumer(BaseTestConsumer):
    async def test_get_next_message_from_stream(self):
        # Publish message
        await self.stream.publish(subject="test.1")
        # Create consumer
        consumer = await self.stream.create_ephemeral_pull_consumer()
        # Check consumer state before GET_NEXT
        state = await consumer.state()
        assert state.num_pending == 1
        assert state.num_ack_pending == 0
        # Open message queue
        async with consumer.messages() as queue:
            # Get message
            msg = await queue.next()
            assert msg.subject() == "test.1"
            assert msg.data() == b""
            # Check consumer state before ACK
            state = await consumer.state()
            assert state.num_ack_pending == 1
            await msg.ack()
        # Check consumer state
        state = await consumer.state()
        assert state.num_pending == 0
        assert state.num_ack_pending == 0
