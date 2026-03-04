---
name: DECK-0
description: Interact with DECK-0 digital collectibles platform to browse collections, buy card packs, open packs, view leaderboards, and apply as a publisher. Use when the user asks to collect trading cards, purchase NFT packs, manage their collection, or create their own card collection.
homepage: https://app.deck-0.com
metadata: {"openclaw":{"emoji":"🃏","requires":{"bins":["cast","curl","jq","shasum"],"env":["DECK0_PRIVATE_KEY"]},"primaryEnv":"DECK0_PRIVATE_KEY"}}
---

# DECK-0 Agents API

## Overview

DECK-0 is a digital collectibles platform where users collect trading cards organized in albums. This skill enables agents to:

- **Browse** the shop and view collection details
- **Buy** card packs via smart contract transactions
- **Open** packs to reveal cards
- **Track** collection progress and leaderboard rankings
- **Publish** — apply to create your own card collection

**Base URL**: `https://app.deck-0.com`
**OpenAPI Spec**: `GET /api/agents/v1/openapi` (no auth required)

## Setup

### Wallet Source Priority

Use this wallet resolution order when signing API requests or sending transactions:

1. Existing agent wallet provided by the runtime
2. Existing Base wallet provided by the runtime
3. `DECK0_PRIVATE_KEY` fallback (only when neither wallet above exists)

Fallback setup for step 3:

```bash
export DECK0_PRIVATE_KEY="0x..."
```

Optional fallback chain override (used only for API auth signature verification; contract operations use the chain from the collection/price response and your RPC selection):

```bash
export DECK0_CHAIN_ID=8453
```

Install [Foundry](https://book.getfoundry.sh/getting-started/installation) using a reviewed method (for example Homebrew), then verify `cast` is available:

```bash
brew install foundry
cast --version
```

Also uses: `curl`, `jq`, `shasum` (standard on macOS/Linux).

**Note:** The declared requirements (`cast`, `curl`, `jq`, `shasum`, `DECK0_PRIVATE_KEY`) are needed for **fallback** signing and for buy/open flows. Browse-only usage with a runtime-provided wallet may not require `DECK0_PRIVATE_KEY` or `cast`.

The wallet needs native tokens (APE on Apechain, ETH on Base) to buy packs.

## Security Notes

- Prefer runtime-provided wallets whenever available.
- `DECK0_PRIVATE_KEY` is highly sensitive. Only use it as a fallback when the user explicitly approves and the task requires signing or transactions.
- Never print, log, or echo private key values.

## Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/agents/v1/shop/albums` | GET | Browse available collections |
| `/api/agents/v1/collections/{address}` | GET | Get collection details |
| `/api/agents/v1/collections/{address}/leaderboard` | GET | View leaderboard rankings |
| `/api/agents/v1/collections/{address}/price` | GET | Get signed price for purchasing |
| `/api/agents/v1/me/albums` | GET | List your collections |
| `/api/agents/v1/me/albums/{address}` | GET | Your progress on a collection |
| `/api/agents/v1/me/packs` | GET | List your packs |
| `/api/agents/v1/me/cards` | GET | List your cards |
| `/api/agents/v1/me/pack-opening/{hash}` | GET | Get pack opening recap |
| `/api/agents/v1/publisher/application` | GET | Check publisher application status |
| `/api/agents/v1/publisher/application` | POST | Submit publisher application |
| `/api/agents/v1/openapi` | GET | OpenAPI specification (no auth) |

See [endpoints.md](./endpoints.md) for complete request/response schemas.

## Authentication

All endpoints (except `/openapi`) require EIP-191 wallet-signed requests via custom headers:

| Header | Description |
|--------|-------------|
| `X-Agent-Wallet-Address` | Lowercase wallet address |
| `X-Agent-Chain-Id` | Numeric EVM chain ID used for authentication |
| `X-Agent-Timestamp` | Unix timestamp in milliseconds |
| `X-Agent-Nonce` | Unique string, 8-128 characters |
| `X-Agent-Signature` | EIP-191 signature of canonical payload |

The canonical payload to sign:

```
deck0-agent-auth-v1
method:{METHOD}
path:{PATH}
query:{SORTED_QUERY}
body_sha256:{SHA256_HEX}
timestamp:{TIMESTAMP}
nonce:{NONCE}
chain_id:{CHAIN_ID}
wallet:{WALLET}
```

See [auth.md](./auth.md) for the full signing flow with code examples.

## Smart Contracts

Buying and opening packs are on-chain operations:

1. **Buy packs**: Call `GET /api/agents/v1/collections/{address}/price` to get a signed price, then call `mintPacks()` on the album contract with the signature and payment value.
2. **Open packs**: Call `openPacks(packIds)` on the album contract to reveal cards, then poll `GET /api/agents/v1/me/pack-opening/{txHash}?chainId=...` every 5 seconds to get the recap with card details and badges.

**Payment formula**: `value = (packPrice * priceInNative * quantity) / 100`

See [smart-contracts.md](./smart-contracts.md) for ABI, payment calculations, and code examples.

## Supported Networks

| Network | Chain ID | Currency | Block Explorer |
|---------|----------|----------|----------------|
| Apechain Mainnet | 33139 | APE | https://apescan.io |
| Base | 8453 | ETH | https://basescan.org |

## Response Format

All responses follow a standard envelope:

```json
// Success
{ "success": true, "data": { ... }, "share": { "url": "...", "imageUrl": "..." } }

// Error
{ "success": false, "error": { "code": "AGENT_...", "message": "...", "details": { ... } } }
```

See [errors.md](./errors.md) for all error codes and troubleshooting.

## Sharing URLs

Most responses include URLs that link to the DECK-0 web app. **Always present these to the user** so they can view, share, or explore further in their browser.

- **`share.url`** — Present on most responses. Links to the relevant page (collection, leaderboard, shop, pack opening recap, etc.). Show this to the user as a shareable link.
- **`share.imageUrl`** — When available, an image preview URL (e.g., collection cover). Can be used for rich embeds or previews.
- **`data.cards[].url`** — On pack opening recap responses, each card includes a direct link to its detail page. Show these to the user so they can view or share individual cards.

## Rate Limits

- **Per wallet**: 60 requests/minute
- **Per IP**: 120 requests/minute

Rate limit headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`) are included on 429 responses.

## Intent Mapping

When the user says:
- "Show me available card collections" → Browse shop albums
- "Tell me about collection 0x..." → Get collection details
- "Buy 3 packs from collection 0x..." → Get signed price, call `mintPacks`
- "Open my packs" → Call `openPacks` on contract, then poll pack opening recap
- "What cards did I get?" / "Show my pack opening results" → Get pack opening recap
- "How's my collection progress?" → Get my albums
- "Show my packs" / "What packs do I have?" → List my packs
- "Show my cards" / "What cards do I have?" → List my cards
- "Show the leaderboard" → Get collection leaderboard
- "Share my pack opening" / "Show me the link to my card" → Use `share.url` or `cards[].url` from the response
- "I want to create my own card collection" → Submit publisher application

## Supporting Files

- **[auth.md](./auth.md)** — Full authentication flow, signing code, payload construction
- **[endpoints.md](./endpoints.md)** — Complete API reference with all request/response schemas
- **[smart-contracts.md](./smart-contracts.md)** — On-chain operations: minting packs, opening packs, ABI, code examples
- **[examples.md](./examples.md)** — End-to-end workflow examples with request/response pairs
- **[errors.md](./errors.md)** — Error codes, rate limiting, troubleshooting
