# @generated

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Action(str, Enum):
    """
    The action that the event describes
    """

    create = "create"
    delete = "delete"


@dataclass
class ConsumerAction:
    """
    An Advisory sent when a Consumer is created or deleted
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
    The name of the Stream that the Consumer belongs to
    """
    consumer: Optional[str] = None
    """
    The name of the Consumer that's acted on
    """
    type: str = "io.nats.jetstream.advisory.v1.consumer_action"

    def __post_init__(self) -> None:
        if not isinstance(
            self.action, Action
        ):  # pyright: ignore[reportUnnecessaryIsInstance]
            self.action = Action(self.action)
