---
name: crypto-signal
description: AI-powered crypto intelligence from 50+ Telegram groups. Get trending topics, alpha signals, whale alerts, and market sentiment — all via API. Free tier available.
---

# Crypto Signal

Real-time crypto intelligence extracted from Telegram groups using AI.

## Setup

1. Get your free API key at https://api.qtxh.top (or ask the bot to create one)
2. Set the environment variable:

```bash
export CRYPTOSIGNAL_API_KEY="cs_your_key_here"
```

Or add to your OpenClaw config:

```yaml
env:
  CRYPTOSIGNAL_API_KEY: "cs_your_key_here"
```

## Commands

All commands use the `crypto-signal` CLI:

### Get trending topics (last 24h)
```bash
crypto-signal trending
crypto-signal trending --hours 12
```

### Get alpha signals
```bash
crypto-signal signals
crypto-signal signals --type whale_transfer
crypto-signal signals --type price_move --limit 10
```

### List monitored groups
```bash
crypto-signal groups
```

### Check service status
```bash
crypto-signal status
```

## Signal Types

| Type | Description |
|------|-------------|
| `whale_transfer` | Large token transfers (>$1M) |
| `price_move` | Significant price movements |
| `liquidation` | Large liquidation events |
| `regulatory` | SEC/CFTC/regulatory news |
| `security` | Hacks, exploits, breaches |
| `listing` | Exchange listings/delistings |
| `airdrop` | Airdrops and token launches |
| `partnership` | Major partnerships |

## Plans

| Feature | Free | Pro ($1/mo) |
|---------|------|-------------|
| Groups monitored | 3 | 50+ |
| API calls/day | 10 | Unlimited |
| Signal delay | 6h | Real-time |
| Custom groups | ❌ | ✅ (up to 20) |
| History & Search | ❌ | ✅ |
| Webhook push | ❌ | ✅ |

## Examples for OpenClaw

Tell your agent:
- "What's trending in crypto today?" → calls `crypto-signal trending`
- "Any whale alerts in the last 12 hours?" → calls `crypto-signal signals --type whale_transfer --hours 12`
- "Show me the latest alpha signals" → calls `crypto-signal signals`
