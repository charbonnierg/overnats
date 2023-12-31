from __future__ import annotations

from pathlib import Path

import pytest

from easynats import options
from easynats.connection import Connection


class TestConnectOptions:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.connection = Connection()

    def test_server_option(self):
        conn = self.connection.with_options(options.Server("nats://localhost:4223"))
        assert conn.options == options.ConnectOpts(
            servers="nats://localhost:4223",
        )

    def test_servers_option(self):
        conn = self.connection.with_options(
            options.Servers(["nats://localhost:4222", "nats://localhost:4223"])
        )
        assert conn.options == options.ConnectOpts(
            servers=[
                "nats://localhost:4222",
                "nats://localhost:4223",
            ]
        )

    def test_name_option(self):
        conn = self.connection.with_options(options.ConnectionName("test-client"))
        assert conn.options == options.ConnectOpts(name="test-client")

    def test_dont_randomize_option(self):
        conn = self.connection.with_options(options.DontRandomize())
        assert conn.options == options.ConnectOpts(dont_randomize=True)

    def test_str_inbox_prefix_option(self):
        conn = self.connection.with_options(options.InboxPrefix("MYINBOX."))
        assert conn.options == options.ConnectOpts(inbox_prefix=b"MYINBOX.")

    def test_bytes_inbox_prefix_option(self):
        conn = self.connection.with_options(options.InboxPrefix(b"MYINBOX."))
        assert conn.options == options.ConnectOpts(inbox_prefix=b"MYINBOX.")

    def test_pedantic_option(self):
        conn = self.connection.with_options(options.Pedantic())
        assert conn.options == options.ConnectOpts(pedantic=True)

    def test_verbose_option(self):
        conn = self.connection.with_options(options.Verbose())
        assert conn.options == options.ConnectOpts(verbose=True)

    def test_no_echo_option(self):
        conn = self.connection.with_options(options.NoEcho())
        assert conn.options == options.ConnectOpts(no_echo=True)

    def test_connect_timeout(self):
        conn = self.connection.with_options(options.ConnectTimeout(10))
        assert conn.options == options.ConnectOpts(connect_timeout=10)

    def test_allow_reconnect_option_with_defaults(self):
        conn = self.connection.with_options(options.AllowReconnect())
        assert conn.options == options.ConnectOpts(
            allow_reconnect=True, max_reconnect_attempts=-1, reconnect_time_wait=2
        )

    def test_allow_reconnect_option_with_max_reconnect_attempts(self):
        conn = self.connection.with_options(options.AllowReconnect(max_attempts=10))
        assert conn.options == options.ConnectOpts(
            allow_reconnect=True, max_reconnect_attempts=10, reconnect_time_wait=2
        )

    def test_allow_reconnect_option_with_delay(self):
        conn = self.connection.with_options(options.AllowReconnect(delay_seconds=20))
        assert conn.options == options.ConnectOpts(
            allow_reconnect=True, max_reconnect_attempts=-1, reconnect_time_wait=20
        )

    def test_pending_queue_option_with_max_bytes(self):
        conn = self.connection.with_options(options.PendingQueue(max_bytes=20))
        assert conn.options == options.ConnectOpts(pending_size=20)

    def test_flusher_option_with_queue_size(self):
        conn = self.connection.with_options(options.Flusher(queue_size=30))
        assert conn.options == options.ConnectOpts(
            flusher_queue_size=30, flush_timeout=10
        )

    def test_flusher_option_with_timeout(self):
        conn = self.connection.with_options(options.Flusher(timeout=60))
        assert conn.options == options.ConnectOpts(
            flusher_queue_size=1024, flush_timeout=60
        )

    def test_tls_certificate_option_with_client_crt_and_client_key(
        self,
        client_crt: str,
        client_key: str,
    ):
        conn = self.connection.with_options(
            options.TLSCertificate(cert_file=client_crt, key_file=client_key)
        )
        assert conn.options.tls is not None

    def test_tls_certificate_option_with_client_crt_and_client_key_and_ca_crt(
        self,
        client_crt: str,
        client_key: str,
        ca_crt: str,
    ):
        conn = self.connection.with_options(
            options.TLSCertificate(
                cert_file=client_crt, key_file=client_key, ca_file=ca_crt
            )
        )
        assert conn.options.tls is not None
        assert len(conn.options.tls.get_ca_certs()) == 1

    def test_tls_certificate_option_with_client_crt_and_client_key__and_ca_crt_and_hostname(
        self,
        client_crt: str,
        client_key: str,
        ca_crt: str,
    ):
        conn = self.connection.with_options(
            options.TLSCertificate(
                cert_file=client_crt,
                key_file=client_key,
                ca_file=ca_crt,
                hostname="test-server.example.org",
            )
        )
        assert conn.options.tls is not None
        assert conn.options.tls_hostname == "test-server.example.org"

    def test_user_password_option(self):
        conn = self.connection.with_options(
            options.UserPassword(user="test-user", password="test-password")
        )
        assert conn.options.user == "test-user"
        assert conn.options.password == "test-password"

    def test_username_option(self):
        conn = self.connection.with_options(options.Username("test-user"))
        assert conn.options.user == "test-user"

    def test_password_option(self):
        conn = self.connection.with_options(options.Password("test-password"))
        assert conn.options.password == "test-password"

    def test_token_option(self):
        conn = self.connection.with_options(options.Token("test-token"))
        assert conn.options.token == "test-token"

    def test_credentials_file_option(self, temporary_file: str):
        conn = self.connection.with_options(options.CredentialsFile(temporary_file))
        assert conn.options.user_credentials == temporary_file

    def test_nkey_seed_option(self):
        conn = self.connection.with_options(options.NKeySeed("test-nkey"))
        assert conn.options.nkeys_seed == "test-nkey"

    def test_nkey_file_option(self, temporary_file: str):
        Path(temporary_file).write_text("test-nkey")
        conn = self.connection.with_options(options.NKeyFile(temporary_file))
        assert conn.options.nkeys_seed == "test-nkey"

    def test_signature_callback_option(self):
        def callback(value: str) -> bytes:
            return value.upper().encode()

        conn = self.connection.with_options(options.SignatureCallback(callback))
        assert conn.options.signature_cb
        assert conn.options.signature_cb("test") == b"TEST"

    def test_user_jwt_callback_option(self):
        def callback() -> bytes:
            return b"test-jwt"

        conn = self.connection.with_options(options.UserJwtCallback(callback))
        assert conn.options.user_jwt_cb
        assert conn.options.user_jwt_cb() == b"test-jwt"

    def test_nkey_seed_and_jwt_option(self):
        conn = self.connection.with_options(
            options.NKeySeedAndJwt(
                seed="SUACSSL3UAHUDXKFSNVUZRF5UHPMWZ6BFDTJ7M6USDXIEDNPPQYYYCU3VY",
                jwt="test-jwt",
            )
        )
        assert conn.options.user_jwt_cb
        assert conn.options.user_jwt_cb() == b"test-jwt"
        assert conn.options.signature_cb
        signed = conn.options.signature_cb("test")
        assert isinstance(signed, bytes)
        assert len(signed) > 0

    def test_nkey_file_and_jwt_file_option(self, temporary_file: str, nkey_file: str):
        Path(temporary_file).write_text("test-jwt")
        conn = self.connection.with_options(
            options.NkeyFileAndJwtFile(nkey_file=nkey_file, jwt_file=temporary_file)
        )
        assert conn.options.user_jwt_cb
        assert conn.options.user_jwt_cb() == b"test-jwt"
        assert conn.options.signature_cb
        signed = conn.options.signature_cb("test")
        assert isinstance(signed, bytes)
        assert len(signed) > 0

    @pytest.mark.asyncio
    async def test_on_error_option(self):
        class Spy:
            received: Exception | None = None

            async def __call__(self, exc: Exception) -> None:
                self.received = exc

        spy = Spy()
        conn = self.connection.with_options(options.OnError(spy))
        assert conn.options.error_cb
        exc = Exception("test")
        await conn.options.error_cb(exc)
        assert spy.received is exc

    @pytest.mark.asyncio
    async def test_on_disconnection_option(self):
        class Spy:
            called = False

            async def __call__(self) -> None:
                self.called = True

        spy = Spy()
        conn = self.connection.with_options(options.OnDisconnection(spy))
        assert conn.options.disconnected_cb
        await conn.options.disconnected_cb()
        assert spy.called is True

    @pytest.mark.asyncio
    async def test_on_connection_closed_option(self):
        class Spy:
            called = False

            async def __call__(self) -> None:
                self.called = True

        spy = Spy()
        conn = self.connection.with_options(options.OnConnectionClosed(spy))
        assert conn.options.closed_cb
        await conn.options.closed_cb()
        assert spy.called is True

    @pytest.mark.asyncio
    async def test_on_discovered_server_option(self):
        class Spy:
            called = False

            async def __call__(self) -> None:
                self.called = True

        spy = Spy()
        conn = self.connection.with_options(options.OnDiscoveredServer(spy))
        assert conn.options.discovered_server_cb
        await conn.options.discovered_server_cb()
        assert spy.called is True

    @pytest.mark.asyncio
    async def test_on_reconnection_option(self):
        class Spy:
            called = False

            async def __call__(self) -> None:
                self.called = True

        spy = Spy()
        conn = self.connection.with_options(options.OnReconnection(spy))
        assert conn.options.reconnected_cb
        await conn.options.reconnected_cb()
        assert spy.called is True

    @pytest.mark.asyncio
    async def test_callbacks_option(self):
        class Spy:
            error_called = False
            disconnected_called = False
            closed_called = False
            discovered_server_called = False
            reconnected_called = False

            async def error(self, exc: Exception) -> None:
                self.error_called = True

            async def disconnected(self) -> None:
                self.disconnected_called = True

            async def closed(self) -> None:
                self.closed_called = True

            async def discovered_server(self) -> None:
                self.discovered_server_called = True

            async def reconnected(self) -> None:
                self.reconnected_called = True

        spy = Spy()
        conn = self.connection.with_options(
            options.Callbacks(
                on_error=spy.error,
                on_disconnection=spy.disconnected,
                on_connection_closed=spy.closed,
                on_server_discovered=spy.discovered_server,
                on_reconnection=spy.reconnected,
            )
        )
        assert conn.options.error_cb
        assert conn.options.disconnected_cb
        assert conn.options.closed_cb
        assert conn.options.discovered_server_cb
        assert conn.options.reconnected_cb
        await conn.options.error_cb(Exception("test"))
        await conn.options.disconnected_cb()
        await conn.options.closed_cb()
        await conn.options.discovered_server_cb()
        await conn.options.reconnected_cb()
        assert spy.error_called is True
        assert spy.disconnected_called is True
        assert spy.closed_called is True
        assert spy.discovered_server_called is True
        assert spy.reconnected_called is True
