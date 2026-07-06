from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TechniqueSeed:
    technique_id: str
    technique_name: str
    tactic: str
    keywords: tuple[str, ...]
    why: str


TECHNIQUES: tuple[TechniqueSeed, ...] = (
    TechniqueSeed(
        "T1059.001",
        "PowerShell",
        "Execution",
        ("powershell", "pwsh", "-enc", "encodedcommand"),
        "PowerShell indicators were observed.",
    ),
    TechniqueSeed(
        "T1569.002",
        "Service Execution",
        "Execution",
        ("psexec", "service creation", "7045", "new service"),
        "Service execution or creation indicators were observed.",
    ),
    TechniqueSeed(
        "T1021.002",
        "SMB/Windows Admin Shares",
        "Lateral Movement",
        ("admin$", "c$", "ipc$", "admin share"),
        "Admin share access indicators were observed.",
    ),
    TechniqueSeed(
        "T1003",
        "OS Credential Dumping",
        "Credential Access",
        ("lsass", "procdump", "mimikatz", "credential dump"),
        "Credential dumping terms were present. Treat as a suggested mapping only.",
    ),
    TechniqueSeed(
        "T1053.005",
        "Scheduled Task",
        "Persistence",
        ("scheduled task", "schtasks", "task scheduler"),
        "Scheduled task indicators were observed.",
    ),
    TechniqueSeed(
        "T1547.001",
        "Registry Run Keys / Startup Folder",
        "Persistence",
        ("run key", "runonce", "registry persistence"),
        "Registry startup persistence terms were observed.",
    ),
    TechniqueSeed(
        "T1566",
        "Phishing",
        "Initial Access",
        ("phish", "proofpoint", "malicious email"),
        "Email security alert resembles phishing activity.",
    ),
    TechniqueSeed(
        "T1204",
        "User Execution",
        "Execution",
        ("url clicked", "clicked", "attachment opened"),
        "User interaction may have executed or opened malicious content.",
    ),
    TechniqueSeed(
        "T1190",
        "Exploit Public-Facing Application",
        "Initial Access",
        ("waf", "sql injection", "xss", "path traversal"),
        "WAF alert suggests public application exploitation attempt.",
    ),
    TechniqueSeed(
        "T1071",
        "Application Layer Protocol",
        "Command and Control",
        ("beacon", "dns query", "proxy", "suspicious domain"),
        "Outbound network activity may involve application-layer C2 patterns.",
    ),
)


def suggest_techniques(text: str) -> list[dict[str, object]]:
    lower = text.lower()
    suggestions: list[dict[str, object]] = []
    for technique in TECHNIQUES:
        hits = [keyword for keyword in technique.keywords if keyword in lower]
        if not hits:
            continue
        confidence = min(0.95, 0.45 + len(hits) * 0.15)
        suggestions.append(
            {
                "technique_id": technique.technique_id,
                "technique_name": technique.technique_name,
                "tactic": technique.tactic,
                "why_suggested": f"{technique.why} Matched: {', '.join(hits)}.",
                "confidence": confidence,
            }
        )
    return suggestions
