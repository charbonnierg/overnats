import pytest
import pytest_asyncio

from easynats.connection import NatsConnection
from easynats.jetstream.api import JetStreamClient
from easynats.jetstream.manager import StreamManager


@pytest.mark.asyncio
class TestStreamManager:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self):
        self.conn = NatsConnection()
        self.js_client = JetStreamClient(self.conn)
        self.manager = StreamManager(self.js_client)
        async with self.conn:
            yield

    async def test_list_streams(self):
        streams = await self.manager.list()
        assert streams == []
