import contextlib
import asyncio
from src.config import settings
from src.database import async_session_factory
from src.core.models.users import User
from fastapi_users.exceptions import UserAlreadyExists

from src.api.dependencies.users import get_users_db
from src.api.dependencies.user_manager import get_user_manager
from src.core.authentication.user_manager import UserManager
from src.core.schemas.users import UserCreate

get_users_db_context = contextlib.asynccontextmanager(get_users_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)

default_email = settings.first_superuser_email
default_password = settings.first_superuser_password
default_username = settings.first_superuser_name
default_is_active = True
default_is_superuser = True
default_is_verified = True


async def create_user(
    user_manager: UserManager,
    user_create: UserCreate,
) -> User:
    user = await user_manager.create(
        user_create=user_create,
        safe=False,
    )
    return user


async def create_superuser(
    email: str = default_email,
    username: str = default_username,
    password: str = default_password,
    is_active: bool = default_is_active,
    is_superuser: bool = default_is_superuser,
    is_verified: bool = default_is_verified,
):
    user_create = UserCreate(
        email=email,
        username=username,
        password=password,
        is_active=is_active,
        is_superuser=is_superuser,
        is_verified=is_verified,
    )
    try:
        async with async_session_factory() as session:
            async with get_users_db_context(session) as users_db:
                async with get_user_manager_context(users_db) as user_manager:
                    return await create_user(
                        user_manager=user_manager,
                        user_create=user_create,
                    )

    except UserAlreadyExists as e:
        print("User already exists. Can't create superuser")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    asyncio.run(create_superuser())
