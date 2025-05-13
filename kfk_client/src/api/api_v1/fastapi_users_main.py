from fastapi import Depends
from fastapi_users import FastAPIUsers
from typing import TYPE_CHECKING, Annotated

from src.core.models.users import User

# if TYPE_CHECKING:
from src.core.types.user_id import UserIdType

from src.api.dependencies.user_manager import get_user_manager
from src.api.dependencies.backend import authentication_backend

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [authentication_backend],
)

current_active_user = fastapi_users.current_user(active=True)
current_active_superuser = fastapi_users.current_user(active=True, superuser=True)

CurrentUserDep = Annotated[User, Depends(current_active_user)]
CurrentSupUserDep = Annotated[User, Depends(current_active_superuser)]
