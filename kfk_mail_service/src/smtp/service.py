from abc import ABC, abstractmethod
from contextlib import asynccontextmanager, contextmanager
from email.message import EmailMessage
from functools import lru_cache
from typing import AsyncGenerator
import aiosmtplib
import smtplib
import ssl

from logging import getLogger

logger = getLogger(__name__)


###################
## EMAIL SERVICE ##
###################


class SMTPService(ABC):
    @abstractmethod
    async def send_email(self, msg: EmailMessage):
        pass


###################
# MailDevService #
###################


class SMTPServiceMailDev(SMTPService):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def send_email(self, msg: EmailMessage):
        try:
            async with aiosmtplib.SMTP(
                hostname=self.host,
                port=self.port,
            ) as server:
                await server.send_message(msg)
            logger.info("Email successfully sent to %s", msg["TO"])
        except Exception as e:
            raise ValueError(f"Failed to load file: {str(e)}")
            logger.error("Failed to send email to %s, error: %s", (msg["TO"], str(e)))


class SMTPServiceSMTP(SMTPService):

    def __init__(self, username, password, host, port, timeout):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.timeout = timeout

    @asynccontextmanager
    @lru_cache
    async def connection(self) -> AsyncGenerator[aiosmtplib.SMTP, None]:
        client = None
        try:

            client = aiosmtplib.SMTP(
                hostname=self.host, port=self.port, timeout=self.timeout
            )

            await client.ehlo()
            await client.starttls(tls_context=ssl.create_default_context())
            await client.login(self.username, self.password)
            logger.info("Connected to %s", self.host)
            yield client
        except Exception as e:
            logger.error("Failed to connect to %s, error: %s", (self.host, str(e)))
        finally:
            if client:
                try:
                    await client.quit()
                except Exception as e:
                    logger.warning(
                        "Failed closing SMTP connection to %s, error: %s",
                        (self.host, str(e)),
                    )

    async def send_email(self, msg: EmailMessage):
        try:
            async with self.connection() as client:
                await client.send_message(msg)
            logger.info("Email successfully sent to %s", msg["TO"])
        except Exception as e:
            raise Exception
            logger.error("Failed to send email to %s, error: %s", (msg["TO"], str(e)))
