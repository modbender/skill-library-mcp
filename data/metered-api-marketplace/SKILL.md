---
name: metered-api-marketplace
description: Build and operate a metered public API endpoint ("agent microservice") for OpenClaw skills/agents with API-key auth, per-request usage logging + pricing, prepaid balances, and crypto top-ups (BTC/ETH) via payment-processor webhooks. Use when you want to monetize a capability as a public API, add rate limiting/anti-abuse, implement a credit ledger, or add revenue share / platform fee logic.
---

# Metered API Marketplace

Provide a production-lean template for: **OpenClaw Skill → Public API Endpoint → Usage Metering → Crypto Payment Gateway → BTC/ETH wallets**.

This skill ships a runnable reference server (Fastify + SQLite) that:
- Accepts **structured JSON input**
- Performs a **high-value transformation** (pluggable “transformers”)
- Returns **structured JSON output**
- Enforces **signed API key** auth
- Checks **prepaid balance**, deducts per call, and logs usage
- Accepts **payment webhooks** (Coinbase Commerce / BTCPay Server style)
- Applies a **2.5% platform fee** in the ledger (fee addresses configurable)

## Workflow (do this in order)

### 1) Pick the productized capability (the thing people pay for)
Choose ONE transformer that is:
- high leverage (makes/keeps money)
- repeatable (called often)
- defensible (data, heuristics, workflow, or automation — not “generic summarization”)

Good defaults:
- revenue/offer optimizer
- ad copy optimizer
- lead scoring
- contract risk flags

If unclear, start with the included `revenue-amplifier` transformer and replace it later.

### 2) Run the reference server locally
Use the bundled server in `scripts/server/`.

Typical run:
- `cd scripts/server`
- `npm install`
- `cp .env.example .env` and edit
- `npm run dev`

Set flat launch pricing in `.env`:
- `COST_CENTS_PER_CALL=25`  # $0.25/call

### 3) Create an API key
Use `scripts/server/admin/create_key_pg.js` (or the admin HTTP endpoint) to create a key and starting balance.

### 4) Integrate from an OpenClaw skill / agent
Call the public endpoint with:
- `x-api-key`
- `x-timestamp` (unix ms)
- `x-signature` = `hex(HMAC_SHA256(api_secret, `${timestamp}.${rawBody}`))`

### 5) Add real payments
Wire a payment processor webhook to `/v1/payments/webhook/:provider`.

Providers are adapter-based:
- start with “manual” credits (admin script)
- then add Coinbase Commerce or BTCPay Server

### 6) Ship
Deploy behind TLS (Cloudflare / Fly.io / Render / AWS / GCP). Put rate limiting at the edge + in-app.

## Bundled resources

### scripts/server/
Runnable reference implementation:
- Fastify API server (long-running)
- Postgres ledger (balances, usage, credits)
- Signed API key auth
- Rate limiting + basic anti-abuse
- Webhook endpoint(s)

### scripts/nextjs-starter/
Vercel-ready Next.js API implementation:
- Serverless API routes (no `listen()`)
- Postgres ledger (Supabase Transaction Pooler recommended)
- Same auth + pricing + webhook concepts

### references/
Read only when needed:
- `references/api_reference.md` – endpoint contracts + auth/signing
- `references/billing_ledger.md` – pricing, fee logic, idempotency
- `references/providers.md` – provider adapters (Coinbase/BTCPay patterns)
