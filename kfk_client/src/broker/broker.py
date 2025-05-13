import logging

from aiokafka import AIOKafkaProducer

from src.core.schemas.base import CreateBaseModel

logger = logging.getLogger(__name__)

#################
### Producer  ###
#################


class BrokerProducer:
    def __init__(self, producer: AIOKafkaProducer, topic: str) -> None:
        self.producer = producer
        self.topic = topic

    async def open_connection(self) -> None:
        await self.producer.start()

    async def close_connection(self) -> None:
        if self.producer is not None:
            await self.producer.stop()

    # Send message and confirm
    async def send_message(self, value: CreateBaseModel) -> None:
        await self.open_connection()
        encoded_value = value.model_dump_json().encode()
        try:
            await self.producer.send(topic=self.topic, value=encoded_value)
        except Exception as e:
            logger.error("Failed, error: %s", (str(e)))
            raise Exception(f"Failed to send message: {str(e)}")
        finally:
            await self.close_connection()
            logger.debug("Stopping producer")
