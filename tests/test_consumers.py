import asyncio

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
    async def test_peek_next_message_from_stream_no_message(self):
        # Create consumer
        consumer = await self.stream.create_ephemeral_push_consumer()
        # Open message queue
        async with consumer.messages() as queue:
            # Get message
            msg = await queue.peek()
            assert msg is None

    async def test_peek_next_message_from_stream_single_message(self):
        await self.stream.publish("test.1", b"1")
        # Create consumer
        consumer = await self.stream.create_ephemeral_push_consumer()
        # Open message queue
        async with consumer.messages() as queue:
            # Give some time for the queue to receive the message
            await asyncio.sleep(1e-2)
            # Get message
            msg = await queue.peek()
            assert msg is not None
            assert msg.subject() == "test.1"
            assert msg.data() == b"1"
            await msg.ack()

    async def test_peek_next_message_from_stream_with_many_message(self):
        await self.stream.publish("test.1", b"1")
        await self.stream.publish("test.2", b"2")
        await self.stream.publish("test.3", b"3")
        # Create consumer
        consumer = await self.stream.create_ephemeral_push_consumer()
        # Open message queue
        async with consumer.messages() as queue:
            # Give some time for the queue to receive the message
            await asyncio.sleep(1e-2)
            # Get message
            msg = await queue.peek()
            assert msg is not None
            assert msg.subject() == "test.1"
            assert msg.data() == b"1"
            await msg.ack()
            # Get message
            msg = await queue.peek()
            assert msg is not None
            assert msg.subject() == "test.2"
            assert msg.data() == b"2"
            await msg.ack()
            # Get message
            msg = await queue.peek()
            assert msg is not None
            assert msg.subject() == "test.3"
            assert msg.data() == b"3"
            await msg.ack()
            # Get message
            msg = await queue.peek()
            assert msg is None

    async def test_get_next_message_from_stream(self):
        # Publish message
        await self.stream.publish(subject="test.1")
        # Create consumer
        consumer = await self.stream.create_ephemeral_push_consumer()
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

    async def test_redeliver_message(self):
        # Publish message
        await self.stream.publish(subject="test.1")
        # Create consumer
        consumer = await self.stream.create_ephemeral_push_consumer()
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
            assert msg.num_delivered() == 1
            # Check consumer state before NACK
            state = await consumer.state()
            assert state.num_ack_pending == 1
            await msg.nak()
            # Check consumer state after NACK
            state = await consumer.state()
            assert state.num_pending == 0
            assert state.num_ack_pending == 1
            # Get message
            msg = await queue.next()
            assert msg.subject() == "test.1"
            assert msg.data() == b""
            assert msg.num_delivered() == 2
            await msg.ack()
        # Check consumer state after ACK
        state = await consumer.state()
        assert state.num_pending == 0
        assert state.num_ack_pending == 0
        # NOTE: Testing for .num_redelivered leads to an error. Is this a bug ?

    async def test_redeliver_message_with_many_pending_messages(self):
        # Publish message
        await self.stream.publish(subject="test.1")
        await self.stream.publish(subject="test.2")
        await self.stream.publish(subject="test.3")
        # Create consumer
        consumer = await self.stream.create_ephemeral_push_consumer(max_ack_pending=1)
        # Check consumer state before GET_NEXT
        state = await consumer.state()
        assert state.num_pending == 3
        assert state.num_ack_pending == 0
        # Open message queue
        async with consumer.messages() as queue:
            # Get message
            msg = await queue.next()
            assert msg.subject() == "test.1"
            assert msg.data() == b""
            assert msg.num_delivered() == 1
            # Check consumer state before NACK
            state = await consumer.state()
            assert state.num_ack_pending == 1
            await msg.nak()
            # Check consumer state after NACK
            state = await consumer.state()
            assert state.num_pending == 2
            assert state.num_ack_pending == 1
            # Get message
            msg = await queue.next()
            assert msg.subject() == "test.1"
            assert msg.data() == b""
            assert msg.num_delivered() == 2
            await msg.ack()
        # Check consumer state after ACK
        state = await consumer.state()
        assert state.num_pending == 1
        assert state.num_ack_pending == 1
        # NOTE: Testing for .num_redelivered leads to an error. Is this a bug ?


class TestPullConsumer(BaseTestConsumer):
    async def test_peek_next_message_from_stream_no_message(self):
        # Create consumer
        consumer = await self.stream.create_ephemeral_pull_consumer()
        # Open message queue
        async with consumer.messages() as queue:
            # Get message
            msg = await queue.peek()
            assert msg is None

    async def test_peek_next_message_from_stream_single_message(self):
        await self.stream.publish("test.1", b"1")
        # Create consumer
        consumer = await self.stream.create_ephemeral_pull_consumer()
        # Open message queue
        async with consumer.messages() as queue:
            # Get message
            msg = await queue.peek()
            assert msg is not None
            assert msg.subject() == "test.1"
            assert msg.data() == b"1"
            await msg.ack()

    async def test_peek_next_message_from_stream_with_many_message(self):
        await self.stream.publish("test.1", b"1")
        await self.stream.publish("test.2", b"2")
        await self.stream.publish("test.3", b"3")
        # Create consumer
        consumer = await self.stream.create_ephemeral_pull_consumer()
        # Open message queue
        async with consumer.messages() as queue:
            # Get message
            msg = await queue.peek()
            assert msg is not None
            assert msg.subject() == "test.1"
            assert msg.data() == b"1"
            await msg.ack()
            # Get message
            msg = await queue.peek()
            assert msg is not None
            assert msg.subject() == "test.2"
            assert msg.data() == b"2"
            await msg.ack()
            # Get message
            msg = await queue.peek()
            assert msg is not None
            assert msg.subject() == "test.3"
            assert msg.data() == b"3"
            await msg.ack()
            # Get message
            msg = await queue.peek()
            assert msg is None

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

    async def test_redeliver_message(self):
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
            assert msg.num_delivered() == 1
            # Check consumer state before NACK
            state = await consumer.state()
            assert state.num_ack_pending == 1
            await msg.nak()
            # Check consumer state after NACK
            state = await consumer.state()
            assert state.num_pending == 0
            assert state.num_ack_pending == 1
            # Get message
            msg = await queue.next()
            assert msg.subject() == "test.1"
            assert msg.data() == b""
            assert msg.num_delivered() == 2
            await msg.ack()
        # Check consumer state after ACK
        state = await consumer.state()
        assert state.num_pending == 0
        assert state.num_ack_pending == 0
        # NOTE: Testing for .num_redelivered leads to an error. Is this a bug ?

    async def test_redeliver_message_with_many_pending_messages(self):
        # Publish message
        await self.stream.publish(subject="test.1")
        await self.stream.publish(subject="test.2")
        await self.stream.publish(subject="test.3")
        # Create consumer
        consumer = await self.stream.create_ephemeral_pull_consumer()
        # Check consumer state before GET_NEXT
        state = await consumer.state()
        assert state.num_pending == 3
        assert state.num_ack_pending == 0
        # Open message queue
        async with consumer.messages() as queue:
            # Get message
            msg = await queue.next()
            assert msg.subject() == "test.1"
            assert msg.data() == b""
            assert msg.num_delivered() == 1
            # Check consumer state before NACK
            state = await consumer.state()
            assert state.num_ack_pending == 1
            await msg.nak()
            # Check consumer state after NACK
            state = await consumer.state()
            assert state.num_pending == 2
            assert state.num_ack_pending == 1
            # Get message
            msg = await queue.next()
            assert msg.subject() == "test.1"
            assert msg.data() == b""
            assert msg.num_delivered() == 2
            await msg.ack()
        # Check consumer state after ACK
        state = await consumer.state()
        assert state.num_pending == 2
        assert state.num_ack_pending == 0
        # NOTE: Testing for .num_redelivered leads to an error. Is this a bug ?
