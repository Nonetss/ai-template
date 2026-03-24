import uuid
from datetime import datetime, timezone

from sqlalchemy import Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from utils.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: uuid.uuid7().hex)
    title: Mapped[str | None] = mapped_column(Text, default=None)
    messages_json: Mapped[list[dict]] = mapped_column(JSON, default=[])
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
