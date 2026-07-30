---
name: signalis
description: >-
  Narrative and content intelligence for AI agents: a 4-hourly Master 
  Intelligence digest (20-source roster) plus AI-business Pulse narratives 
  and raw recent content. Pay per call in USDC via x402 on Base, no signup.
homepage: https://api.signalis.dev
metadata:
  version: 1
  requires:
    env: ["EVM_PRIVATE_KEY"]
---

<!-- Canonical live copy: https://api.signalis.dev/skill.md — fetch it for current endpoints and prices. Snapshot below. -->

# Signalis API — agent skill

Global intelligence, real-time awareness for AI agents on x402 — the 4-hourly Master Intelligence digest (20-source roster) plus AI-business Pulse narratives. Per-call, no signup.

**When to use:** Narrative and content intelligence: emerging narratives, pulse content, intelligence briefs.

No signup. No API key. Pay per call with USDC via x402 (Base).

## Endpoints and prices
| Method | Path | Price | What you get |
|--------|------|-------|--------------|
| GET | /.well-known/hexanon | free | Hexanon family catalog |
| GET | /v1/intelligence/brief | free | Master Intelligence digest brief |
| GET | /v1/intelligence/index | free | Master Intelligence digest index |
| GET | /v1/intelligence/sample | free | Sample master digest |
| GET | /v1/intelligence/latest | free | Latest Master Intelligence digest |
| POST | /v1/intelligence/feedback | free | Submit digest quality feedback |
| GET | /v1/intelligence/history | $0.03 | Historical master digests |
| GET | /v1/pulse/narratives | $0.01 | Active AI-business narratives |
| GET | /v1/pulse/narratives/{id} | $0.01 | Narrative detail |
| GET | /v1/pulse/digests | $0.03 | Historical AI-business narrative digests |
| GET | /v1/pulse/content/recent | $0.02 | Raw recent content items |

## Quickstart (2 minutes)
1. Probe any paid route unauthenticated — you get an HTTP 402 challenge with machine-readable `accepts`:
   `curl -s https://api.signalis.dev/v1/intelligence/history?hours=YOUR_HOURS`
2. Pay and retry with any x402 client, e.g.:
   `npx agentcash fetch "https://api.signalis.dev/v1/intelligence/history?hours=YOUR_HOURS"`
   or `@x402/fetch` (npm install @x402/fetch @x402/evm viem).
3. Response includes `charged: true` only when work succeeded — failed calls are never charged.

## Free routes (no payment)
- GET /.well-known/hexanon — Hexanon family catalog
- GET /v1/intelligence/brief — Master Intelligence digest brief
- GET /v1/intelligence/index — Master Intelligence digest index
- GET /v1/intelligence/sample — Sample master digest
- GET /v1/intelligence/latest — Latest Master Intelligence digest
- POST /v1/intelligence/feedback — Submit digest quality feedback

## Suggested schedule
Every 6h: fetch pulse narratives for narrative shifts; daily: the latest intelligence brief.

## If your wallet is empty
Ask your human operator to fund your Base (eip155:8453) wallet with USDC, or see the API-key alternative in `https://api.signalis.dev/llms.txt`.

## More surfaces
- `https://api.signalis.dev/llms.txt` · `https://api.signalis.dev/llms-full.txt` · `https://api.signalis.dev/openapi.json`
- `https://api.signalis.dev/.well-known/x402` · `https://api.signalis.dev/.well-known/x402-resources.json` · `https://api.signalis.dev/.well-known/agent-card.json`
- Terms: `https://api.signalis.dev/terms.txt` — Contact: jcislo918@gmail.com