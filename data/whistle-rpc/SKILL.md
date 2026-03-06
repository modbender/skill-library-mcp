---
name: Whistle RPC
slug: whistle-rpc
version: 1.0.4
description: Production Solana RPC for AI agents. Unlimited JSON-RPC, WebSocket. 1 SOL/month via on-chain payment. No rate limits, no tiers.
author: DylanPort
homepage: https://whistle.ninja
repository: https://github.com/nickneedsaname/whistle-rpc
tags: solana, rpc, blockchain, web3, defi, agent, infrastructure, websocket, dex, trading
---

# Whistle RPC — Solana Infrastructure for AI Agents

Production Solana RPC with unlimited JSON-RPC, WebSocket, DEX data, and historical APIs. Designed for AI agents that need reliable blockchain access.

## Services

| Service | URL | What It Does |
|---------|-----|-------------|
| **RPC** | `https://rpc.whistle.ninja` | All Solana JSON-RPC 2.0 methods |
| **WebSocket** | `wss://rpc.whistle.ninja/ws` | Real-time subscriptions (slots, accounts, logs) |
| **DEX API** | `https://dex.whistle.ninja/v1` | Trending tokens, trades, holders, volume |
| **Historical** | `https://rpc.whistle.ninja/v1` | Enriched transaction & transfer history |
| **Agent API** | `https://api.whistle.ninja` | Subscription management |

## Authentication

All endpoints require an API key obtained through subscription:

```
Query param:  https://rpc.whistle.ninja?api_key=YOUR_KEY
Header:       X-API-Key: YOUR_KEY
Header:       Authorization: Bearer YOUR_KEY
```

## Supported RPC Methods

All standard Solana JSON-RPC 2.0:

**Account:** `getBalance`, `getAccountInfo`, `getMultipleAccounts`, `getTokenAccountsByOwner`, `getMinimumBalanceForRentExemption`

**Block:** `getSlot`, `getBlockHeight`, `getBlock`, `getEpochInfo`, `getRecentPerformanceSamples`

**Transaction:** `sendTransaction`, `simulateTransaction`, `getTransaction`, `getSignaturesForAddress`, `getLatestBlockhash`

**Node:** `getHealth`, `getVersion`

## WebSocket Subscriptions

`slotSubscribe`, `accountSubscribe`, `programSubscribe`, `signatureSubscribe`, `logsSubscribe`

Example:

```json
{"jsonrpc": "2.0", "id": 1, "method": "slotSubscribe"}
{"jsonrpc": "2.0", "id": 2, "method": "accountSubscribe", "params": ["ADDRESS"]}
```

Connect to `wss://rpc.whistle.ninja/ws` with your API key as a query param.

## DEX & Market Data

```
GET /trending          - Top trending tokens
GET /token/:mint       - Token price, volume, metadata
GET /volume            - Network-wide volume stats
GET /trades/:mint      - Recent trades for a token
GET /holders/:mint     - Holder distribution
```

Base URL: `https://dex.whistle.ninja/v1`

## Historical Data

```
GET /v1/transactions/:address      - Enriched transaction history
GET /v1/token-transfers/:address   - Token transfer history
GET /v1/swaps/:address             - Swap history
```

Base URL: `https://rpc.whistle.ninja`

## Subscription Flow (REST API)

Subscription costs 1 SOL/month, paid on-chain. The flow is three HTTP calls and one Solana transfer.

> **Important:** The payment step sends real SOL on mainnet. The agent must ask the human operator for explicit approval before signing any transaction, display the exact amount and recipient, and use a dedicated low-value wallet.

### 1. Request a quote

```
POST https://api.whistle.ninja/api/agent/subscribe
Content-Type: application/json

{ "walletAddress": "YOUR_WALLET_PUBKEY" }
```

Response: `{ "nonce": "...", "amount": 1, "recipient": "...", "duration": 30 }`

### 2. Send payment on-chain

Transfer `amount` SOL (from the quote) to the `recipient` address using a standard Solana `SystemProgram.transfer`. The agent must confirm the amount and recipient with the user before signing.

### 3. Activate the subscription

```
POST https://api.whistle.ninja/api/agent/activate
Content-Type: application/json

{
  "nonce": "FROM_STEP_1",
  "txSignature": "YOUR_TX_SIG",
  "walletAddress": "YOUR_WALLET_PUBKEY"
}
```

Response: `{ "apiKey": "...", "expiresAt": "...", "rpcUrl": "...", "wsUrl": "..." }`

### Check status

```
GET https://api.whistle.ninja/api/agent/status/YOUR_API_KEY
```

Response: `{ "active": true, "daysLeft": 29, "renewalNeeded": false }`

### Renewal

When `renewalNeeded` is `true`, repeat the subscribe → pay → activate flow. Always confirm with the user before renewing.

## Pricing

1 SOL/month. Everything included. No tiers. No rate limits. Revenue is distributed to WHISTLE stakers and node operators.

## Links

- Website: https://whistle.ninja
- NPM CLI: https://npmjs.com/package/whistle-rpc
- Tools manifest: https://whistle.ninja/tools.json
