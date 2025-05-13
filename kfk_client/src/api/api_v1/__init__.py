from fastapi import APIRouter, Depends
from src.config import settings
from .users import router as users_router
from .auth import router as auth_router
from .files import router as files_router
from .email import router as email_router
from fastapi.security import HTTPBearer

http_bearer = HTTPBearer(auto_error=False)

api_router = APIRouter(
    prefix=settings.api.v1.prefix,
    dependencies=[
        Depends(http_bearer),
    ],
)

api_router.include_router(users_router)
api_router.include_router(auth_router)
api_router.include_router(files_router)
api_router.include_router(email_router)
