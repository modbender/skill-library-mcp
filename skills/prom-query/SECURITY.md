# Security Policy — prom-query

## Design Principles

1. **Read-only by design.** This skill only makes read-only API queries to the Prometheus HTTP API (query/read endpoints). It cannot modify metrics, rules, alerts, or any server configuration.

2. **No credential leakage.** The `PROMETHEUS_TOKEN` is passed only via HTTP `Authorization` header. It is never:
   - Printed to stdout or stderr
   - Included in JSON output
   - Logged to any file
   - Passed as a URL query parameter

3. **Input validation.**
   - `PROMETHEUS_URL` is validated to use only `http://` or `https://` schemes
   - PromQL queries are passed via `--data-urlencode` to curl (proper URL encoding)
   - All JSON construction uses `jq --arg` — no string interpolation or template injection

4. **No code injection surface.**
   - No `eval`, no `$(...)` on user-supplied data in unsafe contexts
   - No Python `f'''${VAR}'''` patterns
   - Shell variables are quoted throughout
   - `set -euo pipefail` enforced

## What This Skill Can Access

- **Metrics data** (timeseries values, metadata, label values)
- **Alert state** (firing, pending, inactive alerts)
- **Target health** (scrape target status and errors)
- **Rule definitions** (alerting and recording rules)

## What This Skill Cannot Access

- Prometheus configuration files
- Prometheus admin API endpoints (`/api/v1/admin/*`)
- Write API endpoints (remote write)
- Any non-Prometheus services

## Authentication

| Method | Supported | How |
|--------|-----------|-----|
| Bearer token | ✅ | `PROMETHEUS_TOKEN` env var |
| No auth | ✅ | Leave `PROMETHEUS_TOKEN` unset |
| Basic auth | ❌ | Not supported (use a reverse proxy) |
| mTLS | ❌ | Not supported (use a sidecar proxy) |
| OAuth2 | ❌ | Not supported (use an auth proxy) |

For unsupported auth methods, place an authenticating reverse proxy (e.g., oauth2-proxy, nginx) in front of Prometheus and point `PROMETHEUS_URL` at it.

## Network Security

- The skill connects only to the URL specified in `PROMETHEUS_URL`
- No DNS rebinding protection beyond what curl provides
- No TLS certificate pinning (standard CA validation)
- Connection timeout: 10 seconds
- Request timeout: 30 seconds

## Reporting Vulnerabilities

If you discover a security issue, please email security@cacheforge.dev with details. We will respond within 48 hours.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | ✅ |

Powered by Anvil AI 📊
