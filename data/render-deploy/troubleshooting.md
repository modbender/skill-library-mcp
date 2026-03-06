# Troubleshooting - Render Deploy

Use this when build, startup, or health checks fail. Fix one issue at a time.

## Failure Classes

1. Build failure
- Wrong build command
- Missing dependencies
- Missing build-time env vars

2. Startup failure
- Wrong start command
- App not binding to `0.0.0.0:$PORT`
- Missing runtime secrets

3. Health/runtime failure
- No healthy endpoint response
- Runtime exceptions after startup
- Downstream dependency failure

## Quick Signature Map

| Signature | Likely cause | First fix |
|----------|--------------|-----------|
| `Cannot find module` | Missing dependency | Add dependency and rebuild |
| `ModuleNotFoundError` | Missing Python package | Update requirements and rebuild |
| `EADDRINUSE` or bind error | Wrong port strategy | Bind to `0.0.0.0:$PORT` |
| `connection refused` | DB unavailable or bad URL | Verify DB state and connection string |
| health check timeout | App not healthy on expected path | Add/verify health endpoint |

## Minimal Triage Loop

1. Confirm latest deploy status.
2. Read top runtime errors.
3. Apply smallest safe fix.
4. Redeploy and re-check health.

Avoid repeated redeploys without an actual fix.
