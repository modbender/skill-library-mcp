---
name: xerolite
description: "Integrate OpenClaw with Xerolite - IBKR. Use when: querying Xerolite API, placing orders, searching contracts."
metadata: {"openclaw":{"requires":{"bins":["node"]}}}
---

# Xerolite

**Trading Bridge from TradingView to Interactive Brokers.**

[Xerolite](https://www.xeroflex.com/xerolite/) automates execution of your trading ideas: it connects [TradingView](https://www.tradingview.com/) alerts to your [Interactive Brokers](https://www.interactivebrokers.com/) account so orders are sent in real time with no manual steps. You design the logic and alerts in TradingView; Xerolite handles the bridge to IB (TWS or IB Gateway) and execution.

This skill lets your OpenClaw agent call the Xerolite REST API to **place orders** and **search contracts** — so you can trade or look up symbols from natural language or automation without leaving your workflow.

## Package Structure

```
skills/xerolite/
├── SKILL.md              # This file
├── scripts/
│   ├── xerolite.mjs      # CLI (order place, contract search)
└── references/
    └── API.md            # REST API guide
```

## Capabilities

- Place orders via Xerolite REST API.
- Search contracts via Xerolite REST API.

## Commands

Use these commands from the skill directory (or with `{baseDir}` in other skills).

**Default flag values** (optional; omit to use): `--currency USD`, `--asset-class STOCK`, `--exch SMART`.

### Place order

Required: `--action`, `--qty`, `--symbol`. Optional: `--currency`, `--asset-class`, `--exch`.

```bash
# Minimal (defaults: USD, STOCK, SMART)
node {baseDir}/scripts/xerolite.mjs order place --symbol AAPL --action BUY --qty 10

# Full
node {baseDir}/scripts/xerolite.mjs order place \
  --symbol AAPL \
  --currency USD \
  --asset-class STOCK \
  --exch SMART \
  --action BUY \
  --qty 10
```

JSON sent to `POST /api/internal/agent/order/place-order`:

```json
{
  "name": "Agent",
  "action": "BUY",
  "qty": "10",
  "symbol": "AAPL",
  "currency": "USD",
  "asset_class": "STOCK",
  "exch": "SMART"
}
```

### Search contract

Required: `--symbol`. Optional: `--currency`, `--asset-class`, `--exch`.

```bash
# Minimal (defaults: USD, STOCK, SMART)
node {baseDir}/scripts/xerolite.mjs contract search --symbol AAPL

# Full
node {baseDir}/scripts/xerolite.mjs contract search \
  --symbol AAPL \
  --currency USD \
  --asset-class STOCK \
  --exch SMART
```

JSON sent to `POST /api/internal/agent/contract/search`:

```json
{
  "brokerName": "IBKR",
  "symbol": "AAPL",
  "currency": "USD",
  "xeroAssetClass": "STOCK"
}
```

## REST API

For the order and contract search endpoints used by this skill, see [references/API.md](references/API.md).

## Requirements

- Node.js 18+ (for built-in `fetch`)
- **CLI only**: Optional `XEROLITE_API_URL` — base URL for Xerolite API. If not set, defaults to `http://localhost` (same machine or local network). No API key in this version; may be added in a future version.
