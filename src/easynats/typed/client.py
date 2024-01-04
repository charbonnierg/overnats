from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .channel import Command, ErrorT, Event, MessageT, ParamsT, ReplyT
from .reply import TypedReply

if TYPE_CHECKING:
    from ..connection import Connection


class TypedClient:
    """A [`TypedClient][easynats.typed.client.TypedClient]` is a high-level interface to NATS.
    It can be used to publish or request typed messages over channels
    rather than simple subjects.

    Checkout the [channel][easynats.typed.channel] module to learn more
    about typed client usage.
    """

    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    async def publish(
        self,
        event_type: Event[ParamsT, MessageT],
        params: ParamsT,
        payload: MessageT,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Publish an event.

        Args:
            event_type: The event type.
            params: The parameters for the event.
            payload: The event payload.
            headers: The event headers.

        Raises:
            RuntimeError: If the connection is not opened.

        Returns:
            None. The message is published asynchronously, and it is possible that message is never published in some cases.
        """
        await self.connection.core.publish(
            subject=event_type.channel.address.get_subject(params),
            payload=event_type.encode(payload),
            headers=headers,
        )

    async def publish_request(
        self,
        command_type: Command[ParamsT, MessageT, Any, Any],
        reply_subject: str,
        params: ParamsT,
        payload: MessageT,
        headers: dict[str, str] | None = None,
        prefix: str | None = None,
    ) -> None:
        """Publish a command.

        Args:
            command_type: The command type.
            reply_subject: The subject to use for the reply. The receiver of the command will send the reply to this subject.
            params: The parameters for the command.
            payload: The command payload.
            headers: The command headers.

        Raises:
            RuntimeError: If the connection is not opened.

        Returns:
            None. The message is published asynchronously, and it is possible that message is never published in some cases.
        """
        subject = command_type.channel.address.get_subject(params)
        if prefix is not None:
            subject = prefix + subject
        await self.connection.core.publish_request(
            subject=subject,
            reply_subject=reply_subject,
            payload=command_type.encode_request(payload),
            headers=headers,
        )

    async def request(
        self,
        command_type: Command[ParamsT, MessageT, ReplyT, ErrorT],
        params: ParamsT,
        payload: MessageT,
        headers: dict[str, str] | None = None,
        prefix: str | None = None,
    ) -> TypedReply[ParamsT, ReplyT, ErrorT]:
        """Send a command and wait for a reply.

        Args:
            command_type: The command type.
            params: The parameters for the command.
            payload: The command payload.
            headers: The command headers.

        Raises:
            RuntimeError: If the connection is not opened.
            TimeoutError: If the request times out (if no reply is received within the timeout duration)

        Returns:
            The typed reply with optional headers.
        """
        subject = command_type.channel.address.get_subject(params)
        if prefix is not None:
            subject = prefix + subject
        reply = await self.connection.core.request(
            subject=subject,
            payload=command_type.encode_request(payload),
            headers=headers,
        )
        return TypedReply.create(command_type, reply)
