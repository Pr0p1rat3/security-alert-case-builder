from __future__ import annotations

TASK_SETS: dict[str, list[tuple[str, str, str]]] = {
    "endpoint": [
        (
            "Confirm hostname and logged-in user",
            "Validate the affected host and primary user.",
            "High",
        ),
        ("Check process tree", "Review parent and child processes around the alert time.", "High"),
        (
            "Review network connections",
            "Identify suspicious destinations and outbound sessions.",
            "Medium",
        ),
        (
            "Check persistence locations",
            "Review startup items, services, scheduled tasks, and run keys.",
            "Medium",
        ),
        (
            "Determine if isolation is required",
            "Decide whether containment is needed; do not auto-isolate from this tool.",
            "High",
        ),
    ],
    "phishing": [
        (
            "Review message headers",
            "Check sender, return path, authentication results, and hops.",
            "High",
        ),
        ("Identify recipients", "Determine all users who received the message.", "High"),
        ("Confirm clicks", "Search proxy, DNS, and mail telemetry for clicks.", "High"),
        (
            "Search for similar messages",
            "Find related campaigns by sender, subject, URL, and hashes.",
            "Medium",
        ),
        (
            "Plan blocks if malicious",
            "Prepare sender/domain/URL blocks if validated malicious.",
            "Medium",
        ),
    ],
    "waf": [
        (
            "Validate source IP and X-Forwarded-For",
            "Review client IP chain and source reputation.",
            "High",
        ),
        ("Review triggered signature", "Understand the WAF rule and request context.", "High"),
        (
            "Identify URL and parameter",
            "Find target endpoint and vulnerable parameter if present.",
            "Medium",
        ),
        ("Check repeat activity", "Search for repeated attempts and related sources.", "Medium"),
        (
            "Assess tuning risk",
            "Only recommend scoped exception if false positive is confirmed.",
            "Medium",
        ),
    ],
    "ad": [
        (
            "Review Windows event chain",
            "Check 4624, 4648, 4672, 4688, and 7045 around the alert.",
            "High",
        ),
        (
            "Validate privileged account use",
            "Confirm whether account activity was authorized.",
            "High",
        ),
        (
            "Review source and destination hosts",
            "Check both endpoints for related activity.",
            "High",
        ),
        ("Check service creation", "Validate new service creation events and binaries.", "Medium"),
        (
            "Search for PowerShell remoting",
            "Look for WinRM and PowerShell operational events.",
            "Medium",
        ),
    ],
}


def recommend_tasks(alert_type: str, text: str) -> list[tuple[str, str, str]]:
    lower = f"{alert_type} {text}".lower()
    if any(marker in lower for marker in ["proofpoint", "phish", "email"]):
        return TASK_SETS["phishing"]
    if any(marker in lower for marker in ["waf", "sql injection", "xss"]):
        return TASK_SETS["waf"]
    if any(marker in lower for marker in ["4624", "4672", "psexec", "admin share", "7045"]):
        return TASK_SETS["ad"]
    return TASK_SETS["endpoint"]
