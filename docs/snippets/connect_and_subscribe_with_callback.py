from easynats import connect, options
from easynats.core import Msg


async def handle_message(msg: Msg):
    """Handle a message."""
    print(msg)


async def main():
    """An example of subscribing to messages from a NATS server."""

    async with connect(
        options.WithServer("nats://localhost:4222"),
        options.WithConnectTimeout(5),
    ) as nc:
        # Create a subscription handler
        sub = nc.create_subscription_handler(
            subject="foo",
            callback=handle_message,
        )
        # Start the subscription handler
        await sub.start()
        # Do something
        # ...
        # Stop the subscription handler
        await sub.stop()
