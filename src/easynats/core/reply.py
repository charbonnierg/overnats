from __future__ import annotations

import abc

from .msg import Msg, MsgImpl, NatsMsg


class ReplyMsg(Msg):
    """The reply message interface.

    This interface is used to represent a reply message.

    This class is an abstract class so it cannot be instantiated.

    However, it should be used as a type hint for any function that
    accepts a reply message as an argument.

    Using an interface instead of a concrete class allows you to
    create your own implementation of the message class (e.g. for
    testing purposes, or to add additional functionality).
    """

    @abc.abstractmethod
    def origin_subject(self) -> str:
        """Get the origin subject of message.

        Returns:
            The origin subject of message as a string.
        """


class ReplyMsgImpl(MsgImpl, ReplyMsg):
    def __init__(self, origin_subject: str, msg: NatsMsg) -> None:
        super().__init__(msg)
        self._origin = origin_subject

    def origin_subject(self) -> str:
        return self._origin
