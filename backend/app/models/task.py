from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import TaskStatus


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(40), default="Medium")
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.open)
    assigned_to_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    evidence_link: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    completion_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    case = relationship("Case", back_populates="tasks")
    assigned_to = relationship("User")
