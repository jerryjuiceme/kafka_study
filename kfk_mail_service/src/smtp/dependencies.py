##########################
## MAILING DEPENDENCIES ##
##########################

# from fastapi import Depends
from src.config import settings
from src.smtp.service import (
    SMTPService,
    SMTPServiceMailDev,
    SMTPServiceSMTP,
)

# from faststream import Depends


def get_smtp_service() -> SMTPService:
    if settings.smtp.smtp_type == "maildev":
        return SMTPServiceMailDev(
            host=settings.smtp.maildev_host,
            port=settings.smtp.maildev_port,
        )

    if settings.smtp.smtp_type == "smtp":
        return SMTPServiceSMTP(
            username=settings.smtp.smtp_user,
            password=settings.smtp.smtp_pass,
            host=settings.smtp.smtp_host,
            port=settings.smtp.smtp_port,
            timeout=settings.smtp.smtp_timeout,
        )
    raise ValueError("Unknown smtp type")
