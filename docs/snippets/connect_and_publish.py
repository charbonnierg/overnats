from easynats import connect, options


async def main():
    """An example of connecting and publishing to a NATS server."""

    async with connect(
        options.WithServer("nats://localhost:4222"),
        options.WithConnectTimeout(5),
    ) as nc:
        # Publish a message without payload
        await nc.publish(subject="foo")
        # Publish a message with payload
        await nc.publish(
            subject="foo",
            payload=b"Hello World!",
        )
        # Publish a message with headers
        await nc.publish(
            subject="foo",
            payload=b"Hello World!",
            headers={
                "Content-Type": "plain/text",
                "Content-Length": "12",
            },
        )
