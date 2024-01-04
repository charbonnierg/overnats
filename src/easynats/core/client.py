from __future__ import annotations

from typing import Awaitable, Callable

import nats.js.api
from nats.aio.client import _CRLF_  # pyright: ignore[reportPrivateUsage]
from nats.aio.client import _CRLF_LEN_  # pyright: ignore[reportPrivateUsage]
from nats.aio.client import _SPC_BYTE_  # pyright: ignore[reportPrivateUsage]
from nats.aio.client import NATS_HDR_LINE, NATS_HDR_LINE_SIZE, STATUS_MSG_LEN
from nats.aio.client import Client as NatsClient

from .msg import Msg
from .reply import ReplyMsg, ReplyMsgImpl
from .subscriptions import SubscriptionHandler, SubscriptionIterator


class CoreClient:
    def __init__(self, client: NatsClient) -> None:
        self.client = client

    async def flush(self) -> None:
        """Flush the connection.

        This method can only be called after the connection is opened,
        otherwise a `RuntimeError` is raised.

        Raises:
            RuntimeError: If the connection is not opened.

        Returns:
            None
        """
        await self.client.flush()

    async def publish(
        self,
        subject: str,
        payload: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Publish a message to a subject.

        This method can only be called after the connection is opened,
        otherwise a `RuntimeError` is raised.

        Args:
            subject: The subject to publish to.
            payload: The message payload. If `None`, an empty payload (`b""`) is used.
            headers: The message headers. If `None`, no headers are used.

        Raises:
            RuntimeError: If the connection is not opened.

        Returns:
            None. The message is published asynchronously, and it is possible that message is never published in some cases.
        """
        await self.client.publish(
            subject=subject,
            payload=payload or b"",
            headers=headers,
        )

    async def request(
        self,
        subject: str,
        payload: bytes | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> ReplyMsg:
        """Send a request and wait for a reply.

        This method can only be called after the connection is opened,
        otherwise a `RuntimeError` is raised.

        Args:
            subject: The subject to send the request to.
            payload: The request payload. If `None`, an empty payload (`b""`) is used.
            headers: The request headers. If `None`, no headers are used.

        Raises:
            RuntimeError: If the connection is not opened.
            TimeoutError: If the request times out (if no reply is received within the timeout duration)

        Returns:
            The reply with optional data and headers.
        """
        msg = await self.client.request(
            subject, payload or b"", headers=headers, timeout=timeout or float("inf")
        )
        return ReplyMsgImpl(subject, msg)

    async def publish_request(
        self,
        subject: str,
        reply_subject: str,
        payload: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Send a request indicating a reply subject and do not wait for a reply.

        This method can only be called after the connection is opened,
        otherwise a `RuntimeError` is raised.

        Args:
            subject: The subject to send the request to.
            reply_subject: The subject to use for the reply. The receiver of the request will send the reply to this subject.
            payload: The request payload. If `None`, an empty payload (`b""`) is used.
            headers: The request headers. If `None`, no headers are used.

        Raises:
            RuntimeError: If the connection is not opened.

        Returns:
            None. The message is published asynchronously, and it is possible that message is never published in some cases.
        """
        await self.client.publish(
            subject=subject,
            reply=reply_subject,
            payload=payload or b"",
            headers=headers,
        )

    def subscribe_with_callback(
        self,
        subject: str,
        callback: Callable[[Msg], Awaitable[None]],
        queue: str | None = None,
        drain_on_exit: bool = True,
    ) -> SubscriptionHandler:
        return SubscriptionHandler(
            client=self.client,
            subject=subject,
            callback=callback,
            queue=queue,
            drain_on_exit=drain_on_exit,
        )

    def subscribe(
        self,
        subject: str,
        queue: str | None = None,
        drain_on_exit: bool = True,
    ) -> SubscriptionIterator:
        return SubscriptionIterator(
            client=self.client,
            subject=subject,
            queue=queue,
            drain_on_exit=drain_on_exit,
        )

    def new_inbox(self) -> str:
        return self.client.new_inbox()

    def parse_headers(self, headers: bytes) -> dict[str, str]:
        if not headers:
            return {}
        nc = self.client
        hdr: dict[str, str] | None = None
        raw_headers = headers[NATS_HDR_LINE_SIZE:]

        # If the first character is an empty space, then this is
        # an inline status message sent by the server.
        #
        # NATS/1.0 404\r\n\r\n
        # NATS/1.0 503\r\n\r\n
        # NATS/1.0 404 No Messages\r\n\r\n
        #
        # Note: it is possible to receive a message with both inline status
        # and a set of headers.
        #
        # NATS/1.0 100\r\nIdle Heartbeat\r\nNats-Last-Consumer: 1016\r\nNats-Last-Stream: 1024\r\n\r\n
        #
        if raw_headers[0] == _SPC_BYTE_:
            # Special handling for status messages.
            line = headers[len(NATS_HDR_LINE) + 1 :]
            status = line[:STATUS_MSG_LEN]
            desc = line[STATUS_MSG_LEN + 1 : len(line) - _CRLF_LEN_ - _CRLF_LEN_]
            stripped_status = status.strip().decode()

            # Process as status only when it is a valid integer.
            hdr = {}
            if stripped_status.isdigit():
                hdr[nats.js.api.Header.STATUS.value] = stripped_status

            # Move the raw_headers to end of line
            i = raw_headers.find(_CRLF_)
            raw_headers = raw_headers[i + _CRLF_LEN_ :]

            if len(desc) > 0:
                # Heartbeat messages can have both headers and inline status,
                # check that there are no pending headers to be parsed.
                i = desc.find(_CRLF_)
                if i > 0:
                    hdr[nats.js.api.Header.DESCRIPTION] = desc[:i].decode()
                    parsed_hdr = nc._hdr_parser.parsebytes(  # pyright: ignore[reportPrivateUsage]
                        desc[i + _CRLF_LEN_ :]
                    )
                    for k, v in parsed_hdr.items():
                        hdr[k] = v
                else:
                    # Just inline status...
                    hdr[nats.js.api.Header.DESCRIPTION] = desc.decode()

        if not len(raw_headers) > _CRLF_LEN_:
            return hdr or {}

        #
        # Example header without status:
        #
        # NATS/1.0\r\nfoo: bar\r\nhello: world
        #
        raw_headers = headers[NATS_HDR_LINE_SIZE + _CRLF_LEN_ :]
        parsed_hdr = {
            k.strip(): v.strip()
            for k, v in nc._hdr_parser.parsebytes(  # pyright: ignore[reportPrivateUsage]
                raw_headers
            ).items()
        }
        if hdr:
            hdr.update(parsed_hdr)
        else:
            hdr = parsed_hdr

        return hdr or {}
