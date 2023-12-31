from dataclasses import dataclass
from typing import Optional

from .consumer_configuration import ConsumerConfig
from .consumer_state import AckFloor, Cluster, Delivered


@dataclass
class ConsumerInfoRequired:
    """
    Information about a JetStream Consumer.
    """

    stream_name: str
    """
    The Stream the consumer belongs to
    """
    name: str
    """
    A unique name for the consumer, either machine generated or the durable name
    """
    config: ConsumerConfig
    """
    The consumer configuration
    """
    created: str
    """
    The time the Consumer was created
    """
    delivered: Delivered
    """
    The last message delivered from this Consumer
    """
    ack_floor: AckFloor
    """
    The highest contiguous acknowledged message
    """
    num_ack_pending: int
    """
    The number of messages pending acknowledgement
    """
    num_redelivered: int
    """
    The number of redeliveries that have been performed
    """
    num_waiting: int
    """
    The number of pull consumers waiting for messages
    """
    num_pending: int
    """
    The number of messages left unconsumed in this Consumer
    """


@dataclass
class ConsumerInfoExtras:
    ts: Optional[str] = None
    """
    The server time the consumer info was created
    """
    cluster: Optional[Cluster] = None
    """
    Informaton about the cluster the consumer is in
    """
    push_bound: Optional[bool] = None
    """
    Indicates if any client is connected and receiving messages from a push consumer
    """


@dataclass
class ConsumerInfo(ConsumerInfoExtras, ConsumerInfoRequired):
    """
    Information about a JetStream Consumer.
    """

    pass
