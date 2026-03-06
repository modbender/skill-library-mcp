---
name: massive-com
description: Bash CLI wrapper and OpenClaw skill for Massive's public REST API. Use when Codex or an OpenClaw agent needs to query Massive market-data endpoints from a shell workflow, align authentication to OpenClaw-style secret references, keep logs free of secrets, or integrate Massive responses into agent pipelines and other CLI tools.
---

# Massive CLI for OpenClaw

Use the bundled CLI before writing ad hoc `curl` commands. Keep requests deterministic, resolve credentials through OpenClaw-compatible secret references when available, and prefer narrow queries over broad scans.

## Quick Start

- Read [references/openclaw-secrets.md](references/openclaw-secrets.md) before configuring credentials.
- Read [references/massive-api.md](references/massive-api.md) when choosing endpoints or query shapes.
- Read [references/security.md](references/security.md) before changing logging, auth, or error handling.
- Run `scripts/massive health` to validate local prerequisites and auth configuration.
- Run `scripts/massive get /v3/reference/tickers/AAPL` for a generic REST request.
- If you package or publish this skill, include every path listed in `BUNDLE_MANIFEST.md`.

## Workflow

1. Resolve credentials through `MASSIVE_API_KEY_REF` when possible.
2. Fall back to `MASSIVE_API_KEY` only when a secret ref is not available.
3. Use a domain shortcut when it matches a documented Massive endpoint.
4. Use `get` for any other documented REST path.
5. Pipe JSON into downstream tools instead of enabling verbose logging.

## Commands

- `scripts/massive health`
- `scripts/massive get <path-or-next-url> [--query key=value ...]`
- `scripts/massive next` to read `next_url` from stdin JSON and fetch the next page
- `scripts/massive stocks ticker-details <ticker>`
- `scripts/massive stocks previous-close <ticker>`
- `scripts/massive options contract-details <options-ticker>`
- `scripts/massive forex currencies`
- `scripts/massive crypto currencies`
- `scripts/massive indices ticker-details <ticker>`

## Agent Rules

- Keep output in JSON unless a human-readable mode is explicitly needed.
- Send diagnostics to `stderr`; treat `stdout` as data.
- Never print resolved secrets, auth headers, or raw secret-ref payloads.
- Avoid `--verbose` in shared logs.
- Feed `next_url` back into `get` or `next` instead of reconstructing pagination manually.
- Treat non-`api.massive.com` absolute URLs as invalid unless `MASSIVE_BASE_URL` was explicitly changed to another HTTPS origin.

## Resources

- `scripts/massive`: main Bash CLI
- `BUNDLE_MANIFEST.md`: required file list for packaged artifacts
- `references/openclaw-secrets.md`: credential and secret-ref contract used by this skill
- `references/massive-api.md`: endpoint selection and request patterns
- `references/security.md`: redaction and operational safety constraints
