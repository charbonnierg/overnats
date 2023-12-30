# @generated

from __future__ import annotations

from dataclasses import dataclass

from .stream_configuration import StreamConfiguration


@dataclass
class StreamTemplateConfiguration:
    """
    The data structure that describe the configuration of a NATS JetStream Stream Template
    """

    name: str
    """
    A unique name for the Stream Template.
    """
    max_streams: int
    """
    The maximum number of Streams this Template can create, -1 for unlimited.
    """
    config: StreamConfiguration
