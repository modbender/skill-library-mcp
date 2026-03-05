# OpenClaw Secrets and Logging Notes

## Purpose

Use this reference when wiring the EODHD wrapper to OpenClaw-managed secrets and when reviewing whether logs, examples, or diagnostics can leak sensitive data.

## OpenClaw alignment

OpenClaw secret management is additive and supports references from:

- `env`
- `file`
- `exec`

For this wrapper, prefer injecting the EODHD credential into `EODHD_API_KEY` at activation time and let the Bash CLI consume only that environment variable. Keep the CLI itself unaware of OpenClaw config file internals unless a future platform requirement explicitly needs that coupling.

## Recommended credential contract

- Canonical env var: `EODHD_API_KEY`
- Optional one-shot override: `--api-key`
- Underlying EODHD query parameter: `api_token`

This keeps the user-facing runtime contract stable while isolating the EODHD-specific token name to request construction.

## Safe examples

Use placeholder values in documentation:

```bash
EODHD_API_KEY=***REDACTED*** eodhd eod AAPL.US
```

If an example needs to show request shape, prefer a masked dry run:

```text
GET /api/eod/AAPL.US?api_token=***REDACTED***&fmt=json
```

## Redaction rules

Apply redaction to:

- stdout in `--dry-run`
- stderr in verbose and error output
- copied curl commands
- test snapshots and fixture generation
- issue templates or support snippets if the repo later adds them

Minimum rule set:

- Replace the exact token value if known.
- Replace `api_token=` values in URLs.
- Replace `Authorization:` header values if headers are introduced later.

## Unsafe patterns

- `set -x` on live requests without a sanitizer
- printing full env vars during debug
- embedding tokens in committed examples
- writing request URLs with raw query strings into CI logs
- storing token-bearing responses in fixtures
