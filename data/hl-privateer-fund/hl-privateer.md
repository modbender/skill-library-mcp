---
name: hl-privateer
description: >
  Access HL Privateer, an open agentic Hyperliquid discretionary trading desk.
  Read live positions, AI analysis, copy-trade signals, and risk state via x402
  pay-per-call endpoints. No API keys. No sign-ups. Just x402 on Base (USDC).
metadata:
  author: hl-privateer
  version: "2.0"
  url: https://hlprivateer.xyz
  source: https://github.com/ADWilkinson/hlprivateer.xyz
  license: proprietary
  category: finance
  tags:
    - hyperliquid
    - trading
    - copy-trading
    - signals
    - x402
    - defi
    - perps
compatibility: >
  Requires network access to api.hlprivateer.xyz.
  Payment via x402 v2 exact scheme (USDC on Base, eip155:8453).
  Facilitator: https://facilitator.payai.network
---

# HL Privateer -- Agent Skill

HL Privateer is an open, agentic discretionary trading desk on Hyperliquid. A fund of autonomous agents making discretionary long/short calls -- positions, analysis, signals, and risk state are all accessible via paid x402 endpoints.

You are an agent. You can follow our trades, read our analysis, copy our positions, or integrate our signals into your own strategy. Pay per call. No API keys. No sign-ups. Just x402.

## Skill Files

This skill package contains the following files, all served at `https://hlprivateer.xyz/skills/`:

| File | Purpose |
|------|---------|
| `hl-privateer.md` | This file. Primary skill definition with full instructions. |
| `llms.txt` | Agent-oriented quick start and endpoint catalog. |
| `api.md` | Complete REST + WebSocket API reference. |
| `x402.md` | x402 payment quickstart with example flows. |
| `agents.json` | Machine-readable OpenAgents v1 discovery document. |

## Quick Start

1. Hit any agent endpoint: `GET https://api.hlprivateer.xyz/v1/agent/stream/snapshot`
2. Receive `402 Payment Required` with `PAYMENT-REQUIRED` header containing payment instructions
3. Decode the header (Base64 JSON) to get price, network, payTo address, and facilitator URL
4. Create and sign an x402 payment payload for the specified amount (USDC on Base)
5. Retry the same request with the `PAYMENT-SIGNATURE` header containing the signed payment (Base64 JSON)
6. Receive data in the `200` response plus `PAYMENT-RESPONSE` settlement header

## Base URLs

- REST API: `https://api.hlprivateer.xyz`
- WebSocket: `wss://ws.hlprivateer.xyz`
- Web UI: `https://hlprivateer.xyz`

## x402 Payment Details

- **Network**: Base (eip155:8453)
- **Asset**: USDC (`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`)
- **Facilitator**: `https://facilitator.payai.network`
- **Protocol**: x402 v2 (exact scheme)

See `x402.md` in this directory for the full payment flow with curl examples.

## Paid Endpoints (x402)

All endpoints are GET requests against `https://api.hlprivateer.xyz`. Pay per call via x402.

### $0.01/call

| Endpoint | What You Get |
|----------|-------------|
| `/v1/agent/stream/snapshot` | Mode, PnL%, health, open positions, recent ops tape |
| `/v1/agent/positions` | Full position array -- symbols, sides, sizes, entries, PnL |
| `/v1/agent/orders` | Open orders on the book |
| `/v1/agent/analysis?latest=true` | Latest AI strategist analysis with thesis and signals |
| `/v1/agent/analysis` | Analysis history (paginated, filterable by correlationId) |

### $0.02/call

| Endpoint | What You Get |
|----------|-------------|
| `/v1/agent/insights?scope=market` | Risk config, signal timeline, account snapshot |
| `/v1/agent/insights?scope=ai` | Full dashboard: floor state, risk, analysis, copy summary |

### $0.03/call

| Endpoint | What You Get |
|----------|-------------|
| `/v1/agent/copy/trade?kind=signals` | Audit trail of proposals, analysis, risk decisions, basket events |
| `/v1/agent/copy/trade?kind=positions` | Position data formatted for copy-trading |

## Free Endpoints (no payment required)

| Endpoint | What You Get |
|----------|-------------|
| `/v1/public/pnl` | Current PnL% and runtime mode |
| `/v1/public/floor-snapshot` | Mode, PnL%, health, account value, positions, ops tape |
| `/v1/public/floor-tape` | Recent ops log lines from all agent roles |
| `/healthz` | Service health check |

### Example: Check Current PnL (free)

```bash
curl https://api.hlprivateer.xyz/v1/public/pnl
```

```json
{
  "pnlPct": 1.92,
  "mode": "READY",
  "updatedAt": "2026-02-13T16:20:00Z"
}
```

## Agent Use Cases

### Copy Trading

Read positions and signals to mirror trades on your own account.

1. Poll `/v1/agent/positions` for current positions ($0.01)
2. Poll `/v1/agent/copy/trade?kind=signals` for entry/exit signals ($0.03)
3. Poll `/v1/agent/copy/trade?kind=positions` for copy-formatted position data ($0.03)

### Signal Integration

Consume analysis and risk signals to inform your own strategy.

1. Read `/v1/agent/analysis?latest=true` for the latest strategist thesis ($0.01)
2. Read `/v1/agent/insights?scope=ai` for full AI floor summary ($0.02)
3. Subscribe to WebSocket at `wss://ws.hlprivateer.xyz` for real-time floor tape

### Monitoring / Dashboard

Build a monitoring view or alerting system.

1. Free: Poll `/v1/public/floor-snapshot` for mode, PnL, positions
2. Paid: Read `/v1/agent/stream/snapshot` for richer health and ops data ($0.01)
3. Paid: Read `/v1/agent/insights?scope=market` for risk config and signal timeline ($0.02)

### Portfolio Composition Research

Understand how the desk constructs and manages its basket.

1. Read `/v1/agent/analysis` for historical analysis entries ($0.01)
2. Read `/v1/agent/insights?scope=ai` for the full AI dashboard ($0.02)
3. Read `/v1/agent/copy/trade?kind=signals` for the full proposal audit trail ($0.03)

## WebSocket Protocol

Connect to `wss://ws.hlprivateer.xyz` for real-time events.

### Subscribe to channels

```json
{ "type": "sub.add", "channel": "public.tape" }
```

### Receive events

```json
{
  "type": "event",
  "channel": "public.tape",
  "payload": {
    "eventType": "FLOOR_TAPE",
    "role": "strategist",
    "line": "LONG HYPE -- momentum breakout, funding neutral"
  }
}
```

### Client message types

| Type | Purpose |
|------|---------|
| `sub.add` | Subscribe to a channel |
| `sub.remove` | Unsubscribe from a channel |
| `cmd.exec` | Execute a command (requires auth) |
| `ping` | Keepalive |

### Server message types

| Type | Purpose |
|------|---------|
| `sub.ack` | Subscription confirmed |
| `event` | Channel event payload |
| `cmd.result` | Command execution result |
| `error` | Error response |
| `pong` | Keepalive response |

## How The Desk Works

HL Privateer runs autonomous agents on a single Hyperliquid account:

- **Strategist**: scans 50+ perp markets, generates long/short proposals with thesis and sizing
- **Research**: regime hypotheses, macro context, funding analysis, social sentiment
- **Risk**: explains risk posture (advisory only -- hard-gated by deterministic risk engine)
- **Execution**: suggests tactics, annotates slippage expectations
- **Ops**: monitors feeds, service health, circuit breakers (3s heartbeat)
- **Market Data**: detects stale feeds, regime shifts, funding divergences
- **Scribe**: produces audit narratives for each proposal cycle

All proposals pass through a deterministic risk engine (fail-closed) before execution. No agent can bypass risk limits. The human operator holds kill-switch authority.

## Runtime Modes

| Mode | Meaning |
|------|---------|
| `INIT` | Starting up, loading keys and config |
| `WARMUP` | Collecting initial market data window |
| `READY` | Flat, watching for opportunities |
| `IN_TRADE` | Active long/short positions |
| `REBALANCE` | Adjusting position weights for parity |
| `HALT` | Operator-initiated stop |
| `SAFE_MODE` | Automatic safety stop (dependency or data failure) |

## Error Responses

All errors follow a standard envelope:

```json
{
  "error": {
    "code": "RISK_DENY",
    "message": "Proposal denied by max drawdown rule",
    "requestId": "req_01J..."
  }
}
```

Common error codes:

| Code | Meaning |
|------|---------|
| `PAYMENT_REQUIRED` | x402 payment needed (HTTP 402) |
| `UNAUTHORIZED` | Missing or invalid authentication |
| `FORBIDDEN` | Insufficient tier or capability |
| `RISK_DENY` | Risk engine denied the action |
| `RATE_LIMITED` | Too many requests |
| `INTERNAL_ERROR` | Server error |

## Further Reading

- Full API reference: https://hlprivateer.xyz/skills/api.md
- x402 payment guide: https://hlprivateer.xyz/skills/x402.md
- Machine-readable discovery: https://hlprivateer.xyz/skills/agents.json
- Agent-oriented quick start: https://hlprivateer.xyz/skills/llms.txt
- Root agent index: https://hlprivateer.xyz/AGENT.md
- Root LLM map: https://hlprivateer.xyz/llms.txt
