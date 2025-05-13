import asyncio
from typing import List
import logging

from src.broker import MessageConsumer
from src.config import settings
from src.broker.consumers import ConsumeEmail, ConsumeCSV

event_loop = asyncio.get_event_loop()

logger = logging.getLogger(__name__)


async def start_email_consuming(group_id: str = "EmailGroupRecieveID") -> None:
    consumer = MessageConsumer(
        topic=settings.broker.receive_topic,
        group_id=group_id,
        bootstrap_servers=settings.broker.kafka_bootstrap_servers,
        loop=event_loop,
    )
    await consumer.consume_message(
        message_service=ConsumeEmail(),
    )

    logger.info("Email consumer started")


async def start_csv_consuming() -> None:
    consumer = MessageConsumer(
        topic=settings.broker.receive_csv_topic,
        group_id="CSVGroupReceiveID",
        bootstrap_servers=settings.broker.kafka_bootstrap_servers,
        loop=event_loop,
    )
    await consumer.consume_message(
        message_service=ConsumeCSV(),
    )
    logger.info("Csv consumer started")


background_tasks: List[asyncio.Task] = []


async def start_consumers() -> None:
    background_tasks.append(
        asyncio.create_task(start_email_consuming("EmailGroupRecieveID"))
    )
    background_tasks.append(asyncio.create_task(start_csv_consuming()))
    logger.info("Consumers started")


async def stop_consumers() -> None:
    for task in background_tasks:
        task.cancel()
    await asyncio.gather(*background_tasks, return_exceptions=True)
    logger.info("Consumers stopped")
