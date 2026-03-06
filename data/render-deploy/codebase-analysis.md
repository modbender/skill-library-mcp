# Codebase Analysis - Render Deploy

Use this file to detect runtime, build/start commands, and infra requirements before choosing a deploy method.

## Stack Detection Checklist

### Node.js
- Inspect `package.json` scripts and engines.
- Detect package manager by lock file.
- Confirm start command binds to `$PORT`.

Default command mapping:
- `pnpm-lock.yaml` -> `pnpm install --frozen-lockfile` + `pnpm start`
- `yarn.lock` -> `yarn install --frozen-lockfile` + `yarn start`
- `package-lock.json` -> `npm ci` + `npm start`

### Python
- Detect package manager from `uv.lock`, `poetry.lock`, `Pipfile.lock`, or `requirements.txt`.
- Identify framework (Django, Flask, FastAPI).
- Verify runtime pin from `runtime.txt`, `.python-version`, or `pyproject.toml`.

Default command mapping:
- `requirements.txt` -> `pip install -r requirements.txt` + `gunicorn app:app --bind 0.0.0.0:$PORT`
- FastAPI -> `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Go
- Read `go.mod` for version and dependencies.
- Build with `go build -o bin/app .` unless repo structure requires a specific entrypoint.

### Static Site
- Detect output folder (`dist`, `build`, `out`, `public`).
- Prefer static runtime if no server-side rendering is required.

## Data and Infra Detection

Collect this before method selection:
- Required environment variables
- Database or key-value needs
- Need for worker/cron/private service
- Health endpoint availability

If the app needs web + worker + datastore, default to Blueprint.
