from __future__ import annotations

from pathlib import Path

from app.mitre.engine import suggest_techniques
from app.parsers.alert_parser import parse_alert
from app.parsers.ioc_extractor import extract_iocs

ROOT = Path(__file__).resolve().parents[3]
SAMPLE = ROOT / "sample_data"


def test_ioc_extraction_normalizes_url_and_domain() -> None:
    raw = "Visit HTTPS://Example.COM/login?id=1#frag from 203.0.113.10 and email User@Example.COM"
    values = {(ioc.type.value, ioc.value) for ioc in extract_iocs(raw)}
    assert ("url", "https://example.com/login?id=1") in values
    assert ("ipv4", "203.0.113.10") in values
    assert ("email", "user@example.com") in values


def test_alert_parser_handles_sophos_fixture() -> None:
    parsed = parse_alert((SAMPLE / "sophos_endpoint_apcviolation.txt").read_text())
    assert parsed.alert_type == "sophos_endpoint"
    assert parsed.fields["hostname"] == "FIN-LAPTOP-022"
    assert parsed.fields["username"] == "contoso\\jane.smith"
    assert parsed.fields["extracted_ioc_count"] >= 2


def test_mitre_suggestions_are_defensive_and_uncertain() -> None:
    suggestions = suggest_techniques(
        "PowerShell EncodedCommand observed in a WAF SQL injection case"
    )
    technique_ids = {item["technique_id"] for item in suggestions}
    assert "T1059.001" in technique_ids
    assert "T1190" in technique_ids
    assert all(float(item["confidence"]) < 1.0 for item in suggestions)
