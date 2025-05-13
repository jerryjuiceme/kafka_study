import asyncio
from typing import List
import logging


from .base_consumer import MessageConsumer
from src.broker.consumers import ConsumeCSV, ConsumeEmail
from src.config import settings

event_loop = asyncio.get_event_loop()

logger = logging.getLogger(__name__)


async def start_email_consuming() -> None:
    consumer1 = MessageConsumer(
        topic=settings.broker.send_topic,
        group_id="EmailGroupID",
        bootstrap_servers=settings.broker.kafka_bootstrap_servers,
        loop=event_loop,
    )

    await consumer1.consume_message(
        message_service=ConsumeEmail(),
    )


async def start_csv_consuming() -> None:
    consumer = MessageConsumer(
        topic=settings.broker.send_csv_topic,
        group_id="CSVGroupID",
        bootstrap_servers=settings.broker.kafka_bootstrap_servers,
        loop=event_loop,
    )
    await consumer.consume_message(
        message_service=ConsumeCSV(),
    )


background_tasks: List[asyncio.Task] = []


async def start_consumers() -> None:
    background_tasks.append(asyncio.create_task(start_email_consuming()))
    background_tasks.append(asyncio.create_task(start_csv_consuming()))


async def stop_consumers() -> None:
    for task in background_tasks:
        task.cancel()
    await asyncio.gather(*background_tasks, return_exceptions=True)
