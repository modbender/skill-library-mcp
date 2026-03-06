# Runtime requirements

Use this checklist before running the interceptor in any environment.

## 1) Dependencies

- `@valiron/sdk`
- Payment rail library used by the host app (x402 package or equivalent)
- Logging/metrics package used for audit events

## 2) Credentials and config

Provide secrets through a secret manager or environment variables (never hardcode).

Default (current SDK behavior):

- No API key is required by default for basic trust lookups.

Optional / deployment-specific:

- `VALIRON_API_KEY` (use when your Valiron endpoint enables auth)
- `VALIRON_BASE_URL` (for non-default/self-hosted endpoint)
- `VALIRON_TIMEOUT_MS` (e.g., `5000`)
- `VALIRON_RETRY_MAX` (small bounded retry count)

Policy inputs:

- Route decision policy (JSON)
- Spend controls (global + per-route caps)
- Fallback mode per endpoint class (`fail-closed` for high risk)

## 3) Startup validation

Validate policy/config on startup:

- If your environment requires auth and credential is missing, do not start payment authorization path.
- If policy file is missing/invalid, default to deny.
- If fallback mode is undefined for an endpoint class, default to fail-closed.

## 4) Security hygiene

- Do not log API keys or raw auth headers.
- Redact sensitive fields in audit logs.
- Rotate keys regularly and document rotation owner/runbook.
