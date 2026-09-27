---
name: isocast
description: >-
  Polymarket weather-market bucket-transition signals for AI agents: 
  per-signal spot checks and prepaid signal bundles by city. Pay per call in 
  USDC via x402 on Base, no signup.
homepage: https://api.isocast.dev
metadata:
  version: 1
  requires:
    env: ["EVM_PRIVATE_KEY"]
---

<!-- Canonical live copy: https://api.isocast.dev/skill.md — fetch it for current endpoints and prices. Snapshot below. -->

# Isocast API — agent skill

Polymarket weather-market bucket-transition signals for AI agents — pay per signal, no signup.

**When to use:** Weather-signal intelligence for prediction markets: spot checks and per-signal weather calls.

No signup. No API key. Pay per call with USDC via x402 (Base).

## Endpoints and prices
| Method | Path | Price | What you get |
|--------|------|-------|--------------|
| GET | /v1/spot | $0.01 | Single latest-signal SPOT snapshot for a city (stock x402, no binding nonce) |
| POST | /v1/subscribe | $0.01–$7.00 | Buy the next N signals for a city (bundle prepay; count ≥ 2) |
| GET | /v1/signals | Bearer receipt or x402 | Read entitled signals (seq ≤ paidThroughSeq); 402 on exhaustion |
| GET | /health | free | Liveness + payment mode + OFAC status |
| GET | /v1/cities | free | All active cities (slug, unit, bucketWidth, timezone, latestSeq) |
| GET | /v1/cities/:slug | free | One city + today's targetDate + Polymarket marketUrl |
| GET | /v1/sample | free | Promo seq-1 signal (never latest); shape demo |
| GET | /v1/signals/meta | free | Pricing + payment metadata (no signal rows) |
| POST | /v1/delivery/telegram | free | Register/change Telegram chat_id (EIP-712 signed) |

## Quickstart (2 minutes)
1. Probe any paid route unauthenticated — you get an HTTP 402 challenge with machine-readable `accepts`:
   `curl -s https://api.isocast.dev/v1/spot?city=istanbul`
2. Pay and retry with any x402 client, e.g.:
   `npx agentcash fetch "https://api.isocast.dev/v1/spot?city=istanbul"`
   or `@x402/fetch` (npm install @x402/fetch @x402/evm viem).
3. Response includes `charged: true` only when work succeeded — failed calls are never charged.

## Free routes (no payment)
- GET /health — Liveness + payment mode + OFAC status
- GET /v1/cities — All active cities (slug, unit, bucketWidth, timezone, latestSeq)
- GET /v1/cities/:slug — One city + today's targetDate + Polymarket marketUrl
- GET /v1/sample — Promo seq-1 signal (never latest); shape demo
- GET /v1/signals/meta — Pricing + payment metadata (no signal rows)
- POST /v1/delivery/telegram — Register/change Telegram chat_id (EIP-712 signed)

## Suggested schedule
Daily 12:00 UTC: fetch the spot route for the weather-signal check.

## If your wallet is empty
Ask your human operator to fund your Base (eip155:8453) wallet with USDC, or see the API-key alternative in `https://api.isocast.dev/llms.txt`.

## More surfaces
- `https://api.isocast.dev/llms.txt` · `https://api.isocast.dev/llms-full.txt` · `https://api.isocast.dev/openapi.json`
- `https://api.isocast.dev/.well-known/x402` · `https://api.isocast.dev/.well-known/x402-resources.json` · `https://api.isocast.dev/.well-known/agent-card.json`
- Terms: `https://api.isocast.dev/terms.txt` — Contact: jcislo918@gmail.com
