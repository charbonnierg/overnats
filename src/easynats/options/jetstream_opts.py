from __future__ import annotations

import abc
from dataclasses import dataclass


@dataclass
class JetStreamOpts:
    """JetStream options for NATS python client.

    Args:
        domain: The jetstream domain.
        api_prefix: The jetstream API prefix.
        kv_prefix: The jetstream KV prefix.
    """

    domain: str | None = None
    api_prefix: str = "$JS.API."
    kv_prefix: str = "$KV."

    def get_api_prefix(self) -> str:
        """Return the API prefix."""
        if self.domain:
            return f"$JS.{self.domain}.API."
        return self.api_prefix


class JetStreamOption(metaclass=abc.ABCMeta):
    """Base class for jetstream options.

    A JetStream option is a callable which can transform a
    [`JetStreamOpts`][easynats.options.jetstream_opts.JetStreamOpts] object.

    For example, the [`WithJetStreamDomain`][easynats.options.jetstream_opts.WithJetStreamDomain]
    jetstream option can be used to specify the jetstream domain:

    ```python
        async with easynats.connect():
            js = easynats.jetstream(WithJetStreamDomain("edge"))
    ```

    It's possible to use the [`configure()` method][easynats.connection.JetStreamConnection.configure] method on
    the [`JetStreamConnection` class][easynats.connection.JetStreamConnection] to add jetstream options:

    ```python
        js = easynats.Connection().jetstream()
        js.configure(
            WithJetStreamDomain("edge")
        )
    ```

    Custom jetstream options can be provided by creating a function
    which takes a [`JetStreamOpts`][easynats.options.jetstream_opts.JetStreamOpts] object as an argument and
    returns `None`:

    ```python
        def use_custom_options(opts: JetStreamOpts) -> None:
            # Do something with opts. For example set the api prefix:
            opts.api_prefix = "$JS.CUSTOM.API."

        js.configure(use_custom_options)
    ```

    See the [`easynats.options.jetstream_opts`][easynats.options.jetstream_opts] module for a list of available jetstream options.
    """

    @abc.abstractmethod
    def __call__(self, opts: JetStreamOpts) -> None:
        raise NotImplementedError


@dataclass
class WithJetStreamDomain(JetStreamOption):
    """Set the jetstream domain.

    Args:
        domain: The jetstream domain.
    """

    domain: str

    def __call__(self, opts: JetStreamOpts) -> None:
        opts.domain = self.domain


@dataclass
class WithJetStreamApiPrefix(JetStreamOption):
    """Set the jetstream API prefix.

    Args:
        api_prefix: The jetstream API prefix.
    """

    api_prefix: str

    def __call__(self, opts: JetStreamOpts) -> None:
        opts.api_prefix = self.api_prefix


@dataclass
class WithKeyValuePrefix(JetStreamOption):
    """Set the jetstream KV prefix.

    Args:
        prefix: The jetstream KV prefix.
    """

    prefix: str

    def __call__(self, opts: JetStreamOpts) -> None:
        opts.kv_prefix = self.prefix
