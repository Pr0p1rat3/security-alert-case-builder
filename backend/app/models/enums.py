from __future__ import annotations

from enum import StrEnum


class UserRole(StrEnum):
    admin = "Admin"
    analyst = "Analyst"
    viewer = "Viewer"


class Severity(StrEnum):
    informational = "Informational"
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"


class CaseStatus(StrEnum):
    new = "New"
    triage = "Triage"
    investigating = "Investigating"
    containment = "Containment"
    eradication = "Eradication"
    recovery = "Recovery"
    closed = "Closed"
    false_positive = "False Positive"


class IocType(StrEnum):
    ipv4 = "ipv4"
    ipv6 = "ipv6"
    domain = "domain"
    url = "url"
    email = "email"
    md5 = "md5"
    sha1 = "sha1"
    sha256 = "sha256"
    windows_path = "windows_path"
    linux_path = "linux_path"
    registry_path = "registry_path"
    cve = "cve"


class Verdict(StrEnum):
    unknown = "Unknown"
    benign = "Benign"
    suspicious = "Suspicious"
    malicious = "Malicious"


class TaskStatus(StrEnum):
    open = "Open"
    in_progress = "In Progress"
    blocked = "Blocked"
    done = "Done"
    not_applicable = "Not Applicable"


class MappingStatus(StrEnum):
    suggested = "Suggested"
    confirmed = "Confirmed"
    rejected = "Rejected"
