import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Text,
    func,
    JSON,
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base import Base


class Result(Base):
    __tablename__ = "results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    key_points: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )

    flashcards: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    task = relationship(
        "Task",
        back_populates="result",
    )