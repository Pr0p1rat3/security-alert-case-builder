from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import IocType, Verdict


class IOC(Base):
    __tablename__ = "iocs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    alert_id: Mapped[int | None] = mapped_column(ForeignKey("alerts.id"), nullable=True)
    type: Mapped[IocType] = mapped_column(Enum(IocType), index=True)
    value: Mapped[str] = mapped_column(String(2048), index=True)
    raw_value: Mapped[str] = mapped_column(String(2048))
    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    case = relationship("Case", back_populates="iocs")
    enrichments = relationship("IOCEnrichment", back_populates="ioc", cascade="all, delete-orphan")


class IOCEnrichment(Base):
    __tablename__ = "ioc_enrichments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ioc_id: Mapped[int] = mapped_column(ForeignKey("iocs.id"), index=True)
    provider_name: Mapped[str] = mapped_column(String(120))
    verdict: Mapped[Verdict] = mapped_column(Enum(Verdict), default=Verdict.unknown)
    confidence: Mapped[float] = mapped_column(Float, default=0)
    summary: Mapped[str] = mapped_column(Text)
    raw_response: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    enriched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    ioc = relationship("IOC", back_populates="enrichments")


class AllowlistEntry(Base):
    __tablename__ = "allowlist_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(String(2048), unique=True, index=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)


class BlocklistEntry(Base):
    __tablename__ = "blocklist_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    value: Mapped[str] = mapped_column(String(2048), unique=True, index=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
