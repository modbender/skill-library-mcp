---
name: iex-cloud
description: Use this skill when a task needs IEX Cloud market data through the REST API (quotes, charts, fundamentals, market lists, and batch calls), including secure token handling and scriptable CLI usage.
homepage: https://github.com/oscraters/iex-cloud-skill
metadata: {"openclaw":{"skillKey":"iex-cloud","homepage":"https://github.com/oscraters/iex-cloud-skill","sourceRepository":"https://github.com/oscraters/iex-cloud-skill.git","requires":{"env":["IEX_TOKEN"],"optionalEnv":["IEX_CLOUD_TOKEN","IEX_BASE_URL"],"primaryEnv":["IEX_TOKEN"],"bins":["curl"],"optionalBins":["jq"]}}}
---

# IEX Cloud

## Overview

This skill provides an operational workflow for IEX Cloud API usage in OpenClaw tasks:
- selecting the right endpoint for market-data requests
- building valid authenticated requests
- handling API and transport errors
- running repeatable calls through a local Bash CLI

## Quick Start

1. Preferred for OpenClaw: store the token at `skills.entries.iex-cloud.apiKey` and back it with a SecretRef via `openclaw secrets configure`.
2. For direct shell use outside OpenClaw, set `export IEX_TOKEN=...`.
3. Compatibility fallback: `export IEX_CLOUD_TOKEN=...`.
4. Read endpoint/parameter guidance in `references/api_docs.md`.
5. Use `scripts/iex_cloud_cli.sh` for reliable calls.

Example:

```bash
scripts/iex_cloud_cli.sh quote AAPL
scripts/iex_cloud_cli.sh chart AAPL 1m
scripts/iex_cloud_cli.sh movers mostactive
```

## Workflow

1. Classify request type:
- latest quote: `quote`
- historical bars: `chart`
- company/fundamentals: `company`, `stats`
- market movers: `movers`
- multi-symbol pulls: `batch`
2. Validate required parameters before call dispatch.
3. Execute request with token auth and timeout.
4. Validate response class:
- HTTP failure / transport failure
- JSON payload containing API error fields
- empty or malformed payload
5. Normalize output downstream as needed.

## Authentication and Safety

- Primary token env var: `IEX_TOKEN`.
- Compatibility token alias: `IEX_CLOUD_TOKEN`.
- In OpenClaw, prefer `skills.entries.iex-cloud.apiKey` with SecretRefs over plaintext config.
- Do not hardcode tokens in source files.
- Do not print full token values in logs.
- Prefer query parameter `token=...` when using these endpoints.
- The CLI accepts only trusted IEX API hosts for base URL overrides and warns when a non-default trusted override is used.
- `raw` calls are limited to relative IEX API paths. Do not pass full URLs.

## Reliability Guidance

- Use bounded timeouts (`curl --max-time` in CLI).
- Handle non-2xx responses as hard failures.
- Validate symbol, range, and list-type inputs early.
- For large jobs, use batch endpoints where possible.
- If you modify `IEX_BASE_URL` or pass `--base-url`, expect a warning so the change is visible during review.

## OpenClaw Secrets Management

- OpenClaw can inject this skill's API key from `skills.entries.iex-cloud.apiKey` for each agent run.
- Secret refs are preferred over plaintext because the resolved secret wins at runtime and plaintext is ignored.
- Recommended operator flow:
  - `openclaw secrets audit --check`
  - `openclaw secrets configure`
  - `openclaw secrets audit --check`
- For direct shell usage outside OpenClaw, export `IEX_TOKEN` in your shell instead.

## Included Files

- `scripts/iex_cloud_cli.sh`: Bash CLI for common endpoints and raw calls.
- `scripts/README.md`: CLI usage examples and command reference.
- `references/api_docs.md`: operational endpoint reference and guardrails.

## Resources

- API docs: https://iexcloud.io/docs/api/
- Status page: https://status.iexapis.com/
- Base URL (stable): `https://cloud.iexapis.com/stable`
- Sandbox URL: `https://sandbox.iexapis.com/stable`
- OpenClaw secrets: https://docs.openclaw.ai/gateway/secrets
