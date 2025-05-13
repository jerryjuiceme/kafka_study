from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from faststream import Depends as FastDepends

from src.database import get_db_request, get_db_async, async_session_factory
from src.core.services.base import BaseService
from src.core.models.emails import Emails
from src.core.schemas.emails import EmailCreate, EmailRead, EmailUpdate
from src.core.repository.emails import EmailRepository


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class EmailsService(
    BaseService[
        EmailRepository,
        Emails,
        EmailRead,
        EmailCreate,
        EmailUpdate,
    ]
): ...


async def get_db_async_stream():
    """
    Get database session from direct dependency.
    Legacy.
    """
    try:
        async with async_session_factory() as session:
            yield session
    finally:
        await session.close()


##################
## REPOSITORIES ##
##################


async def get_emails_repository(
    session: "AsyncSession" = Depends(get_db_request),
) -> EmailRepository:
    return EmailRepository(session)


EmailRepositoryDep = Annotated[
    "EmailRepository",
    Depends(get_emails_repository),
]


##############
## SERVICES ##
##############


async def get_emails_service(rep: EmailRepositoryDep) -> EmailsService:
    return EmailsService(rep)


EmailsServiceDep = Depends(get_emails_service)
