from __future__ import annotations

from datetime import datetime
import enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models.mixins.int_id_pk import IntIdPkMixin
from src.database import Base

if TYPE_CHECKING:
    from src.core.models.users import User


class UploadedFiles(IntIdPkMixin, Base):
    __tablename__ = "uploaded_files"

    file_name: Mapped[str] = mapped_column(String)
    file_path: Mapped[str] = mapped_column(String)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
    )

    user: Mapped["User"] = relationship(back_populates="uploaded_files")
