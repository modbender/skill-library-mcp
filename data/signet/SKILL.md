---
name: signet
description: Interact with Signet onchain advertising on Hunt Town. Use when the user wants to check spotlight ad prices, list current ads/signatures, or post a URL to the Signet spotlight. Supports x402 payment protocol for programmatic ad placement by AI agents.
---

# Signet

Signet is an onchain advertising protocol on Base (Hunt Town Co-op). URLs compete for the spotlight slot, backed by HUNT tokens.

## CLI Tool

Install and use the `@signet-base/cli` tool:

```bash
# Estimate cost for spotlight placement
npx @signet-base/cli estimate --hours 6

# List recent signatures
npx @signet-base/cli list --count 10

# Post a URL (simulate first to check cost)
npx @signet-base/cli post --url https://example.com --hours 6 --simulate

# Post for real (requires PRIVATE_KEY env or --private-key)
PRIVATE_KEY=0x... npx @signet-base/cli post --url https://example.com --hours 6
```

### Commands

- **estimate** — Get estimated USDC cost. Options: `--hours <0-24>`, `--simulate`
- **list** — List recent spotlight signatures. Options: `--count <n>`
- **post** — Place a URL on the spotlight via x402 payment. Options: `--url <url>`, `--hours <0-24>`, `--private-key <key>`, `--simulate`

The `--simulate` flag on `post` runs the full x402 flow (estimate, get 402 requirements, create payment) but stops before submitting. Use it to verify costs before committing.

## API (Direct HTTP)

Base URL: `https://signet.sebayaki.com`

### Estimate Cost

```bash
curl "https://signet.sebayaki.com/api/x402/estimate?guaranteeHours=0"
```

Response:
```json
{
  "guaranteeHours": 0,
  "estimatedUSDC": "12.28",
  "estimatedUSDCRaw": "12280000",
  "spotlightAvailable": true,
  "spotlightRemainingSeconds": 0
}
```

`guaranteeHours` (0-24): hours the spotlight is guaranteed. 0 = can be overtaken immediately.

### List Signatures

```bash
curl "https://signet.sebayaki.com/api/signature/list?startIndex=0&endIndex=5"
```

Returns `{ signatures: [{ signatureIndex, url, huntAmount, viewCount, clickCount, metadata, timestamp, userWallet }] }`.

### Post Spotlight (x402)

```bash
# Step 1: POST without payment → 402 with requirements
curl -X POST https://signet.sebayaki.com/api/x402/spotlight \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","guaranteeHours":0}'

# Step 2: POST with payment header → 200
curl -X POST https://signet.sebayaki.com/api/x402/spotlight \
  -H "Content-Type: application/json" \
  -H "X-402: <encoded-payment>" \
  -d '{"url":"https://example.com","guaranteeHours":0}'
```

The x402 payment flow:
1. Server returns 402 with `accepts` array (USDC amount, payTo address, network)
2. Client signs a USDC payment (Permit2 on Base) using `@x402/core` and `@x402/evm`
3. Client retries with payment header
4. Server verifies via facilitator, executes onchain tx, settles payment
