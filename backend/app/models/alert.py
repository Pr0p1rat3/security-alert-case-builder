from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    source_system: Mapped[str | None] = mapped_column(String(120), nullable=True)
    alert_type: Mapped[str] = mapped_column(String(120), default="generic")
    raw_content: Mapped[str] = mapped_column(Text)
    parsed: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    case = relationship("Case", back_populates="alerts")
