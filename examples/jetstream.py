from easynats import Connection, options


async def main() -> None:
    """Run the example."""
    nc = Connection().with_options(
        options.DrainTimeout(10), options.AllowReconnect(max_attempts=-1)
    )
    # Connect to NATS
    async with nc:
        # Get a JetStream connection over the NATS connection
        js = nc.jetstream()
        # Create a stream
        await js.streams.create(name="ORDERS", subjects=["ORDERS.>"])
        # Delete a stream
        await js.streams.delete("ORDERS")
        # Create another stream
        await js.streams.create(name="ORDERS", subjects=["ORDERS.>"])
        # Get all stream names
        all_stream_names = await js.streams.list_names()
        print(all_stream_names)
        # Get all streams
        all_streams = await js.streams.list()
        print(all_streams)
        # Get one stream
        stream = await js.streams.get("ORDERS")
        print(stream)
        # Publish a message to the stream
        await stream.publish("ORDERS.1", b"Hello World!")
        # Create a consumer
        consumer = await stream.create_ephemeral_push_consumer("some_deliver_subject")
        # Open consumer message queue
        async with consumer.messages() as queue:
            # Get a pending message
            pending = await queue.next()
            # Acknowledge the message
            await pending.ack()
