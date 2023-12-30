# @generated

from dataclasses import dataclass
from typing import Optional, Union

from easynats.channel import Channel, Command

from .api_error import JetStreamApiV1Error
from .common.stream_configuration import StreamConfig
from .common.stream_state import StreamState


@dataclass
class JetStreamApiV1StreamSnapshotParams:
    """
    Params for the JetStream $JS.API.STREAM.SNAPSHOT API
    """

    stream_name: str
    """
    The name of the stream to snapshot
    """


@dataclass
class JetStreamApiV1StreamSnapshotRequest:
    """
    A request to the JetStream $JS.API.STREAM.SNAPSHOT API
    """

    deliver_subject: str
    """
    The NATS subject where the snapshot will be delivered
    """
    no_consumers: Optional[bool] = None
    """
    When true consumer states and configurations will not be present in the snapshot
    """
    chunk_size: Optional[int] = None
    """
    The size of data chunks to send to deliver_subject
    """
    jsck: Optional[bool] = False
    """
    Check all message's checksums prior to snapshot
    """


@dataclass
class StreamSnapshotResponse:
    """
    A response from the JetStream $JS.API.STREAM.SNAPSHOT API
    """

    config: StreamConfig
    state: StreamState
    type: Optional[str] = None


JetStreamApiV1StreamSnapshotResponse = Union[
    StreamSnapshotResponse, JetStreamApiV1Error
]


SNAPSHOT_STREAM = Command(
    channel=Channel(
        subject="STREAM.SNAPSHOT.{stream_name}",
        parameters=JetStreamApiV1StreamSnapshotParams,
    ),
    message=JetStreamApiV1StreamSnapshotRequest,
    reply=JetStreamApiV1StreamSnapshotResponse,
    error=bytes,
)
