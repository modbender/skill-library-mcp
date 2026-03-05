# DECK-0 Agent Skills

A skill for AI coding agents that enables interaction with the [DECK-0](https://app.deck-0.com) digital collectibles platform — browse collections, buy card packs, open packs, track progress, and publish your own card collections.

Skills follow the [Agent Skills](https://skills.sh/) standard.

## Installation

```bash
npx skills add signorcrypto/deck0-skills
```

## Use When

- "Show me available card collections"
- "Buy 3 packs from collection 0x..."
- "Open my packs"
- "What cards did I get?"
- "How's my collection progress?"
- "Show the leaderboard"
- "I want to create my own card collection"

## Capabilities

| Capability | Description |
|------------|-------------|
| **Browse** | Explore the shop and view collection details |
| **Buy** | Purchase card packs via on-chain smart contract transactions |
| **Open** | Open packs to reveal cards and earn badges |
| **Track** | Monitor collection progress and leaderboard rankings |
| **Publish** | Apply to create and publish your own card collection |


## Setup

### Prerequisites

- An EVM wallet with native tokens (APE on Apechain, ETH on Base) for purchasing packs
- [Foundry](https://book.getfoundry.sh/getting-started/installation) (`cast`) for signing (fallback mode only)
- `curl`, `jq`, `shasum` (standard on macOS/Linux)

### Wallet Resolution

The skill resolves a wallet signer in this order:

1. Existing agent wallet provided by the runtime
2. Existing Base wallet provided by the runtime
3. `DECK0_PRIVATE_KEY` environment variable (fallback)

For the fallback, set your private key:

```bash
export DECK0_PRIVATE_KEY="0x..."
```

Optional fallback chain override:

```bash
export DECK0_CHAIN_ID=8453
```

Prefer runtime-provided wallets when available. Use `DECK0_PRIVATE_KEY` only with explicit user approval, and never print or log it.

## Skill Structure

```
deck0-skills/
├── SKILL.md             # Main skill instructions and API reference
├── auth.md              # Authentication flow, signing code, payload construction
├── endpoints.md         # Complete API reference with request/response schemas
├── smart-contracts.md   # On-chain operations: minting packs, opening packs, ABI
├── examples.md          # End-to-end workflow examples
├── errors.md            # Error codes, rate limiting, troubleshooting
└── README.md
```

## How It Works

All API requests are authenticated via **EIP-191 wallet-signed messages** using custom `X-Agent-*` headers. Signature verification supports both:

- **EOA wallets** via `ethers.verifyMessage(...)`
- **Account abstraction / smart wallets** via **ERC-1271** validation on the provided `X-Agent-Chain-Id`

The skill handles:

1. **Browsing** — `GET` requests to the DECK-0 API for collections, leaderboards, and inventory
2. **Purchasing** — fetches a signed price from the API, then calls `mintPacks()` on the album smart contract with the signature and payment value
3. **Opening** — calls `openPacks(packIds)` on-chain, then polls the API for the card reveal recap
4. **Publishing** — submits a publisher application via `POST` to the API

## API Quick Reference

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/agents/v1/shop/albums` | GET | Yes | Browse available collections |
| `/api/agents/v1/collections/{address}` | GET | Yes | Get collection details |
| `/api/agents/v1/collections/{address}/leaderboard` | GET | Yes | View leaderboard |
| `/api/agents/v1/collections/{address}/price` | GET | Yes | Get signed price for purchase |
| `/api/agents/v1/me/albums` | GET | Yes | Your collections |
| `/api/agents/v1/me/packs` | GET | Yes | Your packs |
| `/api/agents/v1/me/cards` | GET | Yes | Your cards |
| `/api/agents/v1/me/pack-opening/{hash}` | GET | Yes | Pack opening recap |
| `/api/agents/v1/publisher/application` | POST | Yes | Submit publisher application |
| `/api/agents/v1/openapi` | GET | No | OpenAPI specification |

See [endpoints.md](./endpoints.md) for full request/response schemas.

## Rate Limits

| Scope | Limit | Window |
|-------|-------|--------|
| Per wallet | 60 requests | 1 minute |
| Per IP | 120 requests | 1 minute |

## Documentation

- **[SKILL.md](./SKILL.md)** — Main skill file with instructions and quick reference
- **[auth.md](./auth.md)** — Full authentication and signing guide
- **[endpoints.md](./endpoints.md)** — Complete API reference
- **[smart-contracts.md](./smart-contracts.md)** — On-chain operations and ABI
- **[examples.md](./examples.md)** — End-to-end workflow examples
- **[errors.md](./errors.md)** — Error codes and troubleshooting

## License

MIT
