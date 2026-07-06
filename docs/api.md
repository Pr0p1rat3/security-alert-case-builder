# API

The backend exposes REST JSON. Authentication uses bearer JWTs.

## Auth

- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`

## Users

- `GET /users`
- `POST /users`
- `PATCH /users/{id}`

## Cases

- `GET /cases`
- `POST /cases`
- `GET /cases/{id}`
- `PATCH /cases/{id}`
- `DELETE /cases/{id}`

## Alerts

- `POST /cases/{id}/alerts/paste`
- `POST /cases/{id}/alerts/upload`
- `GET /cases/{id}/alerts`
- `GET /alerts/{id}`

## IOCs and Enrichment

- `GET /cases/{id}/iocs`
- `POST /cases/{id}/iocs/extract`
- `POST /iocs/{id}/enrich`
- `POST /cases/{id}/iocs/enrich-all`

## Timeline

- `GET /cases/{id}/timeline`
- `POST /cases/{id}/timeline`
- `PATCH /timeline/{id}`
- `DELETE /timeline/{id}`
- `GET /cases/{id}/timeline/export.md`

## MITRE

- `GET /cases/{id}/mitre`
- `POST /cases/{id}/mitre/suggest`
- `PATCH /case-techniques/{id}`

## Tasks, Evidence, Reports, Audit

- `GET /cases/{id}/tasks`
- `POST /cases/{id}/tasks`
- `PATCH /tasks/{id}`
- `GET /cases/{id}/notes`
- `POST /cases/{id}/notes`
- `POST /cases/{id}/evidence`
- `GET /cases/{id}/evidence`
- `GET /evidence/{id}/download`
- `DELETE /evidence/{id}`
- `POST /cases/{id}/reports/generate`
- `GET /cases/{id}/reports`
- `GET /reports/{id}`
- `GET /cases/{id}/audit`
- `GET /audit`

## Dashboard and Search

- `GET /dashboard/summary`
- `GET /search?q=...`

OpenAPI is available at `/openapi.json` and Swagger UI at `/docs` in FastAPI.
