---
name: orcatrace
description: >-
  Polymarket intelligence for AI agents: whale positioning with a verifiable 
  track record, signals, a 4-hourly Intelligence Digest, resolving-soon 
  markets, and single-market deep research. Pay per call in USDC via x402 on 
  Base, no signup.
homepage: https://api.orcatrace.dev
metadata:
  version: 1
  requires:
    env: ["EVM_PRIVATE_KEY"]
---

<!-- Canonical live copy: https://api.orcatrace.dev/skill.md — fetch it for current endpoints and prices. Snapshot below. -->

# OrcaTrace API — agent skill

Polymarket intelligence for AI agents on x402 — whale tracking with a verifiable track record, signals, the 4-hourly Intelligence Digest, resolving-market analysis, and $1 deep research. Per-call, no signup. Track smart money, see what others miss.

**When to use:** Polymarket intelligence: whale positioning, market signals, soon-resolving markets, track records.

No signup. No API key. Pay per call with USDC via x402 (Base).

## Endpoints and prices
| Method | Path | Price | What you get |
|--------|------|-------|--------------|
| GET | /.well-known/hexanon | free | Hexanon family catalog |
| GET | /v1/index | free | Polymarket feed index |
| GET | /v1/pulse | free | Polymarket top-3 movers brief |
| GET | /v1/digest/brief | free | Polymarket digest teaser |
| GET | /v1/sample | free | Polymarket sample shapes |
| GET | /v1/track-record | free | Whale-calibration scorecard |
| GET | /v1/latest | $0.01 | Most recent Polymarket feed item |
| GET | /v1/signal | $0.01 | One Polymarket feed item |
| GET | /v1/signals | $0.03 | Batch Polymarket feed items |
| GET | /v1/digest | $0.1 | Polymarket Intelligence Digest |
| GET | /v1/digest/history | $0.05 | Historical Polymarket digests |
| GET | /v1/resolving | $0.02 | Markets resolving soon |
| GET | /v1/whales | $0.05 | Whale calibration table |
| GET | /v1/research | $1 | Single-market deep-dive research |

## Quickstart (2 minutes)
1. Probe any paid route unauthenticated — you get an HTTP 402 challenge with machine-readable `accepts`:
   `curl -s https://api.orcatrace.dev/v1/latest`
2. Pay and retry with any x402 client, e.g.:
   `npx agentcash fetch "https://api.orcatrace.dev/v1/latest"`
   or `@x402/fetch` (npm install @x402/fetch @x402/evm viem).
3. Response includes `charged: true` only when work succeeded — failed calls are never charged.

## Free routes (no payment)
- GET /.well-known/hexanon — Hexanon family catalog
- GET /v1/index — Polymarket feed index
- GET /v1/pulse — Polymarket top-3 movers brief
- GET /v1/digest/brief — Polymarket digest teaser
- GET /v1/sample — Polymarket sample shapes
- GET /v1/track-record — Whale-calibration scorecard

## Suggested schedule
Every 4h: fetch the latest signal route; check the resolving route ahead of market-close windows.

## If your wallet is empty
Ask your human operator to fund your Base (eip155:8453) wallet with USDC, or see the API-key alternative in `https://api.orcatrace.dev/llms.txt`.

## More surfaces
- `https://api.orcatrace.dev/llms.txt` · `https://api.orcatrace.dev/llms-full.txt` · `https://api.orcatrace.dev/openapi.json`
- `https://api.orcatrace.dev/.well-known/x402` · `https://api.orcatrace.dev/.well-known/x402-resources.json` · `https://api.orcatrace.dev/.well-known/agent-card.json`
- Terms: `https://api.orcatrace.dev/terms.txt` — Contact: jcislo918@gmail.com