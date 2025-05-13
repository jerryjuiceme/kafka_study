from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from src.database import get_db_request
from src.core.services.base import BaseService
from src.core.models.uploaded_file import UploadedFiles
from src.core.schemas.uploaded_file import (
    UploadedFileCreate,
    UploadedFileRead,
    UploadedFileUpdate,
)
from src.core.repository.uploaded_file import UploadedFileRepository


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class UploadedFilesService(
    BaseService[
        UploadedFileRepository,
        UploadedFiles,
        UploadedFileRead,
        UploadedFileCreate,
        UploadedFileUpdate,
    ]
): ...


##################
## REPOSITORIES ##
##################


async def get_uploaded_file_repository(
    session: "AsyncSession" = Depends(get_db_request),
) -> UploadedFileRepository:
    return UploadedFileRepository(session)


UploadedFileRepositoryDep = Annotated[
    "UploadedFileRepository",
    Depends(get_uploaded_file_repository),
]

##############
## SERVICES ##
##############


async def get_uploaded_file_service(
    rep: UploadedFileRepositoryDep,
) -> UploadedFilesService:
    return UploadedFilesService(rep)


UploadedFilesServiceDep = Depends(get_uploaded_file_service)
