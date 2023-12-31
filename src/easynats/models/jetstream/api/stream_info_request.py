# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class IoNatsJetstreamApiV1StreamInfoRequest:
    """
    A request to the JetStream $JS.API.STREAM.INFO API
    """

    deleted_details: Optional[bool] = None
    """
    When true will result in a full list of deleted message IDs being returned in the info response
    """
    subjects_filter: Optional[str] = None
    """
    When set will return a list of subjects and how many messages they hold for all matching subjects. Filter is a standard NATS subject wildcard pattern.
    """
    offset: Optional[int] = None
    """
    Paging offset when retrieving pages of subjet details
    """
