from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models.mixins.int_id_pk import IntIdPkMixin
from src.database import Base


class Emails(IntIdPkMixin, Base):
    __tablename__ = "emails"

    subject: Mapped[str] = mapped_column(String)
    from_email: Mapped[str] = mapped_column(String)
    to_email: Mapped[str] = mapped_column(String)
    message_body: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("TIMEZONE('utc', now())")
    )
