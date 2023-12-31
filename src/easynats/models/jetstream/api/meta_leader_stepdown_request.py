# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Placement:
    """
    Placement requirements for a stream
    """

    cluster: str
    """
    The desired cluster name to place the stream
    """
    tags: Optional[List[str]] = None
    """
    Tags required on servers hosting this stream
    """


@dataclass
class IoNatsJetstreamApiV1MetaLeaderStepdownRequest:
    """
    A request to the JetStream $JS.API.META.LEADER.STEPDOWN API
    """

    placement: Optional[Placement] = None
    """
    Placement requirements for a stream
    """
