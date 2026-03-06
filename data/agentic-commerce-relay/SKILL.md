---
name: agentic-commerce-relay
description: Run the CCTP relay to burn USDC on a source chain and mint on a destination chain, returning verifiable receipts. Use for multichain agent-to-agent settlement, with optional Moltbook discovery and integrations.
---

# Agentic Commerce Relay

Use this skill when you need to settle USDC across CCTP-supported chains without deploying contracts. The relay script calls Circle’s official CCTP contracts and outputs a machine-readable receipt.

## Quick Use

From the repo root:

```bash
SRC_RPC=... \
DST_RPC=... \
PRIVATE_KEY=0x... \
SRC_USDC=0x... \
SRC_TOKEN_MESSENGER=0x... \
SRC_MESSAGE_TRANSMITTER=0x... \
DST_MESSAGE_TRANSMITTER=0x... \
DST_DOMAIN=... \
node scripts/cctp-bridge.js
```

### Required env
- `SRC_RPC`
- `DST_RPC`
- `PRIVATE_KEY`

### Optional env (override per chain)
- `SRC_USDC`
- `SRC_TOKEN_MESSENGER`
- `SRC_MESSAGE_TRANSMITTER`
- `DST_MESSAGE_TRANSMITTER`
- `DST_DOMAIN`
- `AMOUNT` (default `1000000`, 1 USDC with 6 decimals)

## Receipt
The script prints JSON with:
- `burnTx`
- `messageHash`
- `mintTx`
- `recipient`

## Optional modules

### Moltbook discovery
Find counterparties by submolt feed:
```bash
MOLTBOOK_API_KEY=... \
MOLTBOOK_BASE_URL=https://www.moltbook.com \
node scripts/discovery-moltbook.cjs --submolt usdc --sort new --tag payment
```

### Bundled integrations
This repo includes optional modules under `integrations/`:
- `integrations/mvp` (USDC Intent Payer)
- `integrations/anonx402-hackathon` (Anon x402 Relay)

Use these for intent parsing/guardrails or privacy, then call the relay to settle cross-chain.
