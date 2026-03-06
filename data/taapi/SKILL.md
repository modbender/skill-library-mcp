---
name: taapi
description: Use this skill to fetch TAAPI.IO indicator data for crypto or stocks, including fast single-indicator requests and bulk/multi-construct queries for agentic trading workflows.
metadata: {"openclaw":{"homepage":"https://taapi.io/","requires":{"bins":["curl"],"env":["TAAPI_SECRET"]},"primaryEnv":"TAAPI_SECRET"}}
---

# OpenClaw TAAPI Skill

## Overview

This skill gives Codex a reliable workflow for TAAPI.IO integrations and analysis tasks. It includes a CLI helper for low-friction, repeatable API calls from agents and scripts.

Use this skill when:
- You need technical indicators (for example `rsi`, `macd`, `adx`) from TAAPI.IO.
- You need to evaluate one symbol quickly via GET requests.
- You need batch evaluations in one request using `/bulk`.
- You need multi-construct queries across symbols/timeframes/exchanges.
- You need deterministic shell-based tooling for agent loops.

## Workflow Decision Tree

1. If you need one indicator for one market/timeframe, use `direct`.
2. If you need many indicators in one API call, use `bulk`.
3. If you need multiple symbol/timeframe constructs in one API call, use `multi`.
4. If you need non-exchange candles (custom data), this skill documents API expectations but you should create a custom payload and use `bulk --payload-file`.

## API Facts (Checked February 27, 2026)

- Base host: `https://api.taapi.io`
- Direct endpoint pattern: `GET /{indicator}`
- Bulk endpoint: `POST /bulk`
- Mandatory direct params: `secret`, `symbol`, `interval`, and `exchange` for crypto (`type=crypto`, default).
- `type=stocks` is supported for stocks/ETFs.
- Common optional direct params: `backtrack` (max 50), `results`, `addResultTimestamp`, `gaps`, `chart=heikinashi`.
- Bulk and rate limit constraints: max `20` calculations per request on standard plans.
- Plan rate limits documented as:
  - Free: 1 request / 15s
  - Basic: 5 requests / 15s
  - Pro: 30 requests / 15s
  - Expert: 75 requests / 15s

Primary docs:
- https://taapi.io/documentation/
- https://taapi.io/documentation/integration/direct/
- https://taapi.io/documentation/integration/post-rest-bulk/
- https://taapi.io/documentation/multiple-constructs/
- https://taapi.io/documentation/rate-limits/
- https://taapi.io/indicators/

## Security And Runtime Requirements

- This skill is an open-source wrapper around the commercial TAAPI.IO API. Live requests require a TAAPI.IO account secret.
- Set `TAAPI_SECRET` only in the current shell session. Prefer `export TAAPI_SECRET=...` over persistent/global shell files, and prefer the env var over `--secret` so the secret is less exposed in process listings.
- `curl` is required for all live requests.
- `jq` is only required for the `multi` command. `direct`, `bulk`, and CI-safe argument tests work without it.
- The default and audited endpoint is `https://api.taapi.io`. Overriding `TAAPI_BASE_URL` is an advanced escape hatch and should only be used deliberately. Sending requests to another host can expose your secret and request payloads to that endpoint.
- `tests/smoke-live.sh` sends real network requests with your live secret. Use a revocable secret and avoid running it outside an isolated session.

## Quick Start

Use the local helper:

```bash
# 1) Set secret once per session
export TAAPI_SECRET="your_secret"

# 2) Direct RSI query
bash scripts/taapi-agent.sh direct \
  --indicator rsi \
  --exchange binance \
  --symbol BTC/USDT \
  --interval 1h

# 3) Bulk query from JSON payload
bash scripts/taapi-agent.sh bulk --payload-file examples/bulk-single-construct.json

# 4) Multi-construct query (requires jq)
bash scripts/taapi-agent.sh multi \
  --exchange binance \
  --symbols BTC/USDT,ETH/USDT \
  --intervals 15m,1h \
  --indicators rsi,supertrend

# 5) Live smoke tests (requires real TAAPI_SECRET and network access)
bash tests/smoke-live.sh
```

## CLI Tasks

### `direct`
Single indicator via GET:
```bash
bash scripts/taapi-agent.sh direct \
  --indicator macd \
  --exchange binance \
  --symbol BTC/USDT \
  --interval 1h \
  --opt backtrack=1 \
  --opt addResultTimestamp=true
```

### `bulk`
POST an explicit bulk payload file to `/bulk`:
```bash
bash scripts/taapi-agent.sh bulk --payload-file examples/bulk-single-construct.json
bash scripts/taapi-agent.sh bulk --payload-file examples/bulk-multi-constructs.json
```

### `multi`
Build multi-construct payload from flags (for `/bulk`). Requires `jq`:
```bash
bash scripts/taapi-agent.sh multi \
  --exchange binance \
  --symbols BTC/USDT,ETH/USDT \
  --intervals 15m,1h \
  --indicators rsi,supertrend
```

## Agentic Usage Guidelines

- Always pass `--json` in automation loops for stable machine parsing.
- Keep per-request calculations at `<=20`; split workloads deterministically.
- Handle `429` with bounded retries and backoff.
- Prefer `bulk` for multi-indicator evaluations on the same construct.
- Prefer `multi` for cross-symbol/timeframe batching when plan supports constructs.
- For stocks, include `--type stocks` and omit `--exchange` if not required by your setup.
- Treat `TAAPI_BASE_URL` overrides as a deliberate deviation from the default OpenClaw-audited path. If you must override it, use a session-scoped `TAAPI_ALLOW_UNOFFICIAL_BASE_URL=1` as an explicit acknowledgement.

## Resources

### `scripts/taapi-agent.sh`
Bash CLI with:
- direct GET indicator calls
- bulk POST using payload files
- multi-construct payload generation
- retries for transient failures and 429 rate limits
- opt-in guardrails for unofficial base URLs
- optional `jq` formatting, with `jq` required only for `multi`

### `examples/`
Ready-to-run payloads:
- `examples/bulk-single-construct.json`
- `examples/bulk-multi-constructs.json`

### `tests/`
- `tests/test-cli.sh`: CI-safe argument and error-path checks (no API call required).
- `tests/smoke-live.sh`: Live smoke checks using real TAAPI credentials.

CI command:
```bash
bash tests/test-cli.sh
```

Live smoke command:
```bash
export TAAPI_SECRET="your_secret"
bash tests/smoke-live.sh
```
