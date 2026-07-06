from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import CaseStatus, Severity

case_tags_table = Table(
    "case_tags",
    Base.metadata,
    Column("case_id", ForeignKey("cases.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(300), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    severity: Mapped[Severity] = mapped_column(Enum(Severity), default=Severity.medium)
    status: Mapped[CaseStatus] = mapped_column(Enum(CaseStatus), default=CaseStatus.new)
    source_system: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assigned_analyst_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    close_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    business_impact: Mapped[str | None] = mapped_column(Text, nullable=True)
    affected_users: Mapped[str | None] = mapped_column(Text, nullable=True)
    affected_hosts: Mapped[str | None] = mapped_column(Text, nullable=True)
    affected_ips: Mapped[str | None] = mapped_column(Text, nullable=True)
    affected_domains_urls: Mapped[str | None] = mapped_column(Text, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="created_cases")
    assigned_analyst = relationship("User", foreign_keys=[assigned_analyst_id])
    alerts = relationship("Alert", back_populates="case", cascade="all, delete-orphan")
    iocs = relationship("IOC", back_populates="case", cascade="all, delete-orphan")
    timeline_events = relationship(
        "TimelineEvent", back_populates="case", cascade="all, delete-orphan"
    )
    evidence = relationship("EvidenceFile", back_populates="case", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="case", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="case", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="case", cascade="all, delete-orphan")
    technique_mappings = relationship(
        "CaseTechniqueMapping", back_populates="case", cascade="all, delete-orphan"
    )
    tags = relationship("Tag", secondary=case_tags_table, back_populates="cases")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    cases = relationship("Case", secondary=case_tags_table, back_populates="tags")


class CaseTag(Base):
    __tablename__ = "case_tag_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"))
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"))
