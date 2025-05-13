from abc import ABC, abstractmethod
from asyncio import AbstractEventLoop
import asyncio
from typing import Self
import logging

logger = logging.getLogger(__name__)

from aiokafka import AIOKafkaConsumer

######################
### Consumer Base  ###
######################


class ConsumeBase(ABC):
    @abstractmethod
    async def process_message(self, msg: str):
        pass


class MessageConsumer:
    def __init__(
        self,
        topic: str,
        group_id: str,
        bootstrap_servers: str,
        loop: AbstractEventLoop,
    ):
        self.consumer = AIOKafkaConsumer(
            topic,
            group_id=group_id,
            bootstrap_servers=bootstrap_servers,
            loop=loop,
            # auto_offset_reset="latest",  # Начинать с последних сообщений
            # max_poll_records=10,  # Ограничить количество сообщений за опрос
            # max_poll_interval_ms=10000,  # Увеличить интервал опроса
            # session_timeout_ms=30000,  # Увеличить таймаут сессии
            # heartbeat_interval_ms=3000,  # Интервал heartbeat
        )

    async def consume_message(
        self: Self,
        message_service: ConsumeBase,
    ):
        await self.consumer.start()
        logger.info("Consumer started")
        try:
            async for message in self.consumer:
                try:
                    if message.value is not None:
                        decoded_message = message.value.decode("utf-8")
                        await message_service.process_message(decoded_message)
                except Exception as e:
                    logger.error(f"Error while processing message: {e}")
                continue

        except Exception as e:
            logger.error("Unexpected error: %s", e)
        except KeyboardInterrupt:
            logger.warning("KeyboardInterrupt. Buy!")
            await self.consumer.stop()
        finally:
            await self.consumer.stop()
            logger.info("Consumer stopped")
