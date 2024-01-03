from easynats import connect, options


async def main():
    """An example of connecting and publishing a request to a NATS server."""

    async with connect(
        options.WithServer("nats://localhost:4222"),
        options.WithConnectTimeout(5),
    ) as nc:
        # Publish a message without payload
        await nc.publish_request(subject="foo", reply_subject="bar")
        # Send a request with payload
        await nc.publish_request(
            subject="foo",
            reply_subject="bar",
            payload=b"Hello World!",
        )
        # Publish a request with headers
        await nc.publish_request(
            subject="foo",
            reply_subject="bar",
            payload=b"Hello World!",
            headers={
                "Content-Type": "plain/text",
                "Content-Length": "12",
            },
        )
