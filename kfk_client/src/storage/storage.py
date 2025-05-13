from abc import ABC, abstractmethod
from typing import BinaryIO, Literal, IO
import aiofiles
import asyncio
import typing
from fastapi import FastAPI, UploadFile, Depends, HTTPException, status
from pathlib import Path
import shutil
import aiofiles
from aiofiles.threadpool.binary import AsyncBufferedReader
import io
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


class StorageService(ABC):
    @abstractmethod
    async def save_file(self, filename: str, file: UploadFile) -> str:
        pass

    @abstractmethod
    async def get_file(self, file_path_or_id: str) -> BinaryIO:
        pass


###########################
## LOCAL STORAGE SERVICE ##
###########################


class LocalStorageService(StorageService):
    def __init__(
        self,
        filetype: Literal["csv"],
        base_path: str,
    ):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.filetype = filetype

    async def save_file(self, filename: str, file: UploadFile) -> str:
        try:
            file_path = self.base_path / f"{filename}.{self.filetype}"
            async with aiofiles.open(file_path, "wb") as file_obj:
                contents = await file.read()
                await file_obj.write(contents)
            return str(file_path)
        except IOError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file locally: {str(e)}",
            )
        try:
            file_path = self.base_path / f"{filename}.{self.filetype}"
            with open(file_path, "wb") as file_obj:
                shutil.copyfileobj(file, file_obj)
            return str(file_path)
        except IOError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file locally: {str(e)}",
            )

    async def get_file(self, file_path_or_id: str) -> AsyncBufferedReader:
        try:
            if not Path(file_path_or_id).exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
                )
            return await aiofiles.open(file_path_or_id, "rb")
        except IOError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read file: {str(e)}",
            )


############################
## GOOGLE STORAGE SERVICE ##
############################


class GoogleDriveStorageService(StorageService):
    def __init__(
        self,
        credentials,
        folder_id: str,
        filetype: Literal["csv"],
    ):
        self.service = build("drive", "v3", credentials=credentials)
        self.folder_id = folder_id
        self.filetype = filetype

    async def save_file(self, filename: str, file: BinaryIO) -> str:
        try:
            file_metadata = {
                "name": f"{filename}.{self.filetype}",
                "parents": [self.folder_id],
            }
            media = MediaIoBaseUpload(file, mimetype=f"text/{self.filetype}")
            file_obj = (
                self.service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )
            return file_obj.get("id")
        except HttpError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Google Drive error: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload to Google Drive: {str(e)}",
            )

    async def get_file(self, file_path_or_id: str) -> BinaryIO:
        try:
            request = self.service.files().get_media(fileId=file_path_or_id)
            return request.execute()
        except HttpError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found in Google Drive: {str(e)}",
            )
