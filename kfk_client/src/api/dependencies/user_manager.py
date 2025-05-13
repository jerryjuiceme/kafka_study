from fastapi import Depends

from src.api.dependencies.users import get_users_db
from src.core.authentication.user_manager import UserManager


async def get_user_manager(user_db=Depends(get_users_db)):
    yield UserManager(user_db)
