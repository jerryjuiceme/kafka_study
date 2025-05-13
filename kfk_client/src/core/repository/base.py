from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    Optional,
    Protocol,
    Self,
    Sequence,
    TYPE_CHECKING,
    TypeVar,
)

from fastapi import HTTPException
from sqlalchemy import (
    Delete,
    Insert,
    Select,
    func,
    insert,
    select,
    update,
    UnaryExpression,
)

from src.core.schemas.base import (
    BaseModel,
    CreateBaseModel,
    PaginationBaseSchema,
    PaginationResultSchema,
    UpdateBaseModel,
)

if TYPE_CHECKING:
    from src.database import Base
    from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepositoryProtocol(Protocol):

    async def get_all(self: Self) -> Any: ...

    async def get_by_id(self: Self, id: int) -> Any: ...

    async def get_one_or_none(self: Self, **kwargs) -> Any: ...

    async def get_by_ids(self: Self, ids: Sequence[int]) -> Any: ...

    async def paginate(self: Self, params: PaginationBaseSchema) -> Any: ...

    async def add_data(self: Self, **kwargs) -> Any: ...

    async def create(self: Self, create_object: CreateBaseModel) -> Any: ...

    async def bulk_create(
        self: Self, create_objects: Sequence[CreateBaseModel]
    ) -> Any: ...

    async def update(self: Self, update_object: UpdateBaseModel) -> Any: ...

    async def bulk_update(
        self: Self,
        update_objects: Sequence[UpdateBaseModel],
    ) -> Any: ...

    async def delete(self: Self, id: int) -> Any: ...

    async def upsert(self: Self, create_object: CreateBaseModel) -> Any: ...


ReadSchemaT = TypeVar("ReadSchemaT", bound=BaseModel)
CreateSchemaT = TypeVar("CreateSchemaT", bound=CreateBaseModel)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=UpdateBaseModel)


class BaseRepository(Generic[ReadSchemaT, CreateSchemaT, UpdateSchemaT]):
    model = None
    read_schema: type[ReadSchemaT]
    create_schema: type[CreateSchemaT]
    update_schema: type[UpdateSchemaT]

    def __init__(self, session: "AsyncSession") -> None:
        """
        Base CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `read_schema`: A Pydantic model (schema) class
        * `update_schema`: A Pydantic model (schema) class
        * `create_schema`: A Pydantic model (schema) class
        """
        self.session = session

    async def get_all(self) -> list[ReadSchemaT] | None:
        if self.model:
            # await self.session.connection(execution_options={"isolation_level": "SERIALIZABLE"})
            stmt = select(self.model.__table__.columns)
            result = await self.session.execute(stmt)
            return [
                self.read_schema.model_validate(m, from_attributes=True)
                for m in result.mappings().all()
            ]

    async def get_by_id(self: Self, id: int) -> ReadSchemaT | None:
        if self.model:
            stmt = select(self.model).where(self.model.id == id)
            result = await self.session.execute(stmt)
            result = result.scalar_one_or_none()
            return self.read_schema.model_validate(result, from_attributes=True)

    async def get_one_or_none(self: Self, **kwargs: Callable) -> ReadSchemaT | None:
        if self.model:
            stmt = select(self.model).filter_by(**kwargs)
            result = await self.session.execute(stmt)
            result = result.scalar_one_or_none()
            return self.read_schema.model_validate(result, from_attributes=True)

    async def get_by_ids(self: Self, ids: Sequence[int]) -> list[ReadSchemaT] | None:
        if self.model:
            stmt = select(self.model).filter(self.model.id.in_(ids))
            result = await self.session.execute(stmt)
            return [
                self.read_schema.model_validate(m, from_attributes=True)
                for m in result.mappings().all()
            ]

    async def paginate(
        self: Self,
        params: PaginationBaseSchema,
    ) -> PaginationResultSchema[ReadSchemaT] | None:
        if self.model:
            offset = (params.page - 1) * params.page_size
            order_by_expr = self.get_order_by_expr(
                sort_by=params.sort_by, order_by=params.sort_order
            )
            stmt = (
                select(self.model)
                .offset(offset)
                .limit(params.page_size)
                .order_by(order_by_expr)
            )
            result = (await self.session.execute(stmt)).scalars().all()
            objects = [
                self.read_schema.model_validate(m, from_attributes=True) for m in result
            ]
            count_stmt = select(self.model).with_only_columns(func.count(self.model.id))
            count = (await self.session.execute(count_stmt)).scalar_one()
            return PaginationResultSchema(objects=objects, count=count)

    async def add_data(self: Self, **kwargs: Callable) -> None:
        if self.model:
            stmt: Insert = insert(self.model).values(**kwargs)
            await self.session.execute(stmt)
            await self.session.commit()

    async def create(self: Self, create_object: CreateSchemaT) -> ReadSchemaT | None:
        if self.model:
            model = self.model(**create_object.__dict__)
            self.session.add(model)
            await self.session.flush()
            await self.session.commit()
            return self.read_schema.model_validate(model, from_attributes=True)

    async def bulk_create(
        self: Self, create_objects: Sequence[CreateSchemaT]
    ) -> list[CreateSchemaT] | None:
        if self.model:
            stmt: Insert = insert(self.model).values(
                [m.__dict__ for m in create_objects]
            )
            await self.session.execute(stmt)
            await self.session.commit()
            return [
                self.create_schema.model_validate(m, from_attributes=True)
                for m in create_objects
            ]

    async def update(self: Self, update_object: UpdateSchemaT) -> None:
        if self.model:
            stmt = (
                update(self.model)
                .where(self.model.id == update_object.id)
                .values(**update_object.__dict__)
            )

            await self.session.execute(stmt)
            await self.session.commit()

    async def bulk_update(self: Self, update_objects: Sequence[UpdateSchemaT]) -> None:
        if self.model:
            stmt = (
                update(self.model)
                .where(self.model.id.in_([m.id for m in update_objects]))
                .values(**update_objects[0].__dict__)
            )

            await self.session.execute(stmt)
            await self.session.commit()

    async def delete(self: Self, id: int) -> None:
        if self.model:
            stmt = Delete(self.model).where(self.model.id == id)
            await self.session.execute(stmt)
            await self.session.commit()

    async def upsert(self: Self, create_object: CreateSchemaT) -> CreateSchemaT | None:
        if self.model:
            stmt = (
                insert(self.model)
                .values(**create_object.__dict__)
                .returning(self.model)
            )
            new_instance = await self.session.execute(stmt)
            await self.session.commit()

            return self.create_schema.model_validate(new_instance, from_attributes=True)

    def get_order_by_expr(
        self: Self, sort_by: str, order_by: str = "asc"
    ) -> UnaryExpression:
        try:
            if order_by == "asc":
                order_by_expr = getattr(self.model, sort_by).asc()
            else:
                order_by_expr = getattr(self.model, sort_by).desc()
        except AttributeError as attribute_error:
            raise HTTPException(status_code=400, detail=str(attribute_error))

        return order_by_expr
