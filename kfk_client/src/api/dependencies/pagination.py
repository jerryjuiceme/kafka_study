from typing import Annotated
from fastapi import Depends
from src.core.schemas.base import PaginationBaseSchema


PaginationDep = Annotated[PaginationBaseSchema, Depends(PaginationBaseSchema)]
