from enum import Enum
from typing import TYPE_CHECKING
from src.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, text
from datetime import datetime, timezone
from .mixins.int_id_pk import IntIdPkMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase



if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from src.core.models.uploaded_file import UploadedFiles


class User(Base, IntIdPkMixin, SQLAlchemyBaseUserTable[int]):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(length=100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
        # onupdate=datetime.now(timezone.utc), # replaced with trigger
    )

    # access_tokens: Mapped[list["AccessToken"]] = relationship(back_populates="user")
    uploaded_files: Mapped[list["UploadedFiles"]] = relationship(back_populates="user")

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        return SQLAlchemyUserDatabase(session, User)
