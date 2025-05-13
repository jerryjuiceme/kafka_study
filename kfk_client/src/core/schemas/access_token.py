from datetime import datetime

from pydantic import BaseModel

from src.core.schemas.base import CreateBaseModel, UpdateBaseModel


class AccessTokenCreate(CreateBaseModel):
    user_id: int
    token: str
    expires_at: datetime


class AccessTokenRead(BaseModel):
    id: int
    user_id: int
    token: str
    expires_at: datetime
    created_at: datetime


class AccessTokenUpdate(UpdateBaseModel):
    token: str | None = None
    expires_at: datetime | None = None
