from typing import TYPE_CHECKING
from src.core.models.uploaded_file import UploadedFiles
from src.core.repository.base import BaseRepository
from src.core.schemas.uploaded_file import (
    UploadedFileCreate,
    UploadedFileRead,
    UploadedFileUpdate,
)


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class UploadedFileRepository(
    BaseRepository[
        UploadedFileRead,
        UploadedFileCreate,
        UploadedFileUpdate,
    ]
):
    model = UploadedFiles
    read_schema = UploadedFileRead
    update_schema = UploadedFileUpdate
    create_schema = UploadedFileCreate

    def __init__(self, session: "AsyncSession") -> None:
        super().__init__(session)
