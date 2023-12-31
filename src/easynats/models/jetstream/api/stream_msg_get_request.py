# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class IoNatsJetstreamApiV1StreamMsgGetRequest:
    """
    A request to the JetStream $JS.API.STREAM.MSG.GET API
    """

    seq: Optional[int] = None
    """
    Stream sequence number of the message to retrieve, cannot be combined with last_by_subj
    """
    last_by_subj: Optional[str] = None
    """
    Retrieves the last message for a given subject, cannot be combined with seq
    """
    next_by_subj: Optional[str] = None
    """
    Combined with sequence gets the next message for a subject with the given sequence or higher
    """
