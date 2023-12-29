# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class IoNatsJetstreamApiV1StreamListRequest:
    """
    A request to the JetStream $JS.API.STREAM.LIST API
    """

    subject: Optional[str] = None
    """
    Limit the list to streams matching this subject filter
    """
    offset: Optional[int] = None
