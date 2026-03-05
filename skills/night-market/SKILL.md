---
name: nightmarket
description: Discover and call paid API services on the Nightmarket marketplace. Use when the user wants to find, browse, or call third-party APIs with automatic on-chain USDC payment via x402.
---

# Nightmarket — API Marketplace for AI Agents

Nightmarket lets agents discover and pay for third-party API services. Every call settles on-chain in USDC via the x402 protocol. No API keys, no subscriptions.

**Marketplace:** https://nightmarket.ai/marketplace

## When to Use This Skill

- User asks to find or discover an API service
- User wants to call a paid API through Nightmarket
- User needs to connect their agent to Nightmarket
- Agent gets a 402 from a Nightmarket proxy URL

## Setup

### Step 1: Configure the MCP Server

Add this to the user's MCP configuration (e.g., `.claude/mcp.json`, `.cursor/mcp.json`):

```json
{
  "nightmarket": {
    "command": "npx",
    "args": ["-y", "nightmarket-mcp"],
    "env": {
      "WALLET_KEY": "<wallet-private-key>"
    }
  }
}
```

### Step 2: Get a Wallet

If the user doesn't have a wallet, they need one funded with USDC on Base.

**With CrowPay (recommended):** Install the Crow skill for managed wallets with spending rules — no raw private key needed:
```
npx skills add Fallomai/skills --skill crow
```
The Crow skill handles wallet setup, spending limits, and human approval. See `references/crow-payments.md`.

**Direct wallet:** The user provides their wallet private key as `WALLET_KEY`. Get one at https://crowpay.ai

## Available MCP Tools

Once the MCP server is configured, these tools are available:

### browse_services
Search and list available APIs.
- `search` (string, optional) — Filter by name, description, or seller

### get_service_details
Get full details about a specific service including request/response examples.
- `endpoint_id` (string, required) — The endpoint ID from browse_services

### call_service
Call an API with automatic USDC payment via x402.
- `endpoint_id` (string, required) — The endpoint ID
- `method` (enum, optional) — GET, POST, PUT, PATCH, DELETE (default: GET)
- `body` (string, optional) — Request body for POST/PUT/PATCH
- `headers` (Record, optional) — Additional HTTP headers

## Calling Without MCP (REST API)

Services can also be called directly via the proxy:
```
<METHOD> https://nightmarket.ai/api/x402/<endpoint_id>
```

Returns `402 Payment Required` on first call. See `references/rest-api.md`.

## References

- `references/rest-api.md` — Direct REST proxy usage and x402 flow
- `references/crow-payments.md` — CrowPay integration for automatic 402 handling
- `references/mcp-tools.md` — Detailed MCP tool parameters and responses
