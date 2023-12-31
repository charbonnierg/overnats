# @generated

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IoNatsJetstreamApiV1ConsumerListResponse:
    """
    A response from the JetStream $JS.API.CONSUMER.LIST API
    """

    total: int
    offset: int
    limit: int
    type: str
