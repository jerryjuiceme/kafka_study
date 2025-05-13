from abc import ABC, abstractmethod
import asyncio
from email.message import EmailMessage
import logging
from typing import AsyncGenerator, Final

from pydantic import BaseModel, ValidationError
from sqlalchemy.exc import DatabaseError

from src.core.repository.emails import EmailRepository
from src.core.schemas.emails import (
    CsvQueueReturn,
    EmailCreate,
    EmailQueueReturn,
    EmailUpdate,
)
from src.core.services.emails import EmailsService
from src.database import get_db_async

from .consumer_base import ConsumeBase

from src.config import settings

logger = logging.getLogger(__name__)


class ConsumeEmail(ConsumeBase):
    async def process_message(self, msg: str):

        try:
            db_session_gen = get_db_async()
            session = await anext(db_session_gen)
            service = EmailsService(EmailRepository(session))
            await asyncio.sleep(0)
            message: EmailQueueReturn = EmailQueueReturn.model_validate_json(msg)
            logger.info('Received message:  "%s"', message.status_message)
            email_to_update = EmailUpdate(**message.__dict__)
            await service.update(email_to_update)
            logger.info('Message processed:  "%s"', message.status_message)
        except DatabaseError as e:
            logger.error("Database error: %s", e)
        except Exception as e:
            logger.error("Unexpected error: %s", e)
        finally:
            await session.close()
            await asyncio.sleep(0)


class ConsumeCSV(ConsumeBase):
    async def process_message(self, msg: str):
        try:
            db_session_gen = get_db_async()

            session = await anext(db_session_gen)
            service = EmailsService(EmailRepository(session))
            message: CsvQueueReturn = CsvQueueReturn.model_validate_json(msg)
            logger.info('Received message:  "%s"', message.status_message)

            if message.status == "error" or message.subject == "no_subject":
                logger.error('Message has error: "%s"', message.status_message)
                return

            email_to_create = EmailCreate(**message.__dict__)
            await service.create(email_to_create)

        except DatabaseError as e:
            logger.error('Database error: "%s"', e)
        except Exception as e:
            logger.error('Unexpected error: "%s"', e)
        finally:
            await session.close()
            await asyncio.sleep(0)
