"""
Validation schemas module
"""

from typing import Annotated
from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, ConfigDict, EmailStr
from pydantic.alias_generators import to_camel


class EmailBaseModel(BaseModel):
    """
    Schema for creating models
    """

    subject: str
    from_email: Annotated[EmailStr, MinLen(5), MaxLen(100)]
    to_email: Annotated[EmailStr, MinLen(5), MaxLen(100)]
    message_body: str | None = None

    model_config = ConfigDict(from_attributes=True)


class EmailRecieve(EmailBaseModel):
    id: int | None
    status: str


class EmailSendBack(EmailRecieve):
    status_message: str | None = None


class UploadedFileRead(BaseModel):
    id: int
    file_name: str
    file_path: str
    user_id: int


class EmailReturnFromCsv(BaseModel):
    id: int | None = None
    subject: str | None = "No subject"
    from_email: EmailStr | None = None
    to_email: EmailStr | None = None
    message_body: str | None = None
    status: str = "error"
    status_message: str | None = None

    model_config = ConfigDict(from_attributes=True)
