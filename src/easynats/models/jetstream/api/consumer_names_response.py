# @generated

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IoNatsJetstreamApiV1ConsumerNamesResponse:
    """
    A response from the JetStream $JS.API.CONSUMER.NAMES API
    """

    total: int
    offset: int
    limit: int
    type: str
