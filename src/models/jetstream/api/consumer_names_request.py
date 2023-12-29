# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class IoNatsJetstreamApiV1ConsumerNamesRequest:
    """
    A request to the JetStream $JS.API.CONSUMER.NAMES API
    """

    offset: int
    subject: Optional[str] = None
    """
    Filter the names to those consuming messages matching this subject or wildcard
    """
