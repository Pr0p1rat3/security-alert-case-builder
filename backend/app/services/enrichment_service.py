from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enrichment.providers import default_providers
from app.models import IOC, AllowlistEntry, BlocklistEntry, IOCEnrichment


def enrich_ioc(db: Session, ioc: IOC) -> list[IOCEnrichment]:
    allowlist = set(db.scalars(select(AllowlistEntry.value)).all())
    blocklist = set(db.scalars(select(BlocklistEntry.value)).all())
    results: list[IOCEnrichment] = []
    for provider in default_providers(allowlist, blocklist):
        result = provider.enrich(ioc.type, ioc.value)
        record = IOCEnrichment(
            ioc_id=ioc.id,
            provider_name=result.provider_name,
            verdict=result.verdict,
            confidence=result.confidence,
            summary=result.summary,
            raw_response=result.raw_response,
        )
        db.add(record)
        results.append(record)
    db.flush()
    return results
