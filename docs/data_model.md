# Data Model

Core tables:

- `users`: local auth identity, bcrypt password hash, role, active flag.
- `cases`: investigation container with severity, status, source, affected entities, and business fields.
- `alerts`: raw alert content, parser output, source system, parser confidence.
- `iocs`: normalized indicators linked to cases and source alerts.
- `ioc_enrichments`: provider verdicts, confidence, summary, raw JSON, timestamp.
- `timeline_events`: ordered investigation timeline items.
- `evidence_files`: uploaded evidence metadata, storage path, SHA256, size, uploader.
- `mitre_techniques`: local seed ATT&CK techniques.
- `case_technique_mappings`: suggested or analyst-confirmed technique mappings.
- `tasks`: investigation and response checklist items.
- `notes`: analyst notes.
- `reports`: generated Markdown or HTML report content.
- `audit_logs`: actor, case, action, entity, details, timestamp.
- `source_systems`, `tags`, `case_tags`, `allowlist_entries`, `blocklist_entries`: supporting taxonomy and policy data.

Raw evidence is retained by reference, not embedded in reports. Reports include evidence filenames and hashes for traceability.
