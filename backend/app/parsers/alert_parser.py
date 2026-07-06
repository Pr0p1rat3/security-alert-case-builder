from __future__ import annotations

import csv
import io
import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from app.parsers.ioc_extractor import extract_iocs

KEY_VALUE_RE = re.compile(r"^\s*([A-Za-z0-9_. -]{2,60})\s*[:=]\s*(.+?)\s*$")


@dataclass
class ParsedAlert:
    alert_type: str
    fields: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.5


def parse_alert(raw: str, supplied_type: str | None = None) -> ParsedAlert:
    text = raw.strip()
    if not text:
        return ParsedAlert("empty", {"raw_message": raw}, 0.1)

    if supplied_type:
        return _parse_by_hint(text, supplied_type)

    if text.startswith("{") or text.startswith("["):
        return parse_json_alert(text)
    if "," in text.splitlines()[0] and len(text.splitlines()) >= 2:
        return parse_csv_alert(text)
    return parse_text_alert(text)


def parse_json_alert(raw: str) -> ParsedAlert:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return parse_text_alert(raw)
    flattened = _flatten(payload)
    alert_type = detect_alert_type(raw, flattened)
    return ParsedAlert(alert_type, enrich_fields(flattened, raw), 0.85)


def parse_csv_alert(raw: str) -> ParsedAlert:
    reader = csv.DictReader(io.StringIO(raw))
    rows = [row for row in reader]
    if not rows:
        return ParsedAlert("generic_csv", {"raw_message": raw}, 0.4)
    first = {key: value for key, value in rows[0].items() if key}
    return ParsedAlert("generic_csv", enrich_fields(first | {"row_count": len(rows)}, raw), 0.75)


def parse_text_alert(raw: str) -> ParsedAlert:
    fields: dict[str, Any] = {"raw_message": raw}
    for line in raw.splitlines():
        match = KEY_VALUE_RE.match(line)
        if match:
            key = normalize_key(match.group(1))
            fields[key] = normalize_text_value(key, match.group(2).strip())
    return ParsedAlert(
        detect_alert_type(raw, fields),
        enrich_fields(fields, raw),
        0.65 if len(fields) > 1 else 0.45,
    )


def _parse_by_hint(raw: str, hint: str) -> ParsedAlert:
    normalized = hint.lower()
    if normalized == "json":
        return parse_json_alert(raw)
    if normalized == "csv":
        return parse_csv_alert(raw)
    return parse_text_alert(raw)


def detect_alert_type(raw: str, fields: dict[str, Any]) -> str:
    text = raw.lower()
    if "sophos" in text or "apcviolation" in text:
        return "sophos_endpoint"
    if "proofpoint" in text or "phish" in text or "message-id" in text:
        return "proofpoint_email"
    if "waf" in text or "sql injection" in text or "xss" in text:
        return "waf"
    if "sysmon" in text or str(fields.get("event_id", "")) == "1":
        return "sysmon"
    if "event id" in text or "eventid" in fields or "event_id" in fields:
        return "windows_event"
    if "dns" in text or "proxy" in text or "firewall" in text:
        return "network"
    return "generic"


def enrich_fields(fields: dict[str, Any], raw: str) -> dict[str, Any]:
    result = {normalize_key(str(key)): value for key, value in fields.items()}
    text = raw + "\n" + json.dumps(result, default=str)
    iocs = extract_iocs(text)

    by_type = {ioc.type.value: ioc.value for ioc in iocs}
    aliases = {
        "source_ip": ["source_ip", "src_ip", "src", "client_ip", "ipaddress"],
        "destination_ip": ["destination_ip", "dst_ip", "dest_ip", "dst"],
        "hostname": ["hostname", "host", "computer", "device_name", "endpoint"],
        "username": ["username", "user", "account", "targetusername", "user_name"],
        "email": ["email", "sender", "recipient", "from", "to"],
        "url": ["url", "uri", "request_url"],
        "domain": ["domain", "fqdn", "query_name"],
        "event_id": ["event_id", "eventid", "id"],
        "signature": ["signature", "rule", "rule_name", "signature_name", "threat_name"],
        "command_line": ["command_line", "commandline", "process_command_line"],
        "process_name": ["process_name", "image", "process"],
        "parent_process": ["parent_process", "parentimage", "parent_process_name"],
        "http_method": ["method", "http_method"],
        "http_path": ["path", "uri_path", "http_path"],
        "status_code": ["status", "status_code", "http_status"],
        "country": ["country", "geo_country"],
        "asn": ["asn"],
        "timestamp": ["timestamp", "time", "timecreated", "event_time"],
    }
    for canonical, keys in aliases.items():
        if canonical not in result:
            for key in keys:
                if key in result and result[key] not in (None, ""):
                    result[canonical] = result[key]
                    break
    for key, value in by_type.items():
        result.setdefault(key, value)
    result["extracted_ioc_count"] = len(iocs)
    return result


def normalize_text_value(key: str, value: str) -> str:
    if key in {"username", "user", "account", "targetusername", "user_name"}:
        return value.replace("\\\\", "\\")
    return value


def normalize_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", key.strip().lower()).strip("_")


def parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(UTC)


def _flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            child_prefix = f"{prefix}_{key}" if prefix else str(key)
            if isinstance(item, dict):
                out.update(_flatten(item, child_prefix))
            elif isinstance(item, list):
                out[normalize_key(child_prefix)] = item
            else:
                out[normalize_key(child_prefix)] = item
        return out
    return {"value": value}
