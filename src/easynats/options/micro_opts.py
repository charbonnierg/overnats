from __future__ import annotations

import abc
from dataclasses import dataclass


@dataclass
class MicroOpts:
    """JetStream options for NATS python client.

    Args:
        api_prefix: The micro api prefix.
        default_queue: The micro default queue.
    """

    api_prefix: str = "$SRV"
    default_queue: str = "q"


class MicroOption(metaclass=abc.ABCMeta):
    """Base class for micro options.

    A Micro option is a callable which can transform a
    [`MicroOpts`][easynats.options.micro_opts.MicroOpts] object.

    For example, the [`WithServiceApiPrefix`][easynats.options.micro_opts.WithServiceApiPrefix]
    jetstream option can be used to specify the micro api service prefix:

    ```python
        async with easynats.connect():
            micro = easynats.micro(WithServiceApiPrefix("$SRV.CUSTOM"))
    ```

    It's possible to use the [`configure()` method][easynats.connection.MicroConnection.configure] method on
    the [`MicroConnection` class][easynats.connection.MicroConnection] to add micro options:

    ```python
        micro = easynats.Connection().micro()
        micro.configure(
            WithServiceApiPrefix("$SRV.CUSTOM")
        )
    ```

    Custom jetstream options can be provided by creating a function
    which takes a [`MicroOpts`][easynats.options.micro_opts.MicroOpts] object as an argument and
    returns `None`:

    ```python
        def use_custom_options(opts: MicroOpts) -> None:
            # Do something with opts. For example set the api prefix:
            opts.api_prefix = "$JS.CUSTOM.API."

        micro.configure(use_custom_options)
    ```

    See the [`easynats.options.micro_opts`][easynats.options.micro_opts] module for a list of available micro options.
    """

    @abc.abstractmethod
    def __call__(self, opts: MicroOpts) -> None:
        ...


@dataclass
class WithServiceApiPrefix(MicroOption):
    """Set the micro api service prefix.

    Args:
        prefix: The micro api service prefix.
    """

    prefix: str

    def __call__(self, opts: MicroOpts) -> None:
        opts.api_prefix = self.prefix


@dataclass
class WithDefaultServiceQueue(MicroOption):
    """Set the micro default queue.

    Args:
        queue: The micro default queue.
    """

    queue: str

    def __call__(self, opts: MicroOpts) -> None:
        opts.default_queue = self.queue
