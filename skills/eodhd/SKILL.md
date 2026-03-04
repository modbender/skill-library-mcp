---
name: eodhd
description: Plan, build, review, or extend a stateless Bash CLI wrapper for the publicly documented EODHD API, intended for OpenClaw agents and Clawhub.ai distribution. Use when Codex needs to define command structure, auth handling, error semantics, redaction rules, CI, packaging, or skill metadata for an open source EODHD integration that must follow OpenClaw secrets management and avoid leaking sensitive data to stdout, stderr, logs, examples, or repo artifacts.
---

# EODHD

## Overview

Build the wrapper as a small, stateless Bash CLI that translates stable subcommands into EODHD HTTPS requests and emits machine-friendly output. Keep secrets outside the repo and outside the CLI's own persistence model by aligning auth to OpenClaw-managed environment injection.

## Workflow

1. Confirm the task shape.
   - If the user is asking for a plan, load [references/implementation-plan.md](references/implementation-plan.md).
   - If the user is asking how to wire credentials safely, load [references/openclaw-secrets.md](references/openclaw-secrets.md).
   - If the user is asking for actual code changes, implement the narrowest useful slice first and preserve stateless behavior.

2. Hold the contract steady.
   - Prefer `eodhd` as the binary name.
   - Default to JSON on stdout and diagnostics on stderr.
   - Exit non-zero on HTTP, auth, or argument errors.
   - Do not create config files, caches, token stores, or hidden state.

3. Keep auth OpenClaw-native.
   - Expect `EODHD_API_KEY` to be injected by OpenClaw.
   - Allow a one-shot explicit override like `--api-key` only if the user asks for it or the implementation already exposes it.
   - Do not read plaintext secrets from repo files, sample configs, shell history helpers, or generated artifacts.
   - Keep the publish metadata aligned with that contract by declaring `EODHD_API_KEY` as the primary required credential.

4. Enforce redaction and logging hygiene.
   - Never print the raw API key to stdout or stderr.
   - Redact secrets in debug output, dry-run output, request traces, and test snapshots.
   - Avoid `set -x` unless xtrace output is redirected through a sanitizer.
   - Treat query strings, headers, and copied curl commands as sensitive if they can contain `api_token`.

5. Prefer a narrow, agent-friendly surface.
   - Start with stable commands such as `eod`, `fundamentals`, `real-time`, `search`, `exchanges`, and `raw`.
   - Add generic `--query key=value` support before adding many bespoke flags.
   - Use a `raw` escape hatch for unsupported endpoints instead of blocking new EODHD API coverage.

6. Preserve public-distribution constraints.
   - Assume the repo is public.
   - Use only public EODHD docs and public sample symbols in examples.
   - Avoid local-machine assumptions, personal data, or environment-specific artifacts.
   - Verify the release bundle contains `scripts/eodhd` and the metadata that declares it.

## Implementation Rules

- Keep the CLI dependency-light: Bash plus `curl` as the baseline.
- Use deterministic argument parsing and stable exit codes.
- Separate URL construction, request execution, error translation, and output handling into small shell functions.
- Make debug behavior opt-in with `--verbose` or `--dry-run`.
- If tests are added, prefer smoke tests around URL generation, argument validation, and redaction.

## Deliverables

- `scripts/eodhd` for the CLI entrypoint when implementation starts
- `scripts/check-package.sh` for package and manifest consistency checks
- `references/implementation-plan.md` for milestones and acceptance criteria
- `references/openclaw-secrets.md` for secret and logging constraints
- `agents/openai.yaml` for Clawhub/OpenAI-facing metadata

## Validation

- Check that examples never expose a real token.
- Check that debug or dry-run output replaces token values with a fixed mask such as `***REDACTED***`.
- Check that auth failure, HTTP failure, and usage failure produce distinct exit codes or clearly distinct stderr messages.
- Check that the manifest declares `EODHD_API_KEY` and includes `scripts/eodhd` in the packaged files.
- Check that the repo contains no `.env`, token snapshots, or generated local artifacts.
