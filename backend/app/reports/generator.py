from __future__ import annotations

from html import escape

from app.models import Case


def generate_markdown(case: Case, report_type: str = "analyst") -> str:
    if report_type == "ticket":
        return ticket_summary(case)
    if report_type == "director":
        return director_summary(case)
    if report_type == "false_positive":
        return false_positive_report(case)
    return analyst_report(case)


def generate_html(markdown: str) -> str:
    paragraphs = "\n".join(
        f"<p>{escape(line)}</p>" if line else "" for line in markdown.splitlines()
    )
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>Case Report</title></head><body>{paragraphs}</body></html>"
    )


def analyst_report(case: Case) -> str:
    return "\n".join(
        [
            f"# Analyst Report: CASE-{case.id} {case.title}",
            "",
            f"Severity: {case.severity.value}",
            f"Status: {case.status.value}",
            f"Source: {case.source_system or 'Not specified'}",
            "",
            "## Overview",
            case.description or "No description provided.",
            "",
            "## Severity Rationale",
            case.business_impact or "Severity should be validated by the analyst.",
            "",
            "## Extracted IOCs",
            *[f"- {ioc.type.value}: {ioc.value}" for ioc in case.iocs],
            "",
            "## Timeline",
            *[
                f"- {event.timestamp.isoformat()} [{event.event_type}] {event.short_title}"
                for event in case.timeline_events
            ],
            "",
            "## MITRE Mappings",
            *[
                (
                    f"- {mapping.technique.technique_id} "
                    f"{mapping.technique.technique_name}: {mapping.why_suggested}"
                )
                for mapping in case.technique_mappings
            ],
            "",
            "## Recommended Next Steps",
            *[f"- [{task.status.value}] {task.title}: {task.description}" for task in case.tasks],
        ]
    )


def ticket_summary(case: Case) -> str:
    return f"""# Incident Ticket Summary: CASE-{case.id}

## Short Summary
{case.title}

## What Happened
{case.description}

## Affected Users/Assets
Users: {case.affected_users or "TBD"}
Hosts: {case.affected_hosts or "TBD"}
IPs: {case.affected_ips or "TBD"}

## Current Status
{case.status.value}

## Next Steps
{chr(10).join(f"- {task.title}" for task in case.tasks)}

## Closure Criteria
Evidence reviewed, scope validated, remediation tasks completed, and business owner notified.
"""


def director_summary(case: Case) -> str:
    return f"""# Director Summary: CASE-{case.id}

## What Happened
{case.title}

## Business Impact
{case.business_impact or "Impact is still being assessed."}

## Current Risk
Current risk is rated {case.severity.value}.

## Actions Completed
{len([task for task in case.tasks if task.status.value == "Done"])} tasks completed.

## Remaining Actions
{len([task for task in case.tasks if task.status.value != "Done"])} tasks remain open.

## Final Outcome
{case.close_reason or "Case is not closed."}
"""


def false_positive_report(case: Case) -> str:
    signature = next(
        (alert.parsed.get("signature") for alert in case.alerts if alert.parsed.get("signature")),
        "Not identified",
    )
    return f"""# False Positive Review: CASE-{case.id}

Alert source: {case.source_system or "Not specified"}
Triggered rule/signature: {signature}

## Why It Is Likely False Positive
Document analyst rationale here.

## Evidence Reviewed
{chr(10).join(f"- {evidence.file_name} ({evidence.sha256})" for evidence in case.evidence)}

## Suggested Tuning
Use scoped tuning only. Avoid disabling broad rule categories.

## Risk Of Tuning
Broad tuning can hide related true positives.

## Rollback Plan
Remove tuning and re-enable the original detection rule.
"""
