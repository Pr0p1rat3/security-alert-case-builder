from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from app.models.enums import IocType


@dataclass(frozen=True)
class ExtractedIOC:
    type: IocType
    value: str
    raw_value: str


IPV4_RE = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")
IPV6_RE = re.compile(r"\b(?:[a-fA-F0-9]{1,4}:){2,7}[a-fA-F0-9]{1,4}\b")
URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
DOMAIN_RE = re.compile(r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b")
MD5_RE = re.compile(r"\b[a-fA-F0-9]{32}\b")
SHA1_RE = re.compile(r"\b[a-fA-F0-9]{40}\b")
SHA256_RE = re.compile(r"\b[a-fA-F0-9]{64}\b")
WIN_PATH_RE = re.compile(r"\b[A-Za-z]:\\(?:[^<>:\"|?*\r\n]+\\?)+")
LINUX_PATH_RE = re.compile(r"(?<!\w)/(?:[A-Za-z0-9._-]+/)*[A-Za-z0-9._-]+")
REGISTRY_RE = re.compile(
    r"\b(?:HKLM|HKCU|HKCR|HKU|HKEY_LOCAL_MACHINE|HKEY_CURRENT_USER)\\[^\r\n]+", re.IGNORECASE
)
CVE_RE = re.compile(r"\bCVE-\d{4}-\d{4,}\b", re.IGNORECASE)


def extract_iocs(text: str) -> list[ExtractedIOC]:
    seen: set[tuple[IocType, str]] = set()
    results: list[ExtractedIOC] = []

    def add(ioc_type: IocType, raw: str) -> None:
        value = normalize_ioc(ioc_type, raw)
        key = (ioc_type, value)
        if key not in seen:
            seen.add(key)
            results.append(ExtractedIOC(ioc_type, value, raw))

    for raw in URL_RE.findall(text):
        add(IocType.url, raw)
    for raw in EMAIL_RE.findall(text):
        add(IocType.email, raw)
    for raw in SHA256_RE.findall(text):
        add(IocType.sha256, raw)
    for raw in SHA1_RE.findall(text):
        add(IocType.sha1, raw)
    for raw in MD5_RE.findall(text):
        add(IocType.md5, raw)
    for raw in IPV4_RE.findall(text):
        add(IocType.ipv4, raw)
    for raw in IPV6_RE.findall(text):
        add(IocType.ipv6, raw)
    for raw in REGISTRY_RE.findall(text):
        add(IocType.registry_path, raw)
    for raw in WIN_PATH_RE.findall(text):
        add(IocType.windows_path, raw)
    for raw in LINUX_PATH_RE.findall(text):
        add(IocType.linux_path, raw)
    for raw in CVE_RE.findall(text):
        add(IocType.cve, raw)
    for raw in DOMAIN_RE.findall(text):
        if "@" not in raw and not raw.lower().startswith(("http.", "https.")):
            add(IocType.domain, raw)

    return results


def normalize_ioc(ioc_type: IocType, raw: str) -> str:
    value = raw.strip().strip(".,;)]}'\"")
    if ioc_type in {IocType.domain, IocType.email}:
        return value.lower()
    if ioc_type == IocType.url:
        parts = urlsplit(value)
        return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path, parts.query, ""))
    if ioc_type in {IocType.md5, IocType.sha1, IocType.sha256, IocType.cve}:
        return value.upper() if ioc_type == IocType.cve else value.lower()
    return value
