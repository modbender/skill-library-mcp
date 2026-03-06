---
name: numinous-forecast
description: Get calibrated probabilities from Numinous (Bittensor Subnet 6) with metadata/provenance.
homepage: https://numinouslabs.io/
metadata: {"clawdbot":{"emoji":"🔮","homepage":"https://numinouslabs.io/","requires":{"bins":["python3"],"env":["NUMINOUS_X402_EVM_PRIVATE_KEY"]},"primaryEnv":"NUMINOUS_X402_EVM_PRIVATE_KEY","install":[{"id":"uv-evm","kind":"uv","module":"x402[httpx,evm]","label":"Install x402 (httpx + EVM) (uv)"},{"id":"uv-evm-svm","kind":"uv","module":"x402[httpx,evm,svm]","label":"Install x402 (httpx + EVM + SVM) (uv)"}]}}
---

# Numinous Forecast

This skill calls the Numinous forecasting API and returns a calibrated probability \(p \in [0,1]\) plus metadata/provenance.

Note: requests are paid per-call via **x402** (HTTP 402 → pay → retry). You’ll need a wallet key configured (see setup).

## Setup

Install Python deps (recommended: `uv`).

EVM-only (recommended):

```bash
uv pip install "x402[httpx,evm]"
```

If you also want Solana payments:

```bash
uv pip install "x402[httpx,evm,svm]"
```

Set the buyer key (required):

- `NUMINOUS_X402_EVM_PRIVATE_KEY`: EVM key (0x…) for Base / EVM payments

Optional (Solana payments):

- `NUMINOUS_X402_SVM_PRIVATE_KEY`: Solana key (base58) for Solana payments

Optional:

- `NUMINOUS_X402_PREFER`: `auto` (default) | `evm` | `svm`

Security note: these are **private keys**. Treat them like cash. Don’t paste them into chats/logs.

## Predict (query mode)

```bash
python3 "{baseDir}/predict_query.py" "Will BTC be above $100k by 2026-12-31?"
python3 "{baseDir}/predict_query.py" "Will Team X win League Y in 2026?" --topics sports
```

## Predict (event mode)

```bash
python3 "{baseDir}/predict_event.py" \
  --title "Will BTC be above $100k by 2026-12-31?" \
  --description "Resolve YES if BTC/USD spot price is strictly above $100,000 at 2026-12-31 23:59:59 UTC." \
  --cutoff "2026-12-31T23:59:59Z" \
  --topics general
```

## Output

Both scripts print JSON with these top-level fields:

- `ok`: `true|false`
- `prediction`: probability \(p \in [0, 1]\)
- `forecasted_at`: ISO timestamp (UTC)
- `forecaster_name`: forecaster identifier
- `metadata`: provenance/debug context (see below)
- `parsed_fields`: **query mode only** — structured event parsed from your query (see below)
- `error`: `null` on success; otherwise an error string

### `metadata` (common keys)

- `pool`: aggregation pool name
- `miner_uid`: miner UID chosen for this forecast
- `miner_hotkey`: miner hotkey identifier
- `reasoning`: model reasoning / explanation text
- `agent_name`: which forecaster agent produced the result
- `version_id`: model/version identifier
- `version_number`: integer version
- `raw_prediction`: original prediction value before any formatting
- `event_title`: resolved event title
- `event_cutoff`: resolved cutoff timestamp (UTC)

### `parsed_fields` (query mode only)

- `title`: resolved event title
- `description`: resolution criteria / event description
- `cutoff`: ISO cutoff (often ends with `Z`)
- `topics`: list of topic tags
