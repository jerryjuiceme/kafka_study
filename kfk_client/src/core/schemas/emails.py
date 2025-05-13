from datetime import datetime
from typing import Annotated, Literal

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, ConfigDict, EmailStr

from src.core.schemas.base import CreateBaseModel, UpdateBaseModel


class EmailCreate(CreateBaseModel):
    subject: str
    from_email: Annotated[EmailStr, MinLen(5), MaxLen(100)]
    to_email: Annotated[EmailStr, MinLen(5), MaxLen(100)]
    message_body: str | None = None
    status: str | None = "pending"


class EmailRead(BaseModel):
    id: int
    subject: str
    from_email: EmailStr
    to_email: EmailStr
    message_body: str | None = None
    status: str | None
    created_at: datetime
    updated_at: datetime


class EmailUpdate(UpdateBaseModel):
    subject: str
    from_email: EmailStr
    to_email: EmailStr
    message_body: str | None = None
    status: str | None


class EmailRequest(BaseModel):
    subject: str
    to_email: Annotated[EmailStr, MinLen(5), MaxLen(100)]
    message_body: str | None = None


class EmailQueueReturn(BaseModel):
    id: int | None
    subject: str
    from_email: EmailStr
    to_email: EmailStr
    message_body: str | None
    status: str
    status_message: str | None

    # model_config = ConfigDict(from_attributes=True)


class CsvQueueReturn(EmailQueueReturn):
    from_email: EmailStr | None
    to_email: EmailStr | None
    model_config = ConfigDict(from_attributes=True)
