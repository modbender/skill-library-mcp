---
name: x402lint
description: >-
  Conformance scanner for x402 sellers: lint any x402 API origin against what 
  x402scan, Bazaar, AgentCash and agent buyers require, and browse the graded 
  discovery directory. Pay per call in USDC via x402 on Base, no signup.
homepage: https://api.x402lint.dev
metadata:
  version: 1
  requires:
    env: ["EVM_PRIVATE_KEY"]
---

<!-- Canonical live copy: https://api.x402lint.dev/skill.md — fetch it for current endpoints and prices. Snapshot below. -->

# x402lint — agent skill

Conformance scanner for x402 sellers — lint your origin against what x402scan, Bazaar, AgentCash and agent buyers actually require. Per-call USDC pricing, no signup.

**When to use:** x402 seller conformance: lint any x402 API origin, browse the graded discovery directory.

No signup. No API key. Pay per call with USDC via x402 (Base).

## Endpoints and prices
| Method | Path | Price | What you get |
|--------|------|-------|--------------|
| GET | /v1/status | free | FREE scan status lookup |
| GET | /v1/checks | free | FREE check catalog |
| POST | /v1/scan | $0.15 | Full conformance scan |
| GET | /v1/report | $0.02 | Cached full report |
| GET | /v1/directory | free | FREE graded directory |
| GET | /v1/featured | free | FREE featured (recent A-grades) |
| GET | /v1/project | free | FREE single project record |
| POST | /v1/verify/start | free | FREE start ownership verification |
| POST | /v1/verify/confirm | free | FREE confirm ownership verification |
| POST | /v1/listing | free | FREE listing control (verified owners) |

## Quickstart (2 minutes)
1. Probe any paid route unauthenticated — you get an HTTP 402 challenge with machine-readable `accepts`:
   `curl -s https://api.x402lint.dev/v1/scan`
2. Pay and retry with any x402 client, e.g.:
   `npx agentcash fetch "https://api.x402lint.dev/v1/scan"`
   or `@x402/fetch` (npm install @x402/fetch @x402/evm viem).
3. Response includes `charged: true` only when work succeeded — failed calls are never charged.

## Free routes (no payment)
- GET /v1/status — FREE scan status lookup
- GET /v1/checks — FREE check catalog
- GET /v1/directory — FREE graded directory
- GET /v1/featured — FREE featured (recent A-grades)
- GET /v1/project — FREE single project record
- POST /v1/verify/start — FREE start ownership verification
- POST /v1/verify/confirm — FREE confirm ownership verification
- POST /v1/listing — FREE listing control (verified owners)

## Suggested schedule
Weekly: re-scan your own origin so your directory grade stays fresh.

## If your wallet is empty
Ask your human operator to fund your Base (eip155:8453) wallet with USDC, or see the API-key alternative in `https://api.x402lint.dev/llms.txt`.

## More surfaces
- `https://api.x402lint.dev/llms.txt` · `https://api.x402lint.dev/llms-full.txt` · `https://api.x402lint.dev/openapi.json`
- `https://api.x402lint.dev/.well-known/x402` · `https://api.x402lint.dev/.well-known/x402-resources.json` · `https://api.x402lint.dev/.well-known/agent-card.json`
- Terms: `https://api.x402lint.dev/terms.txt` — Contact: 