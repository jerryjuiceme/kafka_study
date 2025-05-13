from abc import ABC, abstractmethod
import asyncio
from email.message import EmailMessage
import logging
from typing import AsyncGenerator
import typing

from pydantic import ValidationError

from src.broker.producer import get_send_csv_producer, get_send_mail_producer
from src.schemas import (
    EmailBaseModel,
    EmailRecieve,
    EmailReturnFromCsv,
    EmailSendBack,
    UploadedFileRead,
)
from src.smtp.dependencies import get_smtp_service
from src.smtp.message import get_prepared_email_template
from src.smtp.service import SMTPService
from src.config import settings
from src.storage.storage import read_csv_file

if typing.TYPE_CHECKING:
    from src.broker.producer import BrokerProducer

logger = logging.getLogger(__name__)


class ConsumeBase(ABC):
    @abstractmethod
    async def process_message(self, msg: str):
        pass


class ConsumeEmail(ConsumeBase):
    def __init__(self):
        self.mail_service: SMTPService = get_smtp_service()

    async def process_message(self, msg: str):
        producer: BrokerProducer = await get_send_mail_producer()

        try:
            message: EmailRecieve = EmailRecieve.model_validate_json(msg)
            prepared_email: EmailMessage = await get_prepared_email_template(message)
            await self.mail_service.send_email(prepared_email)

        except ValueError as e:
            logger.error(e)
            message.status = "error"
            back_message = EmailSendBack(status_message=str(e), **message.__dict__)
            await producer.send_message(value=back_message)
        except Exception as e:
            logger.error(e)
            message.status = "error"
            back_message = EmailSendBack(status_message=str(e), **message.__dict__)
            await producer.send_message(value=back_message)
        else:
            message.status = "success"
            email_processed = EmailSendBack(
                status_message="success", **message.__dict__
            )
            email_processed.status = "success"
            await producer.send_message(value=email_processed)
            logger.warning("Message processed: %s", message)
        finally:
            del producer
        await asyncio.sleep(0)


class ConsumeCSV(ConsumeBase):
    def __init__(self):
        self.mail_service: SMTPService = get_smtp_service()

    async def process_message(self, msg: str):
        producer: BrokerProducer = await get_send_csv_producer()
        try:
            message: UploadedFileRead = UploadedFileRead.model_validate_json(msg)
            csv_path: str = f"{settings.storage.global_path}/{message.file_path}"
            csv_generator = read_csv_file(csv_path)
            await self._iterate_csv(csv_generator, self.mail_service, producer)

        except FileNotFoundError as e:
            logger.warning("CSV file not found: %s", message.file_path)
            await _csv_broken_msg_processor(e, producer)

        except Exception as e:
            logger.error("Error reading CSV: %s", e)
            await _csv_broken_msg_processor(e, producer)

        finally:
            del producer

    async def _iterate_csv(
        self,
        csv_generator: AsyncGenerator[dict, None],
        mail_service: SMTPService,
        producer: "BrokerProducer",
    ):
        async for row in csv_generator:
            try:
                mail_message = EmailBaseModel(**row)
                prepared_email = await get_prepared_email_template(mail_message)
                await mail_service.send_email(prepared_email)
            except ValidationError as e:
                logger.error('ValidationError: "%s"', e)
                await _csv_broken_msg_processor(e, producer)
            except Exception as e:
                logger.error('Exception: "%s"', e)
                await _csv_broken_msg_processor(e, producer)
            else:
                email_processed = EmailReturnFromCsv(**row)
                email_processed.status = "success"
                await producer.send_message(value=email_processed)
                logger.warning("Message processed: %s", email_processed)


async def _csv_broken_msg_processor(
    exception: Exception, producer: "BrokerProducer"
) -> None:
    broken_message = EmailReturnFromCsv(
        status_message=str(exception),
    )
    await producer.send_message(value=broken_message)
