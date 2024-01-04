from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from ..core import ReplyMsg
from .channel import Command, ErrorT, ParamsT, ReplyT

T = TypeVar("T")


@dataclass
class TypedReply(Generic[ParamsT, ReplyT, ErrorT]):
    """The reply of request."""

    success: bool
    """Whether the reply is a success or an error."""
    payload: ReplyT | ErrorT
    """The reply data."""
    headers: dict[str, str]
    """The reply headers."""

    def get_error(self) -> ErrorT | None:
        """Get the error payload or None if reply is a success."""
        if not self.success:
            return self.payload  # type: ignore

    def get_data(self) -> ReplyT | None:
        """Get the data payload or None if reply is an error."""
        if self.success:
            return self.payload  # type: ignore

    def error(self) -> ErrorT:
        """Get the error payload or raise an exception if reply is a success."""
        if self.success:
            raise RuntimeError("Reply is not an error")
        return self.payload  # type: ignore

    def data(self) -> ReplyT:
        """Get the data payload or raise an exception if reply is an error."""
        if not self.success:
            raise RuntimeError("Reply is not a success")
        return self.payload  # type: ignore

    @classmethod
    def create(
        cls, command: Command[ParamsT, Any, ReplyT, ErrorT], reply: ReplyMsg
    ) -> TypedReply[ParamsT, ReplyT, ErrorT]:
        """Create a typed reply from a command and a reply."""
        success = command.is_success(reply)
        if success:
            reply_data = command.decode_reply(reply.payload())
        else:
            reply_data = command.decode_error(reply.payload())
        return cls(
            success=success,
            payload=reply_data,
            headers=reply.headers(),
        )
