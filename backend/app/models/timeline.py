from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    alert_id: Mapped[int | None] = mapped_column(ForeignKey("alerts.id"), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    event_type: Mapped[str] = mapped_column(String(120), index=True)
    source_system: Mapped[str | None] = mapped_column(String(120), nullable=True)
    short_title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text)
    related_user: Mapped[str | None] = mapped_column(String(300), nullable=True)
    related_host: Mapped[str | None] = mapped_column(String(300), nullable=True)
    related_entity: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    case = relationship("Case", back_populates="timeline_events")
