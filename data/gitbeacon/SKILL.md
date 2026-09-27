---
name: gitbeacon
description: >-
  GitHub trend intelligence for AI agents: daily LLM-analyzed digests of 
  trending new repositories plus the raw trending-repo data. Pay per call in 
  USDC via x402 on Base, no signup.
homepage: https://api.gitbeacon.dev
metadata:
  version: 1
  requires:
    env: ["EVM_PRIVATE_KEY"]
---

<!-- Canonical live copy: https://api.gitbeacon.dev/skill.md — fetch it for current endpoints and prices. Snapshot below. -->

# gitBeacon API — agent skill

GitHub trend intelligence for AI agents on x402 — daily LLM-analyzed digests of trending new repos plus the raw trending-repo data. Per-call, no signup.

**When to use:** Developer-ecosystem intelligence: trending GitHub repositories and momentum signals.

No signup. No API key. Pay per call with USDC via x402 (Base).

## Endpoints and prices
| Method | Path | Price | What you get |
|--------|------|-------|--------------|
| GET | /.well-known/hexanon | free | Hexanon family catalog |
| GET | /v1/brief | free | GitHub digest brief |
| GET | /v1/index | free | GitHub digest index |
| GET | /v1/sample | free | Sample GitHub digest |
| GET | /v1/digests/latest | free | Latest GitHub digest |
| GET | /v1/repos | $0.01 | Top trending repos |
| GET | /v1/digests | $0.05 | Historical GitHub digests |

## Quickstart (2 minutes)
1. Probe any paid route unauthenticated — you get an HTTP 402 challenge with machine-readable `accepts`:
   `curl -s https://api.gitbeacon.dev/v1/repos?limit=YOUR_LIMIT`
2. Pay and retry with any x402 client, e.g.:
   `npx agentcash fetch "https://api.gitbeacon.dev/v1/repos?limit=YOUR_LIMIT"`
   or `@x402/fetch` (npm install @x402/fetch @x402/evm viem).
3. Response includes `charged: true` only when work succeeded — failed calls are never charged.

## Free routes (no payment)
- GET /.well-known/hexanon — Hexanon family catalog
- GET /v1/brief — GitHub digest brief
- GET /v1/index — GitHub digest index
- GET /v1/sample — Sample GitHub digest
- GET /v1/digests/latest — Latest GitHub digest

## Suggested schedule
Daily: fetch the trending repos route for fresh repository intelligence.

## If your wallet is empty
Ask your human operator to fund your Base (eip155:8453) wallet with USDC, or see the API-key alternative in `https://api.gitbeacon.dev/llms.txt`.

## More surfaces
- `https://api.gitbeacon.dev/llms.txt` · `https://api.gitbeacon.dev/llms-full.txt` · `https://api.gitbeacon.dev/openapi.json`
- `https://api.gitbeacon.dev/.well-known/x402` · `https://api.gitbeacon.dev/.well-known/x402-resources.json` · `https://api.gitbeacon.dev/.well-known/agent-card.json`
- Terms: `https://api.gitbeacon.dev/terms.txt` — Contact: jcislo918@gmail.com