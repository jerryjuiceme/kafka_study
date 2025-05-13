from typing import Annotated, Any, AsyncGenerator, Generator
from fastapi import Depends, Request
from sqlalchemy import MetaData, NullPool, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase, Session

from src.config import settings

DATABASE_PARAMS: dict[Any, Any] = {}

async_engine: AsyncEngine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=settings.db.echo,
    **DATABASE_PARAMS,
)

async_session_factory = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def dispose() -> None:
    await async_engine.dispose()


async def get_db_async():
    """
    Get database session from direct dependency.
    Legacy.
    """
    try:
        async with async_session_factory() as session:
            yield session
    finally:
        await session.close()


async def get_db_request(request: Request) -> Session:
    """Get database session from request state."""
    session = request.state.db
    return session


SessionDep: Annotated["AsyncSession", Depends(get_db_request)]


class Base(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(naming_convention=settings.db.naming_convention)
