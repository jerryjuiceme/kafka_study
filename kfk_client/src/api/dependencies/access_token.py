from typing import (
    TYPE_CHECKING,
    Annotated,
)

from fastapi import Depends

from src.core.models.access_token import AccessToken
from src.database import get_db_async

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_access_tokens_db(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_async),
    ],
):
    yield AccessToken.get_db(session=session)
