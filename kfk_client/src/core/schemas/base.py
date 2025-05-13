"""
Base schemas module
"""

import uuid
from typing import Generic, Literal, TypeVar

from pydantic import AliasGenerator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CreateBaseModel(BaseModel):
    """
    Schema for creating models
    """

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None


class UpdateBaseModel(BaseModel):
    """
    Schema for updating models
    """

    model_config = ConfigDict(from_attributes=True)

    id: int


class StatusOkSchema(BaseModel):
    """
    Schema for status ok
    """

    status: str = "ok"


# class PaginationSchema(BaseModel):
#     """
#     Schema for pagination
#     """

#     limit: int
#     offset: int


class PaginationBaseSchema(BaseModel):
    """
    Schema for pagination
    """

    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Items per page")
    sort_by: str = "id"
    sort_order: Literal["asc", "desc"] = "asc"


T = TypeVar("T")


class PaginationResultSchema(BaseModel, Generic[T]):
    """
    Schema for pagination result
    """

    objects: list[T]
    count: int


class InputApiSchema(BaseModel):
    """
    Input API schema
    """

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
        )
    )


class OutputApiSchema(BaseModel):
    """
    Output API schema
    """

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            serialization_alias=to_camel,
        )
    )
