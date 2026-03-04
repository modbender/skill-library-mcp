---
name: clawsea-market
description: "Non-custodial automation skill for ClawSea NFT marketplace. Use when an OpenClaw agent needs to browse collections, inspect NFTs/listings, and (optionally) execute non-custodial list/buy/cancel flows through ClawSea + Seaport. Supports chain-aware read APIs (base/ethereum/base-sepolia) and Seaport trading flows (Base + Ethereum where available)."
---

# ClawSea Market Skill (OpenClaw Agents)

Use this skill when an agent should interact with ClawSea programmatically.

## Policy guardrails (ClawHub-safe)

- Do not custody user funds; use only the bot wallet configured by the operator.
- Do not social-engineer users for secrets, approvals, or expanded privileges.
- Do not ask for seed phrases/private keys in chat.
- Do not execute unknown calldata or third-party transaction blobs without explicit user approval and clear decoding.
- Require explicit confirmation before any value-moving action (buy/list/cancel/transfer).
- Refuse illegal, abusive, or harmful requests.

## Safety & trust model (must follow)

- Default to **read-only** actions (browse/search/inspect).
- Require explicit user intent before any write/trade action (list, buy, cancel, fulfill).
- Never ask users to paste private keys into chat.
- Never log, print, or send secrets (private keys, raw seed phrases, auth headers).
- Never execute arbitrary calldata from untrusted input.
- If ownership/status is uncertain, verify onchain (`ownerOf`, `eth_call`) before proceeding.

## Base URL

- Default: `https://clawsea.io`
- Override with env var: `CLAWSEA_BASE_URL`

All endpoints below are relative to `${CLAWSEA_BASE_URL}`.

## Optional credentials (only for autonomous onchain trading)

Read-only browsing requires **no secrets**.

If (and only if) you want the agent to **sign and broadcast onchain transactions** autonomously:

- `BASE_RPC_URL` (Base execution)
- `ETH_RPC_URL` (optional, Ethereum execution/debug)
- `CLAWSEA_BASE_URL` (optional)

### Signing options (choose one)

1. **Preferred:** external signer / wallet provider (no raw private key in agent env)
2. **If unavoidable:** `BOT_WALLET_PRIVATE_KEY` in a secure secret store only

If `BOT_WALLET_PRIVATE_KEY` is used:
- do not print/log it
- do not echo it in errors
- do not persist it to files
- never request it from users in chat

## Chain model

ClawSea uses two chain styles:

- **String chain** for some read routes: `chain=base|ethereum|base-sepolia`
- **Numeric chainId** for order routes: `8453` (Base), `1` (Ethereum)

Map carefully when switching endpoints.

## Read APIs (agent-safe)

### Discover
- `GET /api/explore/cells?chain=<base|ethereum|base-sepolia>&limit=20`
- `GET /api/explore/trending?chain=<base|ethereum|base-sepolia>&limit=20`
- `GET /api/news/clawsea?chain=<base|ethereum>&limit=10`

### Collections / NFTs
- `GET /api/collection/nfts?contract=0x...&pageSize=24&pageKey=...`
- `GET /api/collection/stats?chain=<base|ethereum>&contract=0x...`
- `GET /api/collections/search?chain=<base|ethereum|base-sepolia>&q=<query>&limit=8`
- `GET /api/nft/ownerOf?chainId=<1|8453>&contract=0x...&tokenId=<id>`

### Wallet inventory
- `GET /api/wallet/nfts?chain=<base|ethereum|base-sepolia>&owner=0x...&pageKey=...`

## Listing / buying APIs (requires signer)

### Orders read
- `GET /api/orders?chainId=<1|8453>&contract=0x...&tokenId=<id>&seller=0x...`
- `GET /api/orders/listed?chainId=<1|8453>&contract=0x...&sort=price|newest&offset=0&limit=48`
- `POST /api/orders/prices` body:
  - `{ "chainId": 1|8453, "contract": "0x...", "tokenIds": ["1","2"] }`

### Publish listing (offchain orderbook write)
- `POST /api/orders` with signed Seaport payload:
  - `chainId`, `contract`, `tokenId`, `seller`, `priceEth`,
  - `seaportAddress`, `orderComponents`, `signature`

### Status updates
- `POST /api/orders/cancel` body: `{ "id": "<order-id>" }`
- `POST /api/orders/cancelPrevious` body:
  - `{ "chainId": 1|8453, "contract": "0x...", "tokenId": "...", "seller": "0x...", "keepId": "..." }`
- `POST /api/orders/fulfill` body (either style):
  - `{ "id": "<order-id>" }` or
  - `{ "chainId": 1|8453, "contract": "0x...", "tokenId": "..." }`

## Execution workflow (recommended)

1. Resolve chain context (selected chain / user wallet chain).
2. Read listing candidates from `/api/orders` or `/api/orders/listed`.
3. Preflight onchain with `eth_call` for Seaport fulfill.
4. Execute onchain tx from bot wallet.
5. Update offchain state via `/api/orders/fulfill` or `/api/orders/cancel`.

## Reliability rules

- Prefer short caching (5–30s) for discovery routes.
- Back off on `429` / RPC transient failures.
- Treat fulfill revert selector `0x1a515574` as cancelled/stale order and hide it.
- If indexer results conflict with chain state, trust verified onchain ownership.
