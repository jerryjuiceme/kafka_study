from abc import ABC, abstractmethod
import csv
import aiocsv
from typing import AsyncGenerator, BinaryIO, Literal
from pathlib import Path
import shutil
import aiofiles
from aiofiles.threadpool.binary import AsyncBufferedReader


class StorageService(ABC):
    @abstractmethod
    async def get_file(self, file_path_or_id: str) -> BinaryIO:
        pass


###########################
## LOCAL STORAGE SERVICE ##
###########################


class LocalStorageService(StorageService):
    def __init__(
        self,
        filetype: Literal["csv", "html", "template"],
        base_path: str,
    ):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.filetype = filetype

    async def get_file(self, file_path_or_id: str | Path) -> AsyncBufferedReader:
        try:
            if not Path(file_path_or_id).exists():
                raise FileNotFoundError(f'File "{file_path_or_id}" not found')
            return await aiofiles.open(file_path_or_id, "rb")
        except IOError as e:
            raise IOError(f"Failed to save file: {str(e)}")


async def read_csv_file(file_path_or_id: str | Path) -> AsyncGenerator[dict, None]:
    try:
        if not Path(file_path_or_id).exists():
            raise FileNotFoundError(f'File "{file_path_or_id}" not found')
        async with aiofiles.open(file_path_or_id, "r", encoding="utf-8-sig") as f:
            reader = aiocsv.AsyncDictReader(f, delimiter=",")
            async for row in reader:
                yield row
    except Exception as e:
        raise ValueError(f"Failed to read file: {str(e)}")
