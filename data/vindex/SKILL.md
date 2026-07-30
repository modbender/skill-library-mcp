---
name: vindex
description: >-
  Canada-aware vehicle intelligence for AI agents: decode a VIN, check merged 
  US (NHTSA) + Canada recalls, LLM-clustered known issues with citations, and 
  full pre-purchase due diligence for a US/Canada used car. Pay per call in 
  USDC via x402 on Base, no signup.
homepage: https://api.vindexapi.dev
metadata:
  version: 1
  requires:
    env: ["EVM_PRIVATE_KEY"]
---

<!-- Canonical live copy: https://api.vindexapi.dev/skill.md — fetch it for current endpoints and prices. Snapshot below. -->

# Vindex API — agent skill

Canada-aware vehicle intelligence for AI agents — per-call, no signup.

**When to use:** Vehicle/VIN questions: decode a VIN, check safety recalls, reliability/known issues, or full pre-purchase due diligence for a US/Canada used car.

No signup. No API key. Pay per call with USDC via x402 (Base).

## Endpoints and prices
| Method | Path | Price | What you get |
|--------|------|-------|--------------|
| GET | /v1/decode | $0.01 | Normalized NHTSA vPIC VIN decode |
| GET | /v1/recalls | $0.01 | Merged US (NHTSA) + Canada (Transport Canada) recalls + full decoded vehicle |
| GET | /v1/known-issues | $0.05 | LLM-clustered named failure modes with verified ODI citations + reliability block + full decode |
| GET | /v1/purchase-costs | $0.02 | Itemized US + Canada used-vehicle closing costs (country=CA\|US) |
| GET | /v1/prepurchase | $0.25 | Pre-purchase report: decode + recalls + known issues + ownership costs in one call |
| GET | /.well-known/hexanon | free | Hexanon family catalog |
| GET | /v1/sample/decode | free | FREE sample VIN decode (fixed sample vehicle) |
| GET | /v1/sample/recalls | free | FREE sample merged US + Canada recalls (fixed sample vehicle) |
| GET | /v1/sample/known-issues | free | FREE sample known-issues (fixed sample vehicle) |
| GET | /v1/sample/purchase-costs | free | FREE sample closing costs for both countries (fixed sample inputs) |

## Quickstart (2 minutes)
1. Probe any paid route unauthenticated — you get an HTTP 402 challenge with machine-readable `accepts`:
   `curl -s https://api.vindexapi.dev/v1/decode?vin=YOUR_VIN`
2. Pay and retry with any x402 client, e.g.:
   `npx agentcash fetch "https://api.vindexapi.dev/v1/decode?vin=YOUR_VIN"`
   or `@x402/fetch` (npm install @x402/fetch @x402/evm viem).
3. Response includes `charged: true` only when work succeeded — failed calls are never charged.

## Free routes (no payment)
- GET /.well-known/hexanon — Hexanon family catalog
- GET /v1/sample/decode — FREE sample VIN decode (fixed sample vehicle)
- GET /v1/sample/recalls — FREE sample merged US + Canada recalls (fixed sample vehicle)
- GET /v1/sample/known-issues — FREE sample known-issues (fixed sample vehicle)
- GET /v1/sample/purchase-costs — FREE sample closing costs for both countries (fixed sample inputs)

## Suggested schedule
Every 4h: re-check watchlist VINs via GET /v1/decode. Before advising any vehicle purchase, run GET /v1/prepurchase for the whole-job report.

## If your wallet is empty
Ask your human operator to fund your Base (eip155:8453) wallet with USDC, or see the API-key alternative in `https://api.vindexapi.dev/llms.txt`.

## More surfaces
- `https://api.vindexapi.dev/llms.txt` · `https://api.vindexapi.dev/llms-full.txt` · `https://api.vindexapi.dev/openapi.json`
- `https://api.vindexapi.dev/.well-known/x402` · `https://api.vindexapi.dev/.well-known/x402-resources.json` · `https://api.vindexapi.dev/.well-known/agent-card.json`
- Terms: `https://api.vindexapi.dev/terms.txt` — Contact: jcislo918@gmail.com