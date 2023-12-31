from __future__ import annotations

import abc
import ssl
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Awaitable, Callable

try:
    import nkeys  # type: ignore

    __NKEYS_AVAILABLE__ = True
except ModuleNotFoundError:
    __NKEYS_AVAILABLE__ = False  # type: ignore


@dataclass
class ConnectOpts:
    """Connect options for NATS python client."""

    servers: str | list[str] = "nats://localhost:4222"
    name: str | None = None
    dont_randomize: bool = False
    inbox_prefix: str | bytes = b"_INBOX"  # Note: No trailing "." in inbox prefix
    pedantic: bool = False
    verbose: bool = False
    no_echo: bool = False
    # First connect
    connect_timeout: float = 2  # seconds
    # Drain
    drain_timeout: float = 30  # seconds
    # Reconnect
    allow_reconnect: bool = True
    max_reconnect_attempts: int = -1  # -1 for infinite
    reconnect_time_wait: float = 2  # seconds
    # PingPong
    ping_interval: float = 60  # seconds
    max_outstanding_pings: int = 2
    # Pending queue
    pending_size: int = 1024 * 1024 * 2  # bytes (2MiB)
    # Flusher
    flusher_queue_size: int = 1024
    flush_timeout: float | None = None
    # tls
    tls: ssl.SSLContext | None = None
    tls_hostname: str | None = None
    # Auth
    user: str | None = None
    password: str | None = None
    token: str | None = None
    user_credentials: str | tuple[str, str] | None = None
    nkeys_seed: str | None = None
    signature_cb: Callable[[str], bytes] | None = None
    user_jwt_cb: Callable[[], bytearray | bytes] | None = None
    # Connection state callbacks
    error_cb: Callable[[Exception], Awaitable[None]] | None = None
    disconnected_cb: Callable[[], Awaitable[None]] | None = None
    closed_cb: Callable[[], Awaitable[None]] | None = None
    discovered_server_cb: Callable[[], Awaitable[None]] | None = None
    reconnected_cb: Callable[[], Awaitable[None]] | None = None

    def dict(self) -> dict[str, Any]:
        """Return a dictionary representation of the connect options."""
        return asdict(self)

    @classmethod
    def from_dict(cls, opts: dict[str, Any]) -> ConnectOpts:
        """Update the connect options from a dictionary."""
        return cls(**opts)


class ConnectOption(metaclass=abc.ABCMeta):
    """Base class for connect options.

    A connect option is a callable which can transform a
    [`ConnectOpts`][] object.

    For example, the [`WithServer`][] connect option can be used
    to specify the server URL:

    ```python
        easynats.connect(WithServer("nats://localhost:4222"))
    ```
    """

    @abc.abstractmethod
    def apply(self, opts: ConnectOpts) -> None:
        raise NotImplementedError


@dataclass
class WithServer(ConnectOption):
    url: str

    def apply(self, opts: ConnectOpts) -> None:
        opts.servers = self.url


@dataclass
class WithServers(ConnectOption):
    urls: list[str]

    def apply(self, opts: ConnectOpts) -> None:
        opts.servers = self.urls


@dataclass
class WithConnectionName(ConnectOption):
    name: str

    def apply(self, opts: ConnectOpts) -> None:
        opts.name = self.name


class WithDeterministicServers(ConnectOption):
    def apply(self, opts: ConnectOpts) -> None:
        opts.dont_randomize = True


@dataclass
class WithInboxPrefix(ConnectOption):
    prefix: str | bytes

    def apply(self, opts: ConnectOpts) -> None:
        if isinstance(self.prefix, str):
            opts.inbox_prefix = self.prefix.encode("utf-8")
        else:
            opts.inbox_prefix = self.prefix


class WithPedanticMode(ConnectOption):
    def apply(self, opts: ConnectOpts) -> None:
        opts.pedantic = True


class WithVerboseLogging(ConnectOption):
    def apply(self, opts: ConnectOpts) -> None:
        opts.verbose = True


class WithNoEcho(ConnectOption):
    def apply(self, opts: ConnectOpts) -> None:
        opts.no_echo = True


@dataclass
class WithConnectTimeout(ConnectOption):
    timeout: float

    def apply(self, opts: ConnectOpts) -> None:
        opts.connect_timeout = self.timeout


@dataclass
class WithDrainTimeout(ConnectOption):
    timeout: float

    def apply(self, opts: ConnectOpts) -> None:
        opts.drain_timeout = self.timeout


@dataclass
class WithAllowReconnect(ConnectOption):
    max_attempts: int = -1
    delay_seconds: float = 2

    def apply(self, opts: ConnectOpts) -> None:
        opts.allow_reconnect = True
        opts.max_reconnect_attempts = self.max_attempts
        opts.reconnect_time_wait = self.delay_seconds


@dataclass
class WithPingPong(ConnectOption):
    interval: float = 60
    max_outstanding: int = 2

    def apply(self, opts: ConnectOpts) -> None:
        opts.ping_interval = self.interval
        opts.max_outstanding_pings = self.max_outstanding


@dataclass
class WithPendingQueue(ConnectOption):
    max_bytes: int = 1024 * 1024 * 2  # bytes (2MiB)

    def apply(self, opts: ConnectOpts) -> None:
        opts.pending_size = self.max_bytes


@dataclass
class WithFlusher(ConnectOption):
    queue_size: int = 1024
    timeout: float = 10

    def apply(self, opts: ConnectOpts) -> None:
        opts.flusher_queue_size = self.queue_size
        opts.flush_timeout = self.timeout


@dataclass
class WithTLSCertificate(ConnectOption):
    cert_file: str
    key_file: str
    ca_file: str | None = None
    key_file_password: str | None = None
    hostname: str | None = None

    def apply(self, opts: ConnectOpts) -> None:
        if self.ca_file:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.load_verify_locations(
                self.ca_file,
            )
        else:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(
            self.cert_file,
            self.key_file,
            self.key_file_password,
        )
        opts.tls = context
        if self.hostname:
            opts.tls_hostname = self.hostname


@dataclass
class WithUserPassword(ConnectOption):
    user: str
    password: str

    def apply(self, opts: ConnectOpts) -> None:
        opts.user = self.user
        opts.password = self.password


@dataclass
class WithUsername(ConnectOption):
    user: str

    def apply(self, opts: ConnectOpts) -> None:
        opts.user = self.user


@dataclass
class WithPassword(ConnectOption):
    password: str

    def apply(self, opts: ConnectOpts) -> None:
        opts.password = self.password


@dataclass
class WithToken(ConnectOption):
    token: str

    def apply(self, opts: ConnectOpts) -> None:
        opts.token = self.token


@dataclass
class WithCredentialsFile(ConnectOption):
    filepath: str

    def apply(self, opts: ConnectOpts) -> None:
        path = Path(self.filepath).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Credentials file not found: {path}")
        opts.user_credentials = path.as_posix()


@dataclass
class WithNKeySeed(ConnectOption):
    seed: str

    def apply(self, opts: ConnectOpts) -> None:
        opts.nkeys_seed = self.seed


@dataclass
class WithNKeyFile(ConnectOption):
    filepath: str

    def apply(self, opts: ConnectOpts) -> None:
        path = Path(self.filepath).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"NKey file not found: {path}")
        opts.nkeys_seed = path.read_text()


@dataclass
class WithSignatureCallback(ConnectOption):
    callback: Callable[[str], bytes]

    def apply(self, opts: ConnectOpts) -> None:
        opts.signature_cb = self.callback


@dataclass
class WithUserJwtCallback(ConnectOption):
    callback: Callable[[], bytearray | bytes]

    def apply(self, opts: ConnectOpts) -> None:
        opts.user_jwt_cb = self.callback


@dataclass
class WithNKeySeedAndJwt(ConnectOption):
    seed: str
    jwt: str

    def apply(self, opts: ConnectOpts) -> None:
        if not __NKEYS_AVAILABLE__:
            raise ModuleNotFoundError("nkeys module not installed")
        nkey = nkeys.from_seed(self.seed.encode())  # type: ignore
        opts.signature_cb = lambda nonce: nkey.sign(nonce.encode())  # type: ignore
        opts.user_jwt_cb = lambda: self.jwt.encode()


@dataclass
class WithNkeyFileAndJwtFile(ConnectOption):
    nkey_file: str
    jwt_file: str

    def apply(self, opts: ConnectOpts) -> None:
        return WithNKeySeedAndJwt(
            Path(self.nkey_file).read_text(),
            Path(self.jwt_file).read_text(),
        ).apply(opts)


@dataclass
class WithErrorCallback(ConnectOption):
    callback: Callable[[Exception], Awaitable[None]]

    def apply(self, opts: ConnectOpts) -> None:
        opts.error_cb = self.callback


@dataclass
class WithDisconnectedCallback(ConnectOption):
    callback: Callable[[], Awaitable[None]]

    def apply(self, opts: ConnectOpts) -> None:
        opts.disconnected_cb = self.callback


@dataclass
class WithReconnectedCallback(ConnectOption):
    callback: Callable[[], Awaitable[None]]

    def apply(self, opts: ConnectOpts) -> None:
        opts.reconnected_cb = self.callback


@dataclass
class WithConnectionClosedCallback(ConnectOption):
    callback: Callable[[], Awaitable[None]]

    def apply(self, opts: ConnectOpts) -> None:
        opts.closed_cb = self.callback


@dataclass
class WithServerDiscoveredCallback(ConnectOption):
    callback: Callable[[], Awaitable[None]]

    def apply(self, opts: ConnectOpts) -> None:
        opts.discovered_server_cb = self.callback


@dataclass
class WithCallbacks(ConnectOption):
    on_error: Callable[[Exception], Awaitable[None]] | None = None
    on_disconnection: Callable[[], Awaitable[None]] | None = None
    on_connection_closed: Callable[[], Awaitable[None]] | None = None
    on_server_discovered: Callable[[], Awaitable[None]] | None = None
    on_reconnection: Callable[[], Awaitable[None]] | None = None

    def apply(self, opts: ConnectOpts) -> None:
        if self.on_error:
            opts.error_cb = self.on_error
        if self.on_disconnection:
            opts.disconnected_cb = self.on_disconnection
        if self.on_connection_closed:
            opts.closed_cb = self.on_connection_closed
        if self.on_server_discovered:
            opts.discovered_server_cb = self.on_server_discovered
        if self.on_reconnection:
            opts.reconnected_cb = self.on_reconnection
