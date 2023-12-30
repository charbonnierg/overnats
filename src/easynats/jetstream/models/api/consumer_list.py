# @generated

from dataclasses import dataclass

from easynats.channel import Channel, Command


@dataclass
class JetStreamApiV1ConsumerListParams:
    stream_name: str
    """
    The name of the stream to list consumers from
    """


@dataclass
class JetstreamApiV1ConsumerListRequest:
    """
    A request to the JetStream $JS.API.CONSUMER.LIST API
    """

    offset: int


@dataclass
class ConsumerListResponse:
    """
    A response from the JetStream $JS.API.CONSUMER.LIST API
    """

    total: int
    offset: int
    limit: int
    type: str


JetstreamApiV1ConsumerListResponse = ConsumerListResponse


LIST_CONSUMERS = Command(
    channel=Channel(
        subject="CONSUMER.LIST.{stream_name}",
        parameters=JetStreamApiV1ConsumerListParams,
    ),
    message=JetstreamApiV1ConsumerListRequest,
    reply=JetstreamApiV1ConsumerListResponse,
    error=str,
)
