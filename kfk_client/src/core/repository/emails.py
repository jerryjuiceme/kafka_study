from typing import TYPE_CHECKING
from src.core.models.emails import Emails
from src.core.repository.base import BaseRepository
from src.core.schemas.emails import EmailRead, EmailCreate, EmailUpdate


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class EmailRepository(BaseRepository[EmailRead, EmailCreate, EmailUpdate]):
    model = Emails
    read_schema = EmailRead
    update_schema = EmailUpdate
    create_schema = EmailCreate

    def __init__(self, session: "AsyncSession") -> None:
        super().__init__(session)
