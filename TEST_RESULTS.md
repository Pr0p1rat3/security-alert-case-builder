# Test Results

Validation performed on 2026-07-06.

## Environment

- Backend runtime used for validation: Python 3.13.5
- Frontend runtime used for validation: Node.js v22.16.0, npm 10.9.2
- Docker Compose was not executed in this sandbox because Docker is not installed here.

## Commands Run

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
ruff check app
pytest -q
```

Result:

```text
All checks passed!
6 passed, 3 warnings
```

Warnings observed:

- FastAPI `on_event` deprecation warning. Functional but should eventually migrate to lifespan handlers.
- Starlette/FastAPI TestClient deprecation warning related to `httpx`/`httpx2`.

```bash
cd frontend
npm install --no-audit --no-fund
npm run lint
npm test
npm run build
```

Result:

```text
eslint: passed
vitest: 3 passed
vite build: passed
```

## Fixes Applied During Validation

1. Pinned `bcrypt` below 5.x to keep `passlib[bcrypt]` compatible.
2. Normalized escaped Windows domain usernames in pasted text alerts.
3. Updated `eslint-plugin-react-hooks` to a version compatible with ESLint 9.
4. Added Vite client type declarations for `import.meta.env`.
5. Excluded generated frontend build output from ESLint.
6. Updated Vitest script to use the forks pool, avoiding a test runner hang observed with this Node.js environment.
7. Ran Black and Ruff on backend app code.
8. Fixed frontend hook dependency lint issue in `CaseDetailPage`.
