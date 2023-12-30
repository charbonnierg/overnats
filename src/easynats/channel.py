from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

from pydantic.type_adapter import TypeAdapter

from .address import Address

if TYPE_CHECKING:
    from .connection import Reply


ParamsT = TypeVar("ParamsT")
MessageT = TypeVar("MessageT")
ReplyT = TypeVar("ReplyT")
ErrorT = TypeVar("ErrorT")


class Channel(Generic[ParamsT]):
    def __init__(
        self,
        subject: str,
        parameters: type[ParamsT],
    ) -> None:
        """Create a new channel.

        Args:
            subject: The subject filter.
            parameters: The parameters expected to be found on each valid subject matching subject filter.
                Parameters must be a dataclass or a class with a `__fields__` attribute such as `pydantic.BaseModel`.
        """
        self.address = Address(subject, parameters)
        self.receives: list[Event[ParamsT, Any] | Command[ParamsT, Any, Any, Any]] = []
        self.emits: list[Event[ParamsT, Any]] = []


class Event(Generic[ParamsT, MessageT]):
    def __init__(
        self,
        channel: Channel[ParamsT],
        message: type[MessageT],
    ) -> None:
        """Define a new event.

        Args:
            channel: The channel on which event can be published/subscribed to.
            message: The type of data found within this event.
        """
        self.channel = channel
        self.message = message
        self._type_adapter = TypeAdapter(message)

    def encode(self, message: MessageT) -> bytes:
        """Encode event data into bytes.

        Child classes may override this method to customize
        event data encoding.

        By default `json.dumps` is used to serialize
        python objects as string, before calling `str.encode`
        to encode string as bytes.

        Raises:
            ValueError: when event data cannot be serialized

        Returns:
            The encoded event data as bytes.
        """
        return self._type_adapter.dump_json(message)

    def decode(self, data: bytes) -> MessageT:
        """Decode event data from bytes.

        Child classes may override this method to customize
        message data decoding.

        By default `json.loads` is used to serialize
        bytes string into a python object, before calling
        the class constructor of the message type.

        Raises:
            ValueError: when event data cannot be decoded.

        Returns:
            The decoded event data as a python object.
        """
        return self._type_adapter.validate_json(data)


class Command(Generic[ParamsT, MessageT, ReplyT, ErrorT]):
    def __init__(
        self,
        channel: Channel[ParamsT],
        message: type[MessageT],
        reply: type[ReplyT],
        error: type[ErrorT],
    ) -> None:
        """Create a new command.

        Args:
            channel: The channel on which command can be requested/subscribed to.
            message: The type of data found within command request.
            reply: The type of data found within command success reply.
            error: The type of data found within command error reply.
        """
        self.channel = channel
        self.message = message
        self.reply = reply
        self.error = error
        self._request_type_adapter = TypeAdapter(message)
        self._reply_type_adapter = TypeAdapter(reply)
        self._error_type_adapter = TypeAdapter(error)

    def encode_request(self, message: MessageT) -> bytes:
        """Encode request data into bytes.

        Child classes may override this method to customize
        request data encoding.

        By default `json.dumps` is used to serialize
        python objects as string, before calling `str.encode`
        to encode string as bytes.

        Raises:
            ValueError: when request data cannot be encoded.

        Returns:
            The encoded request data as bytes.
        """
        return self._request_type_adapter.dump_json(message)

    def decode_request(self, data: bytes) -> MessageT:
        """Decode request data from bytes.

        Child classes may override this method to customize
        request data decoding.

        By default `json.loads` is used to decode
        bytes string into a python object, before calling
        the class constructor of the request data type.

        Raises:
            ValueError: when request data cannot be decoded.

        Returns:
            The decoded request data as a python object.
        """
        return self._request_type_adapter.validate_json(data)

    def encode_reply(self, reply: ReplyT) -> bytes:
        """Encode reply data into bytes.

        Child classes may override this method to customize
        reply data encoding.

        By default `json.dumps` is used to serialize
        python objects as string, before calling `str.encode`
        to encode string as bytes.

        Raises:
            ValueError: when reply data cannot be encoded.

        Returns:
            The encoded reply data as bytes.
        """
        return self._reply_type_adapter.dump_json(reply)

    def decode_reply(self, data: bytes) -> ReplyT:
        """Decode reply data from bytes.

        Child classes may override this method to customize
        reply data decoding.

        By default `json.loads` is used to decode
        bytes string into a python object, before calling
        the class constructor of the reply data type.

        Raises:
            ValueError: when reply data cannot be decoded.

        Args:
            data: the reply

        Returns:
            The decoded reply data as a python object.
        """
        return self._reply_type_adapter.validate_json(data)

    def encode_error(self, error: ErrorT) -> bytes:
        """Encode error data into bytes.

        Child classes may override this method to customize
        error data encoding.

        By default `json.dumps` is used to serialize
        python objects as string, before calling `str.encode`
        to encode string as bytes.

        Raises:
            ValueError: when error data cannot be encoded.

        Args:
            error: the error python object to encode into bytes.

        Returns:
            The encoded error data as bytes.
        """
        return self._error_type_adapter.dump_json(error)

    def decode_error(self, data: bytes) -> ErrorT:
        """Decode error data from bytes.

        Child classes may override this method to customize
        error data decoding.

        By default `json.loads` is used to decode
        bytes string into a python object, before calling
        the class constructor of the error data type.

        Args:
            data: the bytes data to decode into an error.

        Raises:
            ValueError: when error data cannot be decoded.

        Returns:
            The decoded reply data as a python object.
        """
        return self._error_type_adapter.validate_json(data)

    def is_success(self, reply: Reply) -> bool:
        """Returns True if headers indicate a success else False.

        Child classes may override this method to customize parsing of
        success and errors.

        By default:

        - the `Nats-Service-Error-Code` header is looked for (case insensitive). If header exists,
            reply is considered an error.

        -  the `Status` header is looked for (case insensitive). If `status` header is found and is equal to one of:
                - `"success"`
                - `"200"`
                - `"201"`
                - `"202"`
                - `"204"`

            Then reply is considered a success, else reply is considered an error.

        If reply does not have header, or `status` header is not defined, reply
        is considered a success.
        """
        if not reply.headers:
            return True
        for key in reply.headers:
            if key.lower() == "Nats-Service-Error-Code":
                return False
            if key.lower() == "status":
                return reply.headers[key] in ("success", "200", "201", "202", "204")
        return True
