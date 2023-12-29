# @generated

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Action(Enum):
    """
    The action that the event describes
    """

    create = "create"
    delete = "delete"
    modify = "modify"


@dataclass
class IoNatsJetstreamAdvisoryV1StreamAction:
    """
    An Advisory sent when a Stream is created, modified or deleted
    """

    id: str
    """
    Unique correlation ID for this event
    """
    timestamp: str
    """
    The time this event was created in RFC3339 format
    """
    action: Action
    """
    The action that the event describes
    """
    stream: str
    """
    The name of the Stream that's acted on
    """
    type: str = "io.nats.jetstream.advisory.v1.stream_action"
    template: Optional[str] = None
    """
    The Stream Template that manages the Stream
    """
