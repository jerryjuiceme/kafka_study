from typing import Annotated, Any
from fastapi import APIRouter, Depends, Form, HTTPException, Response
from src.api.api_v1.fastapi_users_main import fastapi_users, current_active_superuser
from src.api.dependencies.backend import authentication_backend
from src.core.schemas.users import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["Authorization"])

# /login  /logout
router.include_router(
    router=fastapi_users.get_auth_router(
        authentication_backend,
        # requires_verification=True, # Optional when verify is needed
    )
)


# /request-verify-token
# /verify
# router.include_router(router=fastapi_users.get_verify_router(UserRead))

# /reset-password-request
# /reset-password
# router.include_router(router=fastapi_users.get_reset_password_router())
