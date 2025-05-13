from datetime import datetime
from typing import Annotated
from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, EmailStr, ConfigDict

from fastapi_users import schemas
from pydantic import BaseModel

from src.core.types.user_id import UserIdType


class UserRead(schemas.BaseUser[UserIdType]):
    username: str


class UserCreate(schemas.BaseUserCreate):
    username: Annotated[str, MinLen(3), MaxLen(20)]


class UserUpdate(schemas.BaseUserUpdate):
    username: str


class UserReadWithDate(UserRead):
    created_at: datetime | None
    updated_at: datetime | None
