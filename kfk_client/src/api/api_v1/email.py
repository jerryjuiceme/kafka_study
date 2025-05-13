import json
from logging import getLogger
from typing import Annotated, Any

from fastapi import APIRouter, Form, HTTPException, status

from src.api.dependencies.pagination import PaginationDep
from src.broker.broker import BrokerProducer
from src.broker.dependencies import SendEmailTopicDep
from src.core.schemas.api_message import BaseOutputMessage
from src.core.schemas.emails import EmailCreate, EmailRead, EmailRequest
from src.core.services.emails import EmailsService, EmailsServiceDep
from src.utils.string import NOT_IMPLEMENTED
from src.config import settings

# from src.broker.broker import broker, queue_send, exch

router = APIRouter(prefix="/emails", tags=["Emails"])
logger = getLogger(__name__)


@router.post(
    "/send_mail",
    # dependencies=[Depends(current_active_user)],
    status_code=status.HTTP_201_CREATED,
    response_model=BaseOutputMessage[EmailRead],
)
async def send_test_email(
    email_data: Annotated[EmailRequest, Form()],
    service: Annotated[EmailsService, EmailsServiceDep],
    broker: Annotated[BrokerProducer, SendEmailTopicDep],
) -> Any:
    logger.info("Email data registered %s", email_data)
    from_email = settings.email.from_user
    if not from_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=NOT_IMPLEMENTED
        )

    mail_data: EmailCreate = EmailCreate(from_email=from_email, **email_data.__dict__)
    new_email_record = await service.create(mail_data)
    if not new_email_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=NOT_IMPLEMENTED
        )
    await broker.send_message(value=new_email_record)

    return BaseOutputMessage(data=new_email_record, message="Email Sent")


@router.get(
    "/",
    response_model=BaseOutputMessage[list[EmailRead]],
)
async def get_emails(
    service: Annotated[EmailsService, EmailsServiceDep],
):
    emails = await service.get_all()
    return BaseOutputMessage(data=emails, message="all_emails")
