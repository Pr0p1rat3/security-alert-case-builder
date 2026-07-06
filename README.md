# Security Alert Case Builder

Security Alert Case Builder is an internal defensive application for turning raw security alerts into investigation-ready cases. Analysts can paste or upload alerts, extract IOCs, enrich indicators with safe local providers, build a timeline, map likely MITRE ATT&CK techniques, track response tasks, manage evidence, and generate ticket-ready reports.

The MVP intentionally avoids offensive automation. It does not exploit systems, harvest credentials, scan without authorization, or execute containment actions. Containment is represented as analyst tasks and report language.

## Architecture

- Backend: Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, JWT auth, local RBAC.
- Database: PostgreSQL in Docker Compose. SQLite is used by tests.
- Background jobs: Redis and an RQ worker are included; MVP enrichment runs synchronously through safe placeholder providers and can be moved onto the queue.
- Frontend: React, TypeScript, Vite, Tailwind CSS, nginx reverse proxy.
- Evidence: uploaded files are validated by extension, size-limited, SHA256-hashed, and stored outside the web root.

## Screenshots

- Dashboard with severity and status rollups.
<img width="2743" height="1947" alt="Screenshot 2026-07-06 at 11-52-37 " src="https://github.com/user-attachments/assets/a20fe0dc-534c-4565-8129-e3034087ef50" />
<img width="2743" height="1947" alt="Screenshot 2026-07-06 at 11-56-42 " src="https://github.com/user-attachments/assets/d13f1518-33e5-4279-b089-29c3e2c73b4d" />

- Case detail page with Overview, Raw Alerts, Timeline, IOCs, Evidence, MITRE Mapping, Tasks, Notes, Reports, and Audit Log tabs.
<img width="2743" height="1947" alt="Screenshot 2026-07-06 at 11-59-13 " src="https://github.com/user-attachments/assets/7c30fd56-b6cb-4357-9920-372ed99d5c33" />
<img width="2743" height="1947" alt="Screenshot 2026-07-06 at 11-58-49 " src="https://github.com/user-attachments/assets/5ad234f1-7059-4f26-bca1-0afc47999a48" />
<img width="2743" height="1947" alt="Screenshot 2026-07-06 at 11-58-40 " src="https://github.com/user-attachments/assets/b3aa7bcd-6211-447a-915e-e0a5dadc783f" />
<img width="2743" height="1947" alt="Screenshot 2026-07-06 at 11-58-31 " src="https://github.com/user-attachments/assets/82d0edda-c6f5-4466-89b9-da1b35f9e089" />

- Generated Markdown report view.

## Local Docker Setup

```bash
cd security-alert-case-builder
cp .env.example .env
docker compose up --build
```

Open the frontend at:

```text
http://localhost:8080
```

Seeded local credentials:

```text
admin@example.com
ChangeMe123!
```

Change these before any shared deployment.

## Backend Development

```bash
cd backend
python3.12 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Run tests:

```bash
pytest
```

## Frontend Development

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://localhost:8000`.

Run tests:

```bash
npm test
```

## Environment Variables

All backend app settings use the `SACB_` prefix. See `.env.example` for the full list.

Important settings:

- `SACB_DATABASE_URL`
- `SACB_REDIS_URL`
- `SACB_JWT_SECRET`
- `SACB_CORS_ORIGINS`
- `SACB_EVIDENCE_STORAGE_PATH`
- `SACB_MAX_UPLOAD_BYTES`
- `SACB_SEED_ADMIN_EMAIL`
- `SACB_SEED_ADMIN_PASSWORD`

No external enrichment API keys are required for the MVP.

## How To Use

1. Log in with the seeded admin account.
2. Create a case from the Cases page.
3. Open the case and paste a raw alert in the Raw Alerts tab, or upload `.json`, `.csv`, `.txt`, or `.log`.
4. Review extracted IOCs, timeline entries, and recommended investigation tasks.
5. Use the MITRE Mapping tab to suggest local ATT&CK mappings.
6. Upload supporting evidence in the Evidence tab.
7. Generate a Markdown or HTML report in the Reports tab.
8. Review the Audit Log tab for traceability.

Sample alerts are in `sample_data/`.

## Parsing

The parser supports generic JSON, CSV, key-value alert text, Windows event text, Sysmon-like text, WAF alerts, Proofpoint-style phishing alerts, Sophos endpoint alerts, and DNS/proxy/firewall logs. Missing fields do not fail parsing; raw content is preserved with parser confidence.

## IOC Enrichment

MVP enrichment uses local/mock providers:

- DNS lookup provider
- WHOIS/RDAP placeholder
- GeoIP placeholder
- reputation placeholder
- CISA KEV placeholder for CVEs
- internal allowlist/blocklist provider
- MITRE technique suggestion provider

Provider interfaces are isolated so real providers can be added later with environment-based API keys.

## MITRE Mapping

The local mapping engine suggests common ATT&CK techniques from alert terms. Suggestions are explicitly not treated as certainty. Analysts should confirm or reject mappings during investigation.

## Security Notes

- Passwords are hashed with bcrypt.
- JWTs expire by default.
- Role-based dependencies protect API routes.
- CORS is explicit and configurable.
- Evidence uploads are extension-validated, size-limited, hashed, and never executed.
- Audit logs are written for important state-changing actions.
- Secrets are redacted from audit details.
- Production mode returns generic errors rather than stack traces.
- Docker containers run as non-root where practical.

## Known MVP Limitations

- External provider integrations are placeholders.
- Redis/RQ is scaffolded through Compose but long-running jobs are not yet offloaded.
- OIDC/SAML/LDAP are roadmap items.
- Evidence storage is local filesystem by default; S3-compatible storage can be added behind the evidence service.
