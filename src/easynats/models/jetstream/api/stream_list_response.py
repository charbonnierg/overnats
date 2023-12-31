# @generated

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IoNatsJetstreamApiV1StreamListResponse:
    """
    A response from the JetStream $JS.API.STREAM.LIST API
    """

    total: int
    offset: int
    limit: int
    type: str
