from __future__ import annotations

from ...api import Error, JetStreamApiClient, JetStreamAPIException
from ...models.api.common.stream_configuration import (
    Compression,
    Mirror,
    Placement,
    Republish,
    Source,
    Storage,
    SubjectTransform,
)
from ..streams.manager import StreamManager
from .kv import KV, KVConfig


class KVManager:
    def __init__(self, client: JetStreamApiClient):
        self.client = client
        self.streams = StreamManager(client=client)

    async def list(self, offset: int | None = None) -> list[KV]:
        """List all KVs.

        Args:
            offset: offset to start from

        Returns:
            A list of key-value buckets as python objects
        """
        response = await self.client.list_streams(
            subject="$KV.>",
            offset=offset,
        )
        return [
            KV.from_stream_info(client=self.client, stream_info=info)
            for info in response.streams
        ]

    async def list_names(self, offset: int | None = None) -> list[str]:
        """List all KV names.

        Args:
            offset: offset to start from

        Returns:
            A list of key-value bucket names
        """
        response = await self.client.list_stream_names(
            subject="$KV.>",
            offset=offset,
        )
        return [name[3:] for name in response.streams if name.startswith("KV_")]

    async def get(self, bucket_name: str) -> KV:
        """Get a KV by name.

        Args:
            bucket_name: name of the KV to get

        Raises:
            JetStreamAPIException: if the NATS server returns an error

        Returns:
            The KV as a python object
        """
        stream_info_response = await self.client.get_stream_info(
            stream_name=f"KV_{bucket_name}"
        )
        return KV.from_stream_info(client=self.client, stream_info=stream_info_response)

    async def create_from_config(self, kv_config: KVConfig) -> KV:
        """Create a new KV.

        Args:
            kv_config: the KV configuration

        Raises:
            ValueError: if the KV name is not set in the configuration
            JetStreamAPIException: if the NATS server returns an error

        Returns:
            The created KV as a python object
        """
        names = await self.list_names()
        if kv_config.name in names:
            raise JetStreamAPIException(
                error=Error(
                    code=400,
                    description="name is already used by an existing KV",
                    err_code=10058,
                )
            )
        kv_create_response = await self.client.create_stream(
            stream_config=kv_config.to_stream_config()
        )
        return KV.from_stream_info(client=self.client, stream_info=kv_create_response)

    async def create(
        self,
        name: str,
        max_bucket_size: int | None = None,
        ttl: int | None = None,
        history: int | None = None,
        storage: Storage | None = None,
        num_replicas: int | None = None,
        description: str | None = None,
        max_msg_size: int | None = None,
        compression: Compression | None = None,
        placement: Placement | None = None,
        mirror: Mirror | None = None,
        sources: list[Source] | None = None,
        republish: Republish | None = None,
        subject_transform: SubjectTransform | None = None,
        metadata: dict[str, str] | None = None,
    ) -> KV:
        """Create a new KV.

        Args:
            name: name of the KV
            max_bucket_size: maximum bucket size
            ttl: time to live
            history: history
            storage: storage policy
            num_replicas: number of replicas
            description: description
            max_msg_size: maximum message size
            compression: compression policy
            placement: placement policy
            mirror: mirror policy
            sources: list of sources
            republish: republish policy
            subject_transform: subject transformation policy
            metadata: metadata

        Raises:
            JetStreamAPIException: if the NATS server returns an error

        Returns:
            The created KV as a python object
        """
        kv_config = KVConfig.new(
            name=name,
            max_bucket_size=max_bucket_size,
            ttl=ttl,
            history=history,
            storage=storage,
            num_replicas=num_replicas,
            description=description,
            max_msg_size=max_msg_size,
            compression=compression,
            placement=placement,
            mirror=mirror,
            sources=sources,
            republish=republish,
            subject_transform=subject_transform,
            metadata=metadata,
        )
        return await self.create_from_config(kv_config=kv_config)

    async def configure(self, kv_config: KVConfig) -> KV:
        """Get, create or update a KV according to given configuration.

        Args:
            kv_config: the KV configuration

        Returns:
            The KV as a python object
        """
        if not kv_config.name:
            raise ValueError("KV name is required")
        try:
            kv_stream = await self.streams.get(stream_name=kv_config.name)
        except Exception:
            return await self.create_from_config(kv_config=kv_config)
        if kv_config == KVConfig.from_stream_config(kv_stream.config):
            return KV.from_stream(client=self.client, stream=kv_stream)
        kv_update_response = await self.client.update_stream(
            kv_config.to_stream_config()
        )
        return KV.from_stream_info(client=self.client, stream_info=kv_update_response)

    async def delete(self, bucket_name: str) -> None:
        """Delete a KV by name.

        Args:
            bucket_name: name of the KV to delete

        Raises:
            JetStreamAPIException: if the NATS server returns an error

        Returns:
            None. The KV is guaranteed to be deleted if no exception is raised.
        """
        await self.client.delete_stream(stream_name=f"KV_{bucket_name}")
