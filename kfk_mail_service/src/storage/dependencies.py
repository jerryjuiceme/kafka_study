from typing import Literal


from src.config import settings
from src.storage.storage import (
    LocalStorageService,
    StorageService,
)


##########################
## STORAGE DEPENDENCIES ##
##########################


def get_storage_service(filetype: Literal["html", "csv"]) -> StorageService:
    local_path = settings.storage.local_storage_csv_path
    return LocalStorageService(
        filetype=filetype,
        base_path=local_path,
    )


async def get_csv_storage_service() -> StorageService:
    return get_storage_service(filetype="csv")


async def get_html_storage_service() -> StorageService:
    return get_storage_service(filetype="html")
