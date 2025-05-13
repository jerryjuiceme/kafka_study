from logging import getLogger
from pathlib import Path
from typing import Annotated, Any

from fastapi.responses import FileResponse
from fastapi import APIRouter, HTTPException, UploadFile, status, Depends


from src.broker.broker import BrokerProducer
from src.broker.dependencies import SendCsvTopicDep
from src.config import settings
from src.core.models.users import User
from src.core.schemas.api_message import BaseOutputMessage
from src.utils.string import NOT_IMPLEMENTED, name_to_snake
from src.storage.dependencies import CsvStorageDep, validate_csv
from src.storage.storage import StorageService

# from src.broker.broker import broker, exch
from src.api.api_v1.fastapi_users_main import current_active_user
from src.core.schemas.uploaded_file import UploadedFileCreate, UploadedFileRead
from src.core.services.uploaded_file import (
    UploadedFilesService,
    UploadedFilesServiceDep,
)

logger = getLogger(__name__)


router = APIRouter(
    prefix="/files",
    tags=["Files"],
)


def iterfile(filename: str):
    with open(filename, "rb") as file:
        while chunk := file.read(1024 * 1024):
            yield chunk


CSV_PATH: Path = Path(settings.storage.template_file_path) / "csv" / "example.csv"


@router.get("/csv", name="example_csv")
async def get_csv():
    logger.info("File wit path %s is requested", CSV_PATH)

    return FileResponse(
        path=CSV_PATH,
        filename="test_example.csv",
        media_type="multipart/form-data",
    )


@router.post(
    "/upload_csv",
    dependencies=[Depends(validate_csv)],
    status_code=status.HTTP_201_CREATED,
    response_model=BaseOutputMessage[UploadedFileRead],
)
async def upload_csv(
    file: UploadFile,
    storage_service: Annotated[StorageService, CsvStorageDep],
    user: Annotated[User, Depends(current_active_user)],
    service: Annotated[UploadedFilesService, UploadedFilesServiceDep],
    broker: Annotated[BrokerProducer, SendCsvTopicDep],
) -> Any:
    """
    Uploads a CSV file and creates a campaign, queuing it for processing.
    """
    filename = name_to_snake(file.filename, "csv")  # type: ignore
    file_path = await storage_service.save_file(filename=filename, file=file)
    new_file = UploadedFileCreate(
        file_name=filename, user_id=user.id, file_path=file_path
    )
    new_file_record = await service.create(new_file)
    if not new_file_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=NOT_IMPLEMENTED
        )
    await broker.send_message(value=new_file_record)
    return BaseOutputMessage(data=new_file_record, message="File Uploaded")


@router.get("/", response_model=BaseOutputMessage[list[UploadedFileRead]])
async def get_all_files(
    service: Annotated[UploadedFilesService, UploadedFilesServiceDep],
):
    resutl = await service.get_all()
    return BaseOutputMessage(data=resutl, message="all_uploaded_files")
