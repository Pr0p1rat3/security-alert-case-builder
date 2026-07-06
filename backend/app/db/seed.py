from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.mitre.engine import TECHNIQUES
from app.models import Case, MITRETechnique, SourceSystem, User
from app.models.enums import CaseStatus, Severity, UserRole

SOURCE_SYSTEMS = [
    "Sophos",
    "Proofpoint",
    "Fortra WAF",
    "Cisco Secure Access",
    "Alert Logic",
    "Microsoft Defender",
    "Windows Event Logs",
    "Sysmon",
    "Firewall",
    "DNS",
    "Proxy",
    "Generic",
]


def seed_initial_data(db: Session) -> None:
    settings = get_settings()
    admin = db.scalar(select(User).where(User.email == settings.seed_admin_email))
    if not admin:
        admin = User(
            email=settings.seed_admin_email,
            display_name="Seed Admin",
            password_hash=hash_password(settings.seed_admin_password),
            role=UserRole.admin,
            active=True,
        )
        db.add(admin)
        db.flush()

    for name in SOURCE_SYSTEMS:
        if not db.scalar(select(SourceSystem).where(SourceSystem.name == name)):
            db.add(SourceSystem(name=name, description=f"{name} alert source"))

    for technique in TECHNIQUES:
        if not db.scalar(
            select(MITRETechnique).where(MITRETechnique.technique_id == technique.technique_id)
        ):
            db.add(
                MITRETechnique(
                    technique_id=technique.technique_id,
                    technique_name=technique.technique_name,
                    tactic=technique.tactic,
                    description=technique.why,
                )
            )

    if settings.seed_demo_data and not db.scalar(
        select(Case).where(Case.title == "Sample phishing triage")
    ):
        db.add(
            Case(
                title="Sample phishing triage",
                description="Seed sample case for first-run validation.",
                severity=Severity.medium,
                status=CaseStatus.triage,
                source_system="Proofpoint",
                created_by_id=admin.id,
                assigned_analyst_id=admin.id,
                business_impact="No confirmed business impact. Sample case only.",
            )
        )
    db.commit()
