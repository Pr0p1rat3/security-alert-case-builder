from __future__ import annotations

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import MappingStatus


class MITRETechnique(Base):
    __tablename__ = "mitre_techniques"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    technique_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    technique_name: Mapped[str] = mapped_column(String(200))
    tactic: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class CaseTechniqueMapping(Base):
    __tablename__ = "case_technique_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    technique_id: Mapped[int] = mapped_column(ForeignKey("mitre_techniques.id"))
    why_suggested: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    related_evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    analyst_status: Mapped[MappingStatus] = mapped_column(
        Enum(MappingStatus), default=MappingStatus.suggested
    )

    case = relationship("Case", back_populates="technique_mappings")
    technique = relationship("MITRETechnique")
