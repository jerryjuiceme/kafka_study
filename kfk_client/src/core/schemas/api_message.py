"""
Api Base Message Module
"""

import uuid
from typing import Generic, Literal, TypeVar

from pydantic import AliasGenerator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.core.schemas.base import OutputApiSchema


T = TypeVar("T")


class BaseOutputMessage(OutputApiSchema, Generic[T]):
    """
    Base Message schema
    """

    data: T
    message: str
