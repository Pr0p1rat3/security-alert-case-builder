from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class EvidenceFile(Base):
    __tablename__ = "evidence_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    timeline_event_id: Mapped[int | None] = mapped_column(
        ForeignKey("timeline_events.id"), nullable=True
    )
    file_name: Mapped[str] = mapped_column(String(255))
    storage_path: Mapped[str] = mapped_column(String(1000))
    content_type: Mapped[str] = mapped_column(String(120))
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    size_bytes: Mapped[int] = mapped_column(Integer)
    uploaded_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    case = relationship("Case", back_populates="evidence")
    uploaded_by = relationship("User")
