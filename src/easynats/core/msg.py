from __future__ import annotations

import abc

from nats.aio.msg import Msg as NatsMsg


class Msg(metaclass=abc.ABCMeta):
    """Interface for message.

    This class is an abstract class so it cannot be instantiated.

    However, it should be used as a type hint for any function that
    accepts a message as an argument.

    Using an interface instead of a concrete class allows you to
    create your own implementation of the message class (e.g. for
    testing purposes, or to add additional functionality).
    """

    @abc.abstractmethod
    def subject(self) -> str:
        """Get the subject of message.

        Returns:
            The subject of message as a string.
        """

    @abc.abstractmethod
    def payload(self) -> bytes:
        """Get the binary payload of message.

        Returns:
            The payload of message as bytes.
        """

    @abc.abstractmethod
    def headers(self) -> dict[str, str]:
        """Get the headers of message.

        Returns:
            The headers of message as a dict.
        """

    @abc.abstractmethod
    def reply_subject(self) -> str | None:
        """Get the reply subject of message.

        Returns:
            The reply subject of message as a string.
        """

    @abc.abstractmethod
    async def respond(
        self, payload: bytes, headers: dict[str, str] | None = None
    ) -> None:
        """Send a response to the message.

        Args:
            payload: The payload of response.
            headers: The headers of response.

        Returns:
            None
        """


class MsgImpl(Msg):
    def __init__(self, msg: NatsMsg) -> None:
        self.nats_msg = msg

    def subject(self) -> str:
        return self.nats_msg.subject

    def payload(self) -> bytes:
        return self.nats_msg.data

    def headers(self) -> dict[str, str]:
        return self.nats_msg.headers or {}

    def reply_subject(self) -> str | None:
        return self.nats_msg.reply

    async def respond(self, payload: bytes, headers: dict[str, str] | None = None):
        await self.nats_msg._client.publish(self.nats_msg.reply, payload, headers=headers)  # type: ignore[protected-access]
