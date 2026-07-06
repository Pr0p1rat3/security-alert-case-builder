# Architecture

Security Alert Case Builder uses a split frontend/backend architecture.

## Backend

FastAPI exposes REST JSON endpoints for auth, cases, alerts, IOCs, enrichment, timeline events, MITRE mappings, tasks, evidence, reports, audit logs, dashboard summaries, and search.

SQLAlchemy models are the source of truth. Alembic is configured, and the MVP migration creates metadata-defined tables. PostgreSQL is used in Docker and production-like deployments. Tests use SQLite.

Redis and an RQ worker service are included. The MVP runs safe enrichment synchronously because providers are local or placeholders, but the queue module is in place for long-running enrichment, report, or export jobs.

## Frontend

React + TypeScript + Vite provides a dense analyst UI. nginx serves static assets and proxies `/api/*` to the backend.

The UI is intentionally workflow-oriented:

- Dashboard
- Cases list
- Case detail tabs
- Search
- Admin users

## Data Flow

1. Analyst creates a case.
2. Analyst pastes or uploads raw alert data.
3. Backend parses fields and stores raw alert content.
4. IOC extraction normalizes indicators and links them to the alert and case.
5. Timeline generation creates an initial event.
6. Task recommendation adds analyst checklist items.
7. MITRE suggestions and enrichment can be run from the UI.
8. Reports render Markdown or HTML from stored case data.
