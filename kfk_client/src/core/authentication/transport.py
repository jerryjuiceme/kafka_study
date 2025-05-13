from fastapi_users.authentication import BearerTransport

from src.config import settings

bearer_transport = BearerTransport(
    # TODO: add tokenUrl
    tokenUrl=f"{settings.api.prefix}{settings.api.v1.prefix}/auth/login",
)
