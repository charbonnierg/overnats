from __future__ import annotations

import datetime
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..api import JetStreamClient

from ..models.api.common.stream_configuration import StreamConfig
from ..models.api.common.stream_info import StreamInfo
from ..models.api.common.stream_state import StreamState
from ..models.api.stream_create import StreamCreateResponse
from ..models.api.stream_info import StreamInfoResponse
from ..models.api.stream_update import StreamUpdateResponse


@dataclass
class StreamMeta:
    config: StreamConfig
    state: StreamState

    def to_dict(self) -> dict[str, Any]:
        return {
            "config": asdict(self.config),
            "state": asdict(self.state),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StreamMeta:
        return cls(
            config=StreamConfig(**data["config"]),
            state=StreamState(**data["state"]),
        )


class Stream:
    def __init__(
        self,
        client: JetStreamClient,
        stream_name: str,
        stream_config: StreamConfig,
        created_timestamp: datetime.datetime,
    ) -> None:
        self.client = client
        self.name = stream_name
        self.config = stream_config
        self.created = created_timestamp

    @classmethod
    def from_stream_info(
        cls, client: JetStreamClient, stream_info: StreamInfo
    ) -> Stream:
        if not stream_info.config.name:
            raise ValueError("Stream name is required")
        created_timestamp = datetime.datetime.fromisoformat(stream_info.created)
        return cls(
            client=client,
            stream_name=stream_info.config.name,
            stream_config=stream_info.config,
            created_timestamp=created_timestamp,
        )

    @classmethod
    def from_stream_info_response(
        cls, client: JetStreamClient, stream_info_response: StreamInfoResponse
    ) -> Stream:
        if not stream_info_response.config.name:
            raise ValueError("Stream name is required")
        created_timestamp = datetime.datetime.fromisoformat(
            stream_info_response.created
        )
        return cls(
            client=client,
            stream_name=stream_info_response.config.name,
            stream_config=stream_info_response.config,
            created_timestamp=created_timestamp,
        )

    @classmethod
    def from_stream_create_response(
        cls, client: JetStreamClient, stream_create_response: StreamCreateResponse
    ) -> Stream:
        if not stream_create_response.config.name:
            raise ValueError("Stream name is required")
        created_timestamp = datetime.datetime.fromisoformat(
            stream_create_response.created
        )
        return cls(
            client=client,
            stream_name=stream_create_response.config.name,
            stream_config=stream_create_response.config,
            created_timestamp=created_timestamp,
        )

    @classmethod
    def from_stream_update_response(
        cls, client: JetStreamClient, stream_update_response: StreamUpdateResponse
    ) -> Stream:
        if not stream_update_response.config.name:
            raise ValueError("Stream name is required")
        created_timestamp = datetime.datetime.fromisoformat(
            stream_update_response.created
        )
        return cls(
            client=client,
            stream_name=stream_update_response.config.name,
            stream_config=stream_update_response.config,
            created_timestamp=created_timestamp,
        )
