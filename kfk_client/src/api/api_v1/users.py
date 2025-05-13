from typing import Annotated, Any
from fastapi import APIRouter, Depends, Form, HTTPException, Response
from src.api.api_v1.fastapi_users_main import fastapi_users, current_active_superuser
from src.api.dependencies.backend import authentication_backend
from src.core.schemas.users import UserCreate, UserRead, UserUpdate

router = APIRouter(
    prefix="/users", tags=["Users"], dependencies=[Depends(current_active_superuser)]
)


# /me
router.include_router(router=fastapi_users.get_users_router(UserRead, UserUpdate))

# /register
router.include_router(
    router=fastapi_users.get_register_router(UserRead, UserCreate),
)
