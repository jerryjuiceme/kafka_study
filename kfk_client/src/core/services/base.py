from typing import Callable, Self, TypeVar, Generic, TYPE_CHECKING

from sqlalchemy import Sequence

from src.core.repository.base import BaseRepository, BaseRepositoryProtocol

from src.core.schemas.base import (
    BaseModel,
    CreateBaseModel,
    PaginationBaseSchema,
    PaginationResultSchema,
    UpdateBaseModel,
)


R = TypeVar("R", bound=BaseRepository)
ModelType = TypeVar("ModelType")
ReadSchemaType = TypeVar("ReadSchemaType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=CreateBaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=UpdateBaseModel)
IntT = TypeVar("IntT", bound=int)


class BaseService(
    Generic[R, ModelType, ReadSchemaType, CreateSchemaType, UpdateSchemaType]
):
    def __init__(self, repository: R) -> None:
        self.repository = repository

    async def get_all(self) -> list[ReadSchemaType] | None:
        return await self.repository.get_all()

    async def get_by_id(self, id: int) -> ReadSchemaType | None:
        return await self.repository.get_by_id(id)

    async def get_one_or_none(self: Self, **kwargs: Callable) -> ReadSchemaType | None:
        return await self.repository.get_one_or_none(**kwargs)

    async def get_by_ids(
        self: Self, ids: Sequence[IntT]
    ) -> list[ReadSchemaType] | None:
        return await self.repository.get_by_ids(ids)  # type: ignore

    async def paginate(
        self: Self, params: PaginationBaseSchema
    ) -> PaginationResultSchema[ReadSchemaType] | None:
        return await self.repository.paginate(params)

    async def add_data(self: Self, **kwargs):
        return await self.repository.add_data(**kwargs)

    async def create(self: Self, create_object: CreateBaseModel):
        return await self.repository.create(create_object)

    async def bulk_create(self: Self, create_objects: Sequence[CreateBaseModel]):
        return await self.repository.bulk_create(create_objects)  # type: ignore

    async def update(self: Self, update_object: UpdateBaseModel):
        return await self.repository.update(update_object)

    async def bulk_update(self: Self, update_objects: Sequence[UpdateBaseModel]):
        return await self.repository.bulk_update(update_objects)  # type: ignore

    async def delete(self: Self, id: int):
        return await self.repository.delete(id)

    async def upsert(self: Self, create_object: CreateBaseModel):
        return await self.repository.upsert(create_object)
