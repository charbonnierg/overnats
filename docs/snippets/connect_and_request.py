from easynats import connect, options


async def main():
    """An example of connecting and sending a request to a NATS server."""

    async with connect(
        options.WithServer("nats://localhost:4222"),
        options.WithConnectTimeout(5),
    ) as nc:
        # Publish a message without payload
        reply = await nc.request(subject="foo", timeout=1)
        # Send a request with payload
        reply = await nc.request(
            subject="foo",
            payload=b"Hello World!",
            timeout=1,
        )
        # Send a request with headers
        reply = await nc.request(
            subject="foo",
            payload=b"Hello World!",
            headers={
                "Content-Type": "plain/text",
                "Content-Length": "12",
            },
            timeout=1,
        )
        # The headers of the reply
        print(reply.headers)
        # The payload of the reply
        print(reply.payload)
        # The subject on which reply was sent
        print(reply.subject)
        # The subject on which request was sent
        print(reply.origin)
