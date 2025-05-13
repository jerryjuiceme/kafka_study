import asyncio
from asyncio import AbstractEventLoop
import logging
from typing import Self

from aiokafka import AIOKafkaConsumer

from src.broker.consumers import ConsumeBase

logger = logging.getLogger(__name__)


class MessageConsumer:
    def __init__(
        self, topic: str, group_id: str, bootstrap_servers: str, loop: AbstractEventLoop
    ):
        self.consumer = AIOKafkaConsumer(
            topic,
            group_id=group_id,
            bootstrap_servers=bootstrap_servers,
            # loop=loop,
            max_poll_records=10,  # Ограничить количество сообщений за опрос
            max_poll_interval_ms=5000,  # Увеличить интервал опроса
        )
        self.topic: str = topic

    async def consume_message(
        self: Self,
        message_service: ConsumeBase,
    ):
        await self.consumer.start()
        logger.info("Consumer started, topic: %s", self.topic)
        try:
            async for message in self.consumer:
                if message.value is not None:
                    decoded_message = message.value.decode("utf-8")
                await message_service.process_message(decoded_message)
                await asyncio.sleep(0) #

        except KeyboardInterrupt:
            logger.warning("KeyboardInterrupt. Buy!")
            await self.consumer.stop()
        finally:
            await self.consumer.stop()
            logger.info("Consumer stopped, topic: %s", self.topic)

    #
    # async with self.consumer as consumer:
    #     logger.info("Consumer started")
    #     async for message in consumer:
    #         if message.value is not None:
    #             decoded_message = message.value.decode("utf-8")
    #             await message_service.process_message(decoded_message)
    #     logger.info("Consumer stopped")
