from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.models.enums import IocType, Verdict


@dataclass(frozen=True)
class EnrichmentResult:
    provider_name: str
    verdict: Verdict
    confidence: float
    summary: str
    raw_response: dict[str, Any]


class EnrichmentProvider:
    name = "base"

    def enrich(self, ioc_type: IocType, value: str) -> EnrichmentResult:
        raise NotImplementedError


class DnsLookupProvider(EnrichmentProvider):
    name = "dns_lookup"

    def enrich(self, ioc_type: IocType, value: str) -> EnrichmentResult:
        if ioc_type != IocType.domain:
            return unknown(self.name, "DNS lookup applies to domains only")
        return unknown(self.name, f"DNS lookup placeholder for {value}")


class PlaceholderProvider(EnrichmentProvider):
    def __init__(self, name: str, summary: str) -> None:
        self.name = name
        self._summary = summary

    def enrich(self, ioc_type: IocType, value: str) -> EnrichmentResult:
        return unknown(self.name, f"{self._summary}: {value}")


class LocalListProvider(EnrichmentProvider):
    name = "internal_lists"

    def __init__(self, allowlist: set[str], blocklist: set[str]) -> None:
        self.allowlist = allowlist
        self.blocklist = blocklist

    def enrich(self, ioc_type: IocType, value: str) -> EnrichmentResult:
        if value in self.allowlist:
            return EnrichmentResult(
                self.name,
                Verdict.benign,
                0.95,
                "IOC is present on the internal allowlist.",
                {"list": "allowlist"},
            )
        if value in self.blocklist:
            return EnrichmentResult(
                self.name,
                Verdict.malicious,
                0.95,
                "IOC is present on the internal blocklist.",
                {"list": "blocklist"},
            )
        return unknown(self.name, "IOC was not present on internal allowlist/blocklist.")


def default_providers(
    allowlist: set[str] | None = None, blocklist: set[str] | None = None
) -> list[EnrichmentProvider]:
    return [
        LocalListProvider(allowlist or set(), blocklist or set()),
        DnsLookupProvider(),
        PlaceholderProvider("whois_rdap", "WHOIS/RDAP provider placeholder"),
        PlaceholderProvider("geoip", "GeoIP provider placeholder"),
        PlaceholderProvider("reputation", "Reputation provider placeholder"),
        PlaceholderProvider("cisa_kev", "CISA KEV provider placeholder for CVEs"),
        PlaceholderProvider("mitre_suggestion", "MITRE technique suggestion provider placeholder"),
    ]


def unknown(provider_name: str, summary: str) -> EnrichmentResult:
    return EnrichmentResult(
        provider_name=provider_name,
        verdict=Verdict.unknown,
        confidence=0.2,
        summary=summary,
        raw_response={"timestamp": datetime.now(UTC).isoformat(), "placeholder": True},
    )
