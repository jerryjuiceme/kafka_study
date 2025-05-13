from typing import (
    TYPE_CHECKING,
    Annotated,
)

from fastapi import Depends

from src.core.models.users import User
from src.database import get_db_async


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_users_db(
    session: Annotated[
        "AsyncSession",
        Depends(get_db_async),
    ],
):
    yield User.get_db(session=session)
