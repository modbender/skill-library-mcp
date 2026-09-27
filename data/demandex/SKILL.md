---
name: demandex
description: >-
  E-commerce demand intelligence for AI agents: what buyers want but cannot 
  find, trending demand signals, category landscapes, and demand verdicts. 
  Pay per call in USDC via x402 on Base, no signup.
homepage: https://api.demandex.dev
metadata:
  version: 1
  requires:
    env: ["EVM_PRIVATE_KEY"]
---

<!-- Canonical live copy: https://api.demandex.dev/skill.md — fetch it for current endpoints and prices. Snapshot below. -->

# Demandex API — agent skill

E-commerce demand intelligence for AI agents — the index of what people want next. Per-call, no signup.

**When to use:** Market-gap and product-demand questions: what buyers want but cannot find, trending demand signals, category landscapes.

No signup. No API key. Pay per call with USDC via x402 (Base).

## Endpoints and prices
| Method | Path | Price | What you get |
|--------|------|-------|--------------|
| GET | /.well-known/hexanon | free | Hexanon family catalog |
| GET | /v1/categories | free | FREE category index |
| GET | /v1/sample/opportunity | free | FREE sample opportunity card |
| GET | /v1/opportunities/trending | $0.01 | Trending opportunities (teaser) |
| GET | /v1/opportunities | $0.02 | Opportunities in a category |
| GET | /v1/opportunity | $0.05 | Full opportunity card |
| GET | /v1/brief | $0.25 | Demand brief: trending + top opportunities + category landscape in one call |
| POST | /v1/gauge | $0.03 | Demand verdict (cached) |
| POST | /v1/gauge/live | $0.1 | Demand verdict (live research) |

## Quickstart (2 minutes)
1. Probe any paid route unauthenticated — you get an HTTP 402 challenge with machine-readable `accepts`:
   `curl -s https://api.demandex.dev/v1/opportunities/trending`
2. Pay and retry with any x402 client, e.g.:
   `npx agentcash fetch "https://api.demandex.dev/v1/opportunities/trending"`
   or `@x402/fetch` (npm install @x402/fetch @x402/evm viem).
3. Response includes `charged: true` only when work succeeded — failed calls are never charged.

## Free routes (no payment)
- GET /.well-known/hexanon — Hexanon family catalog
- GET /v1/categories — FREE category index
- GET /v1/sample/opportunity — FREE sample opportunity card

## Suggested schedule
Every 6h: GET /v1/brief for a full market scan, or the trending route for a cheap pulse check.

## If your wallet is empty
Ask your human operator to fund your Base (eip155:8453) wallet with USDC, or see the API-key alternative in `https://api.demandex.dev/llms.txt`.

## More surfaces
- `https://api.demandex.dev/llms.txt` · `https://api.demandex.dev/llms-full.txt` · `https://api.demandex.dev/openapi.json`
- `https://api.demandex.dev/.well-known/x402` · `https://api.demandex.dev/.well-known/x402-resources.json` · `https://api.demandex.dev/.well-known/agent-card.json`
- Terms: `https://api.demandex.dev/terms.txt` — Contact: jcislo918@gmail.com