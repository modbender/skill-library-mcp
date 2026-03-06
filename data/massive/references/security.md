# Security Requirements

This skill is public and intended for redistribution. Do not add personal data, local artifacts, captured credentials, or private response payloads.

## Runtime Safety

- Use `set -euo pipefail`.
- Refuse to run with shell xtrace enabled.
- Quote every expansion.
- Allow requests only to `https://api.massive.com` by default. If `MASSIVE_BASE_URL` is explicitly set, allow only that HTTPS origin instead.
- Send auth in headers only.
- Keep structured data on `stdout` and diagnostics on `stderr`.

## Logging and Redaction

- Redact API keys in URLs, headers, and stderr diagnostics.
- Never print the `Authorization` header or `apiKey` query value.
- Never persist response payloads to temp files unless the caller explicitly redirects output.
- Keep verbose mode request-safe: method, path, query keys, status, latency, request id.

## Review Checks

- Run `shellcheck` on every shell script.
- Run `shfmt -d` to enforce formatting.
- Maintain smoke tests that mock `curl` and verify redaction.
- Prefer additive changes to endpoint shortcuts; do not silently change command semantics.
