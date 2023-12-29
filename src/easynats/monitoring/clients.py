from __future__ import annotations

import asyncio
import json
from dataclasses import asdict
from typing import Any, TypeVar

from nats.aio.client import Client
from nats.aio.subscription import Subscription

from .requests import (
    AccountzRequest,
    ConnzRequest,
    GatewayzRequest,
    InfoRequest,
    JszRequest,
    LeafzRequest,
    RoutezRequest,
    StatszRequest,
    SubszRequest,
    VarzRequest,
)
from .responses import (
    AccountzResponse,
    ConnzResponse,
    GatewayzResponse,
    InfoResponse,
    JszResponse,
    LeafzResponse,
    RoutezResponse,
    StatszResponse,
    SubszResponse,
    VarzsResponse,
)

T = TypeVar("T")


def _get_server_id(nc: Client) -> str:
    return nc._server_info["server_id"]  # pyright: ignore[reportPrivateUsage]


def _encode(obj: Any) -> bytes:
    if obj is None:
        return b""
    return json.dumps(asdict(obj)).encode("utf-8")


def _decode(obj: bytes, typ: type[T]) -> T:
    if typ is type(None):
        if obj and obj != b"null":
            raise ValueError("Expected empty bytes")
        return None  # type: ignore
    content = json.loads(obj)
    return typ(**content)


class SystemMonitorClient:
    def __init__(
        self,
        nc: Client,
        prefix: str = "$SYS.REQ.SERVER.PING",
    ) -> None:
        self.nc = nc
        self.prefix = prefix

    async def _receive_messages(self, sub: Subscription, msgs: list[bytes]) -> None:
        await self.nc.flush()
        async for msg in sub.messages:
            msgs.append(msg.data)

    async def _request(
        self,
        response_type: type[T],
        endpoint: str,
        params: Any,
        timeout: float = 1,
        n: int = 1,
    ) -> list[T]:
        payload = _encode(params)
        reply = self.nc.new_inbox()
        sub = await self.nc.subscribe(  # pyright: ignore[reportUnknownMemberType]
            reply, max_msgs=max(0, n)
        )
        await self.nc.publish(f"{self.prefix}.{endpoint}", payload, reply=reply)
        msgs: list[bytes] = []
        pending, done = await asyncio.wait(
            [self._receive_messages(sub, msgs)], timeout=timeout
        )
        for task in pending:
            task.cancel()
        for task in done:
            if not task.cancelled():
                if exc := task.exception():
                    raise exc
        return [_decode(msg, response_type) for msg in msgs]

    async def statsz(
        self, request: StatszRequest | None = None, timeout: float = 1, n: int = 1
    ) -> list[StatszResponse]:
        """The `STATSZ` endpoint reports per-account statistics such as the number of connections, messages/bytes in/out, etc.

        Returns:
            results as a dictionary.
        """

        return await self._request(
            StatszResponse, "STATSZ", request or StatszRequest(), timeout=timeout, n=n
        )

    async def varz(
        self, request: VarzRequest | None = None, timeout: float = 1, n: int = 1
    ) -> list[VarzsResponse]:
        """The `VARZ` endpoint returns general information about the server state and configuration.

        Example: https://demo.nats.io:8222/varz
        """
        return await self._request(
            VarzsResponse, "VARZ", request or VarzRequest(), timeout=timeout, n=n
        )

    async def connz(
        self, request: ConnzRequest | None = None, timeout: float = 1, n: int = 1
    ) -> list[ConnzResponse]:
        """The `CONNZ` endpoint reports more detailed information on current and recently closed connections.

        It uses a paging mechanism which defaults to 1024 connections.

        Returns:
            results as a dictionary.
        """
        return await self._request(
            ConnzResponse, "CONNZ", request or ConnzRequest(), timeout=timeout, n=n
        )

    async def routez(
        self, request: RoutezRequest | None = None, timeout: float = 1, n: int = 1
    ) -> list[RoutezResponse]:
        """The `ROUTEZ` endpoint reports information on active routes for a cluster.

        Returns:
            results as a dictionary.
        """
        return await self._request(
            RoutezResponse, "ROUTEZ", request or RoutezRequest(), timeout=timeout, n=n
        )

    async def gatewayz(
        self, request: GatewayzRequest | None = None, timeout: float = 1, n: int = 1
    ) -> list[GatewayzResponse]:
        """The `GATEWAYZ` endpoint reports information about gateways used to create a NATS supercluster.

        Like routes, the number of gateways are expected to be low, so there is no paging mechanism with this endpoint.

        Returns:
            results as dict
        """
        return await self._request(
            GatewayzResponse,
            "GATEWAYZ",
            request or GatewayzRequest(),
            timeout=timeout,
            n=n,
        )

    async def leafz(
        self, request: LeafzRequest | None = None, timeout: float = 1, n: int = 1
    ) -> list[LeafzResponse]:
        """The `LEAFZ` endpoint reports detailed information about the leaf node connections.

        Returns:
            results as dict
        """
        return await self._request(
            LeafzResponse, "LEAFZ", request or LeafzRequest(), timeout=timeout, n=n
        )

    async def subsz(
        self, request: SubszRequest | None = None, timeout: float = 1, n: int = 1
    ) -> list[SubszResponse]:
        """The `SUBSZ` endpoint reports detailed information about the current subscriptions and the routing data structure.

        Returns:
            results as a dictionary.
        """
        return await self._request(
            SubszResponse, "SUBSZ", request or SubszRequest(), timeout=timeout, n=n
        )

    async def jsz(
        self, request: JszRequest | None = None, timeout: float = 1, n: int = 1
    ) -> list[JszResponse]:
        """The `JSZ` endpoint reports more detailed information on JetStream.

        For accounts, it uses a paging mechanism that defaults to 1024 connections.

        NOTE: If you're in a clustered environment, it is recommended to retrieve the information
              from the stream's leader in order to get the most accurate and up-to-date data.

        Returns:
            results as a dictionary.
        """
        return await self._request(
            JszResponse, "JSZ", request or JszRequest(), timeout=timeout, n=n
        )

    async def accountz(
        self, request: AccountzRequest | None = None, timeout: float = 1, n: int = 1
    ) -> list[AccountzResponse]:
        """The `ACCOUNTZ` endpoint reports information on a server's active accounts.

        The default behavior is to return a list of all accounts known to the server.
        """
        return await self._request(
            AccountzResponse,
            "ACCOUNTZ",
            request or AccountzRequest(),
            timeout=timeout,
            n=n,
        )


class ServerMonitorClient:
    def __init__(
        self,
        nc: Client,
        server: str | None = None,
        prefix: str = "$SYS.REQ.SERVER.PING",
    ) -> None:
        self.nc = nc
        self.server = server or _get_server_id(nc)
        self.prefix = f"{prefix}.{server}"

    async def _request(
        self,
        response_type: type[T],
        endpoint: str,
        params: Any,
        timeout: float = 1,
    ) -> T:
        payload = _encode(params)
        msg = await self.nc.request(
            f"{self.prefix}.{endpoint}", payload, timeout=timeout
        )
        return _decode(msg.data, response_type)

    async def statsz(
        self, request: StatszRequest | None = None, timeout: float = 1
    ) -> StatszResponse:
        """The `STATSZ` endpoint reports per-account statistics such as the number of connections, messages/bytes in/out, etc.

        Returns:
            results as a dictionary.
        """
        return await self._request(
            StatszResponse, "STATSZ", request or StatszRequest(), timeout=timeout
        )

    async def varz(
        self, request: VarzRequest | None = None, timeout: float = 1
    ) -> VarzsResponse:
        """The `VARZ` endpoint returns general information about the server state and configuration.

        Example: https://demo.nats.io:8222/varz
        """
        return await self._request(
            VarzsResponse, "VARZ", request or VarzRequest(), timeout=timeout
        )

    async def connz(
        self, request: ConnzRequest | None = None, timeout: float = 1, n: int = 1
    ) -> ConnzResponse:
        """The `CONNZ` endpoint reports more detailed information on current and recently closed connections.

        It uses a paging mechanism which defaults to 1024 connections.

        Returns:
            results as a dictionary.
        """
        return await self._request(
            ConnzResponse, "CONNZ", request or ConnzRequest(), timeout=timeout
        )

    async def routez(
        self, request: RoutezRequest | None = None, timeout: float = 1
    ) -> RoutezResponse:
        """The `ROUTEZ` endpoint reports information on active routes for a cluster.

        Returns:
            results as a dictionary.
        """
        return await self._request(
            RoutezResponse, "ROUTEZ", request or RoutezRequest(), timeout=timeout
        )

    async def gatewayz(
        self, request: GatewayzRequest | None = None, timeout: float = 1
    ) -> GatewayzResponse:
        """The `GATEWAYZ` endpoint reports information about gateways used to create a NATS supercluster.

        Like routes, the number of gateways are expected to be low, so there is no paging mechanism with this endpoint.

        Returns:
            results as dict
        """
        return await self._request(
            GatewayzResponse, "GATEWAYZ", request or GatewayzRequest(), timeout=timeout
        )

    async def leafz(
        self, request: LeafzRequest | None = None, timeout: float = 1
    ) -> LeafzResponse:
        """The `LEAFZ` endpoint reports detailed information about the leaf node connections.

        Returns:
            results as dict
        """
        return await self._request(
            LeafzResponse, "LEAFZ", request or LeafzRequest(), timeout=timeout
        )

    async def subsz(
        self, request: SubszRequest | None = None, timeout: float = 1
    ) -> SubszResponse:
        """The `SUBSZ` endpoint reports detailed information about the current subscriptions and the routing data structure.

        Returns:
            results as a dictionary.
        """
        return await self._request(
            SubszResponse, "SUBSZ", request or SubszRequest(), timeout=timeout
        )

    async def jsz(
        self, request: JszRequest | None = None, timeout: float = 1
    ) -> JszResponse:
        """The `JSZ` endpoint reports more detailed information on JetStream.

        For accounts, it uses a paging mechanism that defaults to 1024 connections.

        NOTE: If you're in a clustered environment, it is recommended to retrieve the information
              from the stream's leader in order to get the most accurate and up-to-date data.

        Returns:
            results as a dictionary.
        """
        return await self._request(
            JszResponse, "JSZ", request or JszRequest(), timeout=timeout
        )

    async def accountz(
        self, request: AccountzRequest | None = None, timeout: float = 1
    ) -> AccountzResponse:
        """The `ACCOUNTZ` endpoint reports information on a server's active accounts.

        The default behavior is to return a list of all accounts known to the server.
        """
        return await self._request(
            AccountzResponse, "ACCOUNTZ", request or AccountzRequest(), timeout=timeout
        )


class AccountMonitorClient:
    def __init__(
        self,
        nc: Client,
        account_id: str | None = None,
    ) -> None:
        self.nc = nc
        self.account_id = account_id
        self.prefix = "$SYS.REQ.ACCOUNT"
        if self.account_id:
            self.prefix += f".{self.account_id}"

    async def _request(
        self,
        response_type: type[T],
        endpoint: str,
        params: Any,
        timeout: float = 1,
    ) -> T:
        payload = _encode(params)
        msg = await self.nc.request(
            f"{self.prefix}.{endpoint}", payload, timeout=timeout
        )
        return _decode(msg.data, response_type)

    async def connz(self, options: ConnzRequest | None = None) -> ConnzResponse:
        """The `$SYS.REQ.ACCOUNT.<account-id>.CONNZ` endpoint reports more detailed information on current and recently closed connections.

        It uses a paging mechanism which defaults to 1024 connections.

        Returns:
            results as a dictionary.
        """
        return await self._request(ConnzResponse, "CONNZ", options or ConnzRequest())

    async def leafz(self, options: LeafzRequest | None = None) -> LeafzResponse:
        """The `$SYS.REQ.ACCOUNT.<account-id>.LEAFZ` endpoint reports detailed information about the leaf node connections.

        Returns:
            results as dict
        """
        return await self._request(LeafzResponse, "LEAFZ", options or LeafzRequest())

    async def subsz(self, options: SubszRequest | None = None) -> SubszResponse:
        """The /subsz endpoint reports detailed information about the current subscriptions and the routing data structure.

        Returns:
            results as a dictionary.
        """
        return await self._request(SubszResponse, "SUBSZ", options or SubszRequest())

    async def jsz(self, options: JszRequest | None = None) -> dict[str, Any]:
        """The `$SYS.REQ.ACCOUNT.<account-id>.JSZ` endpoint reports more detailed information on JetStream.

        For accounts, it uses a paging mechanism that defaults to 1024 connections.

        NOTE: If you're in a clustered environment, it is recommended to retrieve the information
              from the stream's leader in order to get the most accurate and up-to-date data.

        Returns:
            results as a dictionary.
        """
        return await self._request(JszResponse, "JSZ", options or JszRequest())

    async def info(self, request: InfoRequest | None = None) -> dict[str, Any]:
        """The `$SYS.REQ.ACCOUNT.<account-id>.INFO` endpoint reports information on a server's active accounts.

        The default behavior is to return a list of all accounts known to the server.
        """
        return await self._request(InfoResponse, "INFO", request or InfoRequest())
