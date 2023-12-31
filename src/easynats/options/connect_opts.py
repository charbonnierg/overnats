"""Connect options for NATS python client."""
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
    """Connect options for NATS python client.

    Args:
        servers: A single server URL or a list of server URLs.
        name: The connection name.
        dont_randomize: Disable randomizing the server list.
        inbox_prefix: The inbox prefix to use.
        pedantic: Enable pedantic mode.
        verbose: Enable verbose logging.
        no_echo: Disable echo.
        connect_timeout: The connection timeout in seconds.
        drain_timeout: The drain timeout in seconds.
        allow_reconnect: Enable automatic reconnection.
        max_reconnect_attempts: The maximum number of reconnection attempts. `-1` for infinite.
        reconnect_time_wait: The delay between reconnection attempts in seconds.
        ping_interval: The ping interval in seconds.
        max_outstanding_pings: The maximum number of outstanding pings before closing the connection.
        pending_size: The maximum size of the pending queue in bytes.
        flusher_queue_size: The size of the flusher queue in number of messages.
        flush_timeout: The flusher timeout in seconds.
        tls: The TLS context to use.
        tls_hostname: The hostname to use for TLS verification.
        user: The username to use for authentication.
        password: The password to use for authentication.
        token: The token to use for authentication.
        user_credentials: The path to the credentials file to use for authentication.
        nkeys_seed: The nkeys seed to use for authentication.
        signature_cb: The callback function to sign the nonce during authentication.
        user_jwt_cb: The callback function to return the jwt during authentication.
        error_cb: The callback function to call each time an error occurs.
        disconnected_cb: The callback function to call each time connection is lost.
        closed_cb: The callback function to call once connection is closed.
        discovered_server_cb: The callback function to call each time a new server is discovered.
        reconnected_cb: The callback function to call each time connection is reestablished.
    """

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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, opts: dict[str, Any]) -> ConnectOpts:
        return cls(**opts)


class ConnectOption(metaclass=abc.ABCMeta):
    """Base class for connect options.

    A connect option is a callable which can transform a
    [`ConnectOpts`][easynats.options.connect_opts.ConnectOpts] object.

    For example, the [`WithServer`][easynats.options.connect_opts.WithServer]
    connect option can be used to specify the server URL:

    ```python
        easynats.connect(
            WithServer("nats://localhost:4222")
        )
    ```

    It's possible to use the [`configure()` method][easynats.connection.Connection.configure] method on
    the [`Connection` class][easynats.connection.Connection] to add connect options:

    ```python
        nc = easynats.Connection()
        nc.configure(
            WithServer("nats://localhost:4222")
        )
    ```

    Custom connect options can be provided by creating a function
    which takes a [`ConnectOpts`][easynats.options.connect_opts.ConnectOpts] object as an argument and
    returns `None`:

    ```python
        def use_custom_options(opts: ConnectOpts) -> None:
            # Do something with opts. For example set the name:
            opts.name = "my-connection"

        nc.configure(use_custom_options)
    ```

    See the [`easynats.options.connect_opts`][easynats.options.connect_opts] module for a list of available connect options.
    """

    @abc.abstractmethod
    def __call__(self, opts: ConnectOpts) -> None:
        raise NotImplementedError


@dataclass
class WithServer(ConnectOption):
    """Connect option to specify the server URL.

    Args:
        url: The server URL to connect to.
    """

    url: str

    def __call__(self, opts: ConnectOpts) -> None:
        opts.servers = self.url


@dataclass
class WithServers(ConnectOption):
    """Connect option to specify the server URLs.

    Args:
        urls: The server URLs to connect to.
    """

    urls: list[str]

    def __call__(self, opts: ConnectOpts) -> None:
        opts.servers = self.urls


@dataclass
class WithConnectionName(ConnectOption):
    """Connect option to specify the connection name.

    Args:
        name: The connection name to use.
    """

    name: str

    def __call__(self, opts: ConnectOpts) -> None:
        opts.name = self.name


class WithDeterministicServers(ConnectOption):
    """Connect option to disable randomizing the server list."""

    def __call__(self, opts: ConnectOpts) -> None:
        opts.dont_randomize = True


@dataclass
class WithInboxPrefix(ConnectOption):
    """Connect option to specify the inbox prefix.

    Args:
        prefix: The inbox prefix to use.
    """

    prefix: str | bytes

    def __call__(self, opts: ConnectOpts) -> None:
        if isinstance(self.prefix, str):
            opts.inbox_prefix = self.prefix.encode("utf-8")
        else:
            opts.inbox_prefix = self.prefix


class WithPedanticMode(ConnectOption):
    """Connect option to enable pedantic mode."""

    def __call__(self, opts: ConnectOpts) -> None:
        opts.pedantic = True


class WithVerboseLogging(ConnectOption):
    """Connect option to enable verbose logging."""

    def __call__(self, opts: ConnectOpts) -> None:
        opts.verbose = True


class WithNoEcho(ConnectOption):
    """Connect option to disable echo."""

    def __call__(self, opts: ConnectOpts) -> None:
        opts.no_echo = True


@dataclass
class WithConnectTimeout(ConnectOption):
    """Connect option to specify the connection timeout.

    Args:
        timeout: The connection timeout in seconds.
    """

    timeout: float

    def __call__(self, opts: ConnectOpts) -> None:
        opts.connect_timeout = self.timeout


@dataclass
class WithDrainTimeout(ConnectOption):
    """Connect option to specify the drain timeout.

    Args:
        timeout: The drain timeout in seconds.
    """

    timeout: float

    def __call__(self, opts: ConnectOpts) -> None:
        opts.drain_timeout = self.timeout


@dataclass
class WithDisallowReconnect(ConnectOption):
    """Connect option to disable automatic reconnection."""

    def __call__(self, opts: ConnectOpts) -> None:
        opts.allow_reconnect = False


@dataclass
class WithAllowReconnect(ConnectOption):
    """Connect option to enable automatic reconnection.

    The default is to allow reconnection, so this option is only needed
    to override a previous [`WithDisallowReconnect`][easynats.options.connect_opts.WithDisallowReconnect]
    connect option or to configure the reconnection options.

    Args:
        max_attempts: The maximum number of reconnection attempts. `-1` for infinite.
        delay_seconds: The delay between reconnection attempts in seconds.
    """

    max_attempts: int = -1
    delay_seconds: float = 2

    def __call__(self, opts: ConnectOpts) -> None:
        opts.allow_reconnect = True
        opts.max_reconnect_attempts = self.max_attempts
        opts.reconnect_time_wait = self.delay_seconds


@dataclass
class WithPingPong(ConnectOption):
    """Connect option to configure ping/pong.

    Args:
        interval: The ping interval in seconds.
        max_outstanding: The maximum number of outstanding pings before closing the connection.
    """

    interval: float = 60
    max_outstanding: int = 2

    def __call__(self, opts: ConnectOpts) -> None:
        opts.ping_interval = self.interval
        opts.max_outstanding_pings = self.max_outstanding


@dataclass
class WithPendingQueue(ConnectOption):
    """Connect option to configure the pending queue.

    Args:
        max_bytes: The maximum size of the pending queue in bytes.
    """

    max_bytes: int = 1024 * 1024 * 2  # bytes (2MiB)

    def __call__(self, opts: ConnectOpts) -> None:
        opts.pending_size = self.max_bytes


@dataclass
class WithFlusher(ConnectOption):
    """Connect option to configure the flusher.

    Args:
        queue_size: The size of the flusher queue in number of messages.
        timeout: The flusher timeout in seconds.
    """

    queue_size: int = 1024
    timeout: float = 10

    def __call__(self, opts: ConnectOpts) -> None:
        opts.flusher_queue_size = self.queue_size
        opts.flush_timeout = self.timeout


@dataclass
class WithTLSCertificate(ConnectOption):
    """Connect option to configure client TLS certficiate.

    Args:
        cert_file: The path to the client certificate file.
        key_file: The path to the client key file.
        ca_file: The path to the CA certificate file.
        key_file_password: The password for the client key file.
        hostname: The hostname to use for TLS verification.
    """

    cert_file: str
    key_file: str
    ca_file: str | None = None
    key_file_password: str | None = None
    hostname: str | None = None

    def __call__(self, opts: ConnectOpts) -> None:
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
    """Connect option to configure user/password authentication.

    Args:
        user: The username.
        password: The password.
    """

    user: str
    password: str

    def __call__(self, opts: ConnectOpts) -> None:
        opts.user = self.user
        opts.password = self.password


@dataclass
class WithUsername(ConnectOption):
    """Connect option to configure username authentication.

    Args:
        user: The username.
    """

    user: str

    def __call__(self, opts: ConnectOpts) -> None:
        opts.user = self.user


@dataclass
class WithPassword(ConnectOption):
    """Connect option to configure password authentication.

    Args:
        password: The password.
    """

    password: str

    def __call__(self, opts: ConnectOpts) -> None:
        opts.password = self.password


@dataclass
class WithToken(ConnectOption):
    """Connect option to configure token authentication.

    Args:
        token: The token.
    """

    token: str

    def __call__(self, opts: ConnectOpts) -> None:
        opts.token = self.token


@dataclass
class WithCredentialsFile(ConnectOption):
    """Connect option to configure user credentials (concatenated user jwt + nkeys seed).

    Args:
        filepath: The path to the credentials file.
    """

    filepath: str

    def __call__(self, opts: ConnectOpts) -> None:
        path = Path(self.filepath).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Credentials file not found: {path}")
        opts.user_credentials = path.as_posix()


@dataclass
class WithNKeySeed(ConnectOption):
    """Connect option to configure nkeys authentication.

    Args:
        seed: The nkeys seed.
    """

    seed: str

    def __call__(self, opts: ConnectOpts) -> None:
        opts.nkeys_seed = self.seed


@dataclass
class WithNKeyFile(ConnectOption):
    """Connect option to configure nkeys authentication.

    Args:
        filepath: The path to the nkeys seed file.
    """

    filepath: str

    def __call__(self, opts: ConnectOpts) -> None:
        path = Path(self.filepath).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"NKey file not found: {path}")
        opts.nkeys_seed = path.read_text()


@dataclass
class WithSignatureCallback(ConnectOption):
    """Connect option to configure nkeys authentication.

    Args:
        callback: The callback function to sign the nonce.
    """

    callback: Callable[[str], bytes]

    def __call__(self, opts: ConnectOpts) -> None:
        opts.signature_cb = self.callback


@dataclass
class WithUserJwtCallback(ConnectOption):
    """Connect option to configure jwt authentication.

    Args:
        callback: The callback function to return the jwt.
    """

    callback: Callable[[], bytearray | bytes]

    def __call__(self, opts: ConnectOpts) -> None:
        opts.user_jwt_cb = self.callback


@dataclass
class WithNKeySeedAndJwt(ConnectOption):
    """Connect option to configure user credentials.

    Args:
        seed: The nkeys seed.
        jwt: The user jwt.
    """

    seed: str
    jwt: str

    def __call__(self, opts: ConnectOpts) -> None:
        if not __NKEYS_AVAILABLE__:
            raise ModuleNotFoundError("nkeys module not installed")
        nkey = nkeys.from_seed(self.seed.encode())  # type: ignore
        opts.signature_cb = lambda nonce: nkey.sign(nonce.encode())  # type: ignore
        opts.user_jwt_cb = lambda: self.jwt.encode()


@dataclass
class WithNkeyFileAndJwtFile(ConnectOption):
    """Connect option to configure user credentials.

    Args:
        nkey_file: The path to the nkeys seed file.
        jwt_file: The path to the user jwt file.
    """

    nkey_file: str
    jwt_file: str

    def __call__(self, opts: ConnectOpts) -> None:
        return WithNKeySeedAndJwt(
            Path(self.nkey_file).read_text(),
            Path(self.jwt_file).read_text(),
        ).__call__(opts)


@dataclass
class WithErrorCallback(ConnectOption):
    """Connect option to configure the error callback.

    Args:
        callback: The callback function to call each time an error occurs.
    """

    callback: Callable[[Exception], Awaitable[None]]

    def __call__(self, opts: ConnectOpts) -> None:
        opts.error_cb = self.callback


@dataclass
class WithDisconnectedCallback(ConnectOption):
    """Connect option to configure the disconnection callback.

    Args:
        callback: The callback function to call each time connection is lost.
    """

    callback: Callable[[], Awaitable[None]]

    def __call__(self, opts: ConnectOpts) -> None:
        opts.disconnected_cb = self.callback


@dataclass
class WithReconnectedCallback(ConnectOption):
    """Connect option to configure the reconnection callback.

    Args:
        callback: The callback function to call each time connection is reestablished.
    """

    callback: Callable[[], Awaitable[None]]

    def __call__(self, opts: ConnectOpts) -> None:
        opts.reconnected_cb = self.callback


@dataclass
class WithConnectionClosedCallback(ConnectOption):
    """Connect option to configure the connection closed callback.

    Args:
        callback: The callback function to call once connection is closed.
    """

    callback: Callable[[], Awaitable[None]]

    def __call__(self, opts: ConnectOpts) -> None:
        opts.closed_cb = self.callback


@dataclass
class WithServerDiscoveredCallback(ConnectOption):
    """Connect option to configure the server discovered callback.

    Args:
        callback: The callback function to call each time a new server is discovered.
    """

    callback: Callable[[], Awaitable[None]]

    def __call__(self, opts: ConnectOpts) -> None:
        opts.discovered_server_cb = self.callback


@dataclass
class WithCallbacks(ConnectOption):
    """Connect option to configure all connection state callbacks.

    Args:
        on_error: The callback function to call each time an error occurs.
        on_disconnection: The callback function to call each time connection is lost.
        on_connection_closed: The callback function to call once connection is closed.
        on_server_discovered: The callback function to call each time a new server is discovered.
        on_reconnection: The callback function to call each time connection is reestablished.
    """

    on_error: Callable[[Exception], Awaitable[None]] | None = None
    on_disconnection: Callable[[], Awaitable[None]] | None = None
    on_connection_closed: Callable[[], Awaitable[None]] | None = None
    on_server_discovered: Callable[[], Awaitable[None]] | None = None
    on_reconnection: Callable[[], Awaitable[None]] | None = None

    def __call__(self, opts: ConnectOpts) -> None:
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
