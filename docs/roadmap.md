# Roadmap

## Near Term

- Move enrichment and report generation to RQ workers.
- Add durable job status endpoints.
- Add richer audit filters and export.
- Add report template editing.
- Add S3-compatible evidence storage.
- Add database encryption guidance for self-hosted deployments.

## Integrations

- Sophos Central API
- Proofpoint TAP/SIEM API
- Microsoft Defender Advanced Hunting API
- Alert Logic API/export parser
- Fortra WAF log export parser
- Cisco Secure Access logs
- AbuseIPDB
- VirusTotal
- GreyNoise
- Shodan
- CISA KEV
- MISP
- Jira and ServiceNow ticket creation
- Slack and Teams notification
- OIDC, SAML, and LDAP authentication

## Hardening

- Add per-user API tokens for automation.
- Add stricter Content Security Policy once frontend asset needs are final.
- Add optional object lock/immutability for evidence.
- Add field-level redaction policies for reports.
