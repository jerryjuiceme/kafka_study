import io
from typing import Literal
from fastapi import FastAPI, UploadFile, Depends, HTTPException, status
from pathlib import Path
import csv
from google.oauth2.credentials import Credentials
from starlette.formparsers import MultiPartParser
from src.config import settings
from src.storage.storage import (
    GoogleDriveStorageService,
    LocalStorageService,
    StorageService,
)

### Change default max file size
### Set max RAM upload filesize via MultiPartParser from starlette
MAX_FILE_SIZE: int = 1 * 1024 * 1024  # 1MB
MultiPartParser.max_part_size = MAX_FILE_SIZE


#######################
## FILE VALIDATIONS ##
#######################


async def validate_csv(file: UploadFile) -> None:
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the maximum allowed 4MB",
        )
    await file.seek(0)

    if file is not None and file.filename is not None:
        if not file.filename.lower().endswith(".csv"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a CSV",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded or no filename provided",
        )

    try:
        # read the first 10240 bytes (10kb)
        content = await file.read(10240)
        # Проверяем, что это валидный CSV
        text = content.decode("utf-8-sig")
        dialect = csv.Sniffer().sniff(text)
        await file.seek(0)
        # Проверяем заголовки столбцов
        reader = csv.DictReader(io.StringIO(text), dialect=dialect)
        required_columns = {
            "subject",
            "from_email",
            "to_email",
            "message_body",
        }
        if not reader.fieldnames:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV file has no headers",
            )

        missing_columns = required_columns - set(reader.fieldnames)
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CSV file is missing required columns: {', '.join(missing_columns)}",
            )

        # Возвращаем указатель в начало файла
        await file.seek(0)
    except (UnicodeDecodeError, csv.Error) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid CSV format",
        )
    except HTTPException:
        raise  # Перебрасываем уже созданные HTTPException
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating CSV: {str(e)}",
        )


##########################
## STORAGE DEPENDENCIES ##
##########################


def get_storage_service(filetype: Literal["csv"]) -> StorageService:
    local_path = settings.storage.local_storage_csv_path
    return LocalStorageService(
        filetype=filetype,
        base_path=local_path,
    )


async def get_csv_storage_service() -> StorageService:
    return get_storage_service(filetype="csv")


CsvStorageDep = Depends(get_csv_storage_service)
