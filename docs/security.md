# Security

This application is defensive-only.

It does not include exploitation logic, credential harvesting, brute force behavior, unauthorized scanning, stealth behavior, or automatic destructive response actions.

## Secure Defaults

- Passwords are hashed with bcrypt.
- JWT expiration is enabled.
- RBAC protects state-changing routes.
- Evidence files are stored outside the web root.
- Evidence uploads are validated by extension and size-limited.
- File SHA256 hashes are calculated on upload.
- Audit logs are created for important state-changing actions.
- Secrets are redacted from audit details.
- CORS origins are explicit.
- Production mode hides stack traces.
- Docker backend runs as a non-root user.

## Operational Notes

- Replace seeded admin credentials immediately.
- Set a strong `SACB_JWT_SECRET`.
- Restrict frontend/backend access to internal networks.
- Back up PostgreSQL and evidence storage together.
- Treat uploaded evidence as sensitive incident data.
- Do not connect external enrichment providers until legal, privacy, and data handling requirements are approved.
