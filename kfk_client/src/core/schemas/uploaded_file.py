from datetime import datetime
from typing import Annotated, Literal

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, ConfigDict, EmailStr

from src.core.schemas.base import CreateBaseModel, UpdateBaseModel


class UploadedFileCreate(CreateBaseModel):
    file_name: str
    file_path: str
    user_id: int


class UploadedFileRead(BaseModel):
    id: int
    file_name: str
    file_path: str
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UploadedFileUpdate(UpdateBaseModel):
    file_name: str
    file_path: str
