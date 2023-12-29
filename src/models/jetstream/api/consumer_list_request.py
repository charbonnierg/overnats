# @generated

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IoNatsJetstreamApiV1ConsumerListRequest:
    """
    A request to the JetStream $JS.API.CONSUMER.LIST API
    """

    offset: int
