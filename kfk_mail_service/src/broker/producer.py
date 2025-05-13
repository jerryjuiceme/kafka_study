import logging
import asyncio

from aiokafka import AIOKafkaProducer
from pydantic import BaseModel

from src.config import settings


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
    async def send_message(self, value: BaseModel) -> None:
        logger.info("Starting producer")
        if not self.producer._closed:
            await self.close_connection()
        await self.open_connection()
        encoded_value = value.model_dump_json().encode()
        try:
            await self.producer.send_and_wait(topic=self.topic, value=encoded_value)
        except Exception as e:
            logger.error("Failed, error: %s", (str(e)))
            raise Exception(f"Failed to send message: {str(e)}")
        finally:
            await self.close_connection()
            logger.info("Stopping producer")
            await asyncio.sleep(0)

    def __del__(self):
        asyncio.run(self.close_connection())
        logger.info("Producer deleted")


######################
### Get Producers  ###
######################


async def get_broker() -> AIOKafkaProducer:
    return AIOKafkaProducer(bootstrap_servers=settings.broker.kafka_bootstrap_servers)
    # return AIOKafkaProducer(bootstrap_servers="localhost:9092")


async def get_send_mail_producer() -> BrokerProducer:
    broker = await get_broker()
    return BrokerProducer(broker, settings.broker.receive_topic)


async def get_send_csv_producer() -> BrokerProducer:
    broker = await get_broker()
    return BrokerProducer(broker, settings.broker.receive_csv_topic)
