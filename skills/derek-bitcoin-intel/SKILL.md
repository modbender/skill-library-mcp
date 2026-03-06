---
name: Bitcoin Market Intelligence
description: Live Bitcoin market data and curated news — served over Lightning
  (L402) micropayments.
---

# Bitcoin Market Intelligence

Live Bitcoin market data and curated news — served over Lightning (L402) micropayments.

## What You Get

Your agent pays a few sats and gets back structured JSON with real market intelligence — not recycled headlines.

| Endpoint | Cost | What's Inside |
|----------|------|--------------|
| `/api/health` | Free | Service status, endpoints, pricing |
| `/api/market-brief` | 100 sats | BTC price, 24h change, curated non-obvious news, alert state |
| `/api/latest-alert` | 50 sats | Most recent breaking alert (5%+ moves, major events) |

Updates every 1–4 hours (market brief) and every 15 minutes (alerts).

## Quick Start

No API keys. No accounts. Just HTTP requests — free endpoints work with plain `curl`.

```bash
# Check status (free — no Lightning needed)
curl http://jnfaphddbeubdgpsbrw4d2z6wjew57djdzyrzkbt2ta7bi3wfzmfsfyd.onion/api/health
```

For paid endpoints, you need a way to pay Lightning invoices inline. Options:

```bash
# Option 1: lnget (auto-pays L402 invoices)
lnget -q http://jnfaphddbeubdgpsbrw4d2z6wjew57djdzyrzkbt2ta7bi3wfzmfsfyd.onion/api/market-brief

# Option 2: Any L402-compatible HTTP client
# The server returns HTTP 402 with a Lightning invoice — pay it, resubmit with the token
```

## Requirements

- **Free endpoints:** `curl` + Tor (or a Tor proxy)
- **Paid endpoints:** An L402-capable HTTP client (`lnget`, `l402-fetch`, or custom) + a funded Lightning channel

## Example Response

```json
{
  "endpoint": "market-brief",
  "timestamp": "2026-02-28T20:52:36Z",
  "price": {
    "price_usd": 67042.0,
    "change_24h_pct": 2.2
  },
  "recent_coverage": [
    {
      "topic": "morgan-stanley-bitcoin-custody-yield",
      "headline": "Morgan Stanley confirms plans for Bitcoin trading, lending, yield, and custody products",
      "timestamp": "2026-02-27T12:00:00-05:00"
    }
  ],
  "alert_state": {
    "active": false,
    "last_alert": "2026-02-26T14:30:00Z"
  }
}
```

## How L402 Works

1. Your agent sends a request to a paid endpoint
2. Server responds with HTTP 402 + a Lightning invoice
3. Your agent pays the invoice (fractions of a cent)
4. Server verifies payment, returns data
5. The L402 token is cached — reuse it until it expires

No signup. No rate limits. No API keys. Sats in, signal out.

## What Powers This

An autonomous Bitcoin intelligence agent running 24/7 on LND + Aperture (L402 reverse proxy) over a Tor hidden service. It monitors markets, tracks on-chain metrics, curates news from dozens of sources, and distills it into structured data for other agents.

Built for the agent economy — machines paying machines for signal.

> **Note:** `lnget` v0.1.0 has a known macaroon parsing bug with some L402 servers. If you hit errors, use a wrapper script that handles the 402→pay→resubmit flow manually.
