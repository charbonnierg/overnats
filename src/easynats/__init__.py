from . import options
from .connection import Connection
from .options import ConnectOption, ConnectOpts


def connect(*options: ConnectOption) -> Connection:
    """Create a new connection.

    This function does NOT open the connection. Instead, use
    the returned connection object as an asynchronous context
    manager to open the connection:

    ```python
        async with easynats.connect() as nc:
            pass
    ```

    Or, use the `open()` method:

    ```python
        nc = easynats.connect()
        await nc.open()
    ```

    See [`Connection.open()`][easynats.Connection.open] for more details.

    Args:
        options: Connection options.

    Returns:
        A new connection object.
    """
    return Connection().configure(*options)


__all__ = ["Connection", "ConnectOpts", "ConnectOption", "options", "connect"]
