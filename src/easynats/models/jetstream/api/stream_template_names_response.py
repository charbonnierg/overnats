# @generated

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IoNatsJetstreamApiV1StreamTemplateNamesResponse:
    """
    A response from the JetStream $JS.API.STREAM.TEMPLATE.NAMES API
    """

    total: int
    offset: int
    limit: int
    type: str
