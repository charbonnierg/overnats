from easynats import connect, options


async def main():
    """An example of subscribing to messages from a NATS server."""

    async with connect(
        options.WithServer("nats://localhost:4222"),
        options.WithConnectTimeout(5),
    ) as nc:
        # Subscribe to messages usng an iterator
        async with nc.core.subscribe(subject="foo") as sub:
            # Iterate over messages
            async for msg in sub.messages():
                # Process message
                print(msg)
                # Stop iterating, subscription will be closed
                # on context manager exit
                break
