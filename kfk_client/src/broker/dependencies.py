from functools import lru_cache
from fastapi import Depends
from aiokafka import AIOKafkaProducer

from src.config import settings

from .broker import BrokerProducer


# @lru_cache
async def get_broker() -> AIOKafkaProducer:
    return AIOKafkaProducer(bootstrap_servers=settings.broker.kafka_bootstrap_servers)
    # return AIOKafkaProducer(bootstrap_servers="localhost:9092")


async def get_send_mail_producer(
    broker: AIOKafkaProducer = Depends(get_broker),
) -> BrokerProducer:
    return BrokerProducer(broker, settings.broker.send_topic)


async def get_send_csv_producer(
    broker: AIOKafkaProducer = Depends(get_broker),
) -> BrokerProducer:
    return BrokerProducer(broker, settings.broker.send_csv_topic)


SendEmailTopicDep = Depends(get_send_mail_producer)
SendCsvTopicDep = Depends(get_send_csv_producer)
