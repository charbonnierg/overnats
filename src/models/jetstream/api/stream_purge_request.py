# @generated

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class IoNatsJetstreamApiV1StreamPurgeRequest:
    """
    A request to the JetStream $JS.API.STREAM.PURGE API
    """

    filter: Optional[str] = None
    """
    Restrict purging to messages that match this subject
    """
    seq: Optional[int] = None
    """
    Purge all messages up to but not including the message with this sequence. Can be combined with subject filter but not the keep option
    """
    keep: Optional[int] = None
    """
    Ensures this many messages are present after the purge. Can be combined with the subject filter but not the sequence
    """
