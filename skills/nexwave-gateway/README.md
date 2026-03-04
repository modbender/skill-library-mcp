# nexwave-gateway 🌐

**Unified Crosschain USDC for OpenClaw Agents — Powered by Circle Gateway**

> The only OpenClaw skill that gives agents a single USDC balance accessible on any chain in <500ms. No bridging. No liquidity pools. No waiting.

## What It Does

`nexwave-gateway` enables OpenClaw agents to use [Circle Gateway](https://www.circle.com/gateway) for instant crosschain USDC operations. Instead of managing separate USDC balances on Ethereum, Base, Avalanche, etc., your agent deposits USDC into Gateway on any chain and can instantly access it on any other supported chain.

### The Flow

```
1. Deposit USDC on Chain A → Gateway credits unified balance
2. Sign burn intent → Gateway returns attestation (<500ms)
3. Submit attestation on Chain B → USDC minted for you
```

### Why This Matters for Agents

- **Capital efficiency**: No pre-positioning USDC across chains
- **Speed**: <500ms crosschain transfers vs. 15-20 minute bridge waits
- **Simplicity**: One balance, accessible everywhere
- **Non-custodial**: Funds only move with your signature

## Quick Start

### 1. Install

```bash
clawhub install nexwave-gateway
# or manually:
git clone <repo-url> ~/.openclaw/skills/nexwave-gateway
```

### 2. Configure

Install the Circle Wallet skill and set your credentials:

```bash
clawhub install eltontay/circle-wallet

# Set Circle Wallet credentials (from https://console.circle.com)
export CIRCLE_API_KEY=your_api_key
export CIRCLE_ENTITY_SECRET=your_entity_secret
export CIRCLE_WALLET_SET_ID=your_wallet_set_id
```

No raw private keys needed — uses Circle's MPC-secured developer-controlled wallets.

### 3. Setup & Run

```bash
cd ~/.openclaw/skills/nexwave-gateway
bash setup.sh
cd gateway-app
node check-balance.js   # See your unified balance
node deposit.js         # Deposit USDC into Gateway
node transfer.js        # Transfer crosschain to Base
```

### 4. Get Testnet USDC

Visit [faucet.circle.com](https://faucet.circle.com) — 20 USDC per address per chain, every 2 hours.

## Supported Chains (Testnet)

| Chain | Network | Domain ID | Notes |
|---|---|---|---|
| Ethereum | Sepolia | 0 | ~20 min finality |
| Base | Sepolia | 6 | ~13-19 min finality |
| Arc | Testnet | 26 | ~0.5s finality, USDC-native gas |

## Files

| File | Description |
|---|---|
| `SKILL.md` | OpenClaw skill definition with instructions |
| `setup.sh` | Project initialization script |
| `abis.js` | Gateway Wallet & Minter contract ABIs |
| `gateway-client.js` | Lightweight Circle Gateway API client |
| `circle-wallet-client.js` | Circle Programmable Wallets SDK wrapper (MPC signing + transactions) |
| `typed-data.js` | EIP-712 typed data for burn intents |
| `setup-gateway.js` | Chain clients and contract initialization |
| `check-balance.js` | Query unified USDC balance |
| `deposit.js` | Deposit USDC into Gateway |
| `transfer.js` | Full crosschain transfer demo |

## Circle Products Used

- **[Circle Gateway](https://developers.circle.com/gateway)** — Unified crosschain USDC balance
- **[Circle Programmable Wallets](https://developers.circle.com/wallets)** — MPC-secured developer-controlled wallets (no raw private keys)
- **[Arc L1](https://docs.arc.network)** — Circle's purpose-built blockchain where USDC is the native gas token
- **[USDC](https://www.circle.com/usdc)** — Native stablecoin on all supported chains
- **[Circle Faucet](https://faucet.circle.com)** — Testnet USDC

## Architecture

```
┌─────────────────────────────────────────────┐
│           OpenClaw Agent (NexBot)            │
│  ┌───────────────────────────────────────┐  │
│  │       nexwave-gateway Skill           │  │
│  │  check-balance │ deposit │ transfer   │  │
│  └───────────┬───────────────────────────┘  │
└──────────────┼──────────────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌────────────┐    ┌──────────────────┐
│  Gateway   │    │   Gateway API    │
│  Wallet    │    │  (attestations)  │
│  Contract  │    │  <500ms response │
│ (on-chain) │    │                  │
└────────────┘    └──────────────────┘
    │                     │
    ▼                     ▼
┌──────────────────────────────────┐
│       Gateway Minter Contract    │
│    (mints USDC on dest chain)    │
└──────────────────────────────────┘
```

## Why Gateway > Bridging

| | Traditional Bridge | Circle Gateway |
|---|---|---|
| **Speed** | 13-19 minutes (Ethereum) | <500ms |
| **Trust** | Third-party bridge operators | Circle (USDC issuer) |
| **Liquidity** | Fragmented pools | Unified balance |
| **Capital** | Pre-positioned per chain | On-demand, any chain |
| **USDC type** | Often "wrapped" | Always native USDC |

## Built By

**[Nexwave](https://nexwave.dev)** — AI Trading Agent Factory

Built for the [USDC Agentic Hackathon](https://www.moltbook.com/post/b021cdea-de86-4460-8c4b-8539842423fe) on Moltbook.

## References

- [Circle Gateway Docs](https://developers.circle.com/gateway)
- [Gateway Quickstart](https://developers.circle.com/gateway/quickstarts/unified-balance-evm)
- [Full Quickstart Code](https://github.com/circlefin/evm-gateway-contracts/tree/master/quickstart)
- [Gateway Blog Post](https://www.circle.com/blog/circle-gateway-redefining-crosschain-ux)
- [Machine-to-Machine Micropayments](https://www.circle.com/blog/enabling-machine-to-machine-micropayments-with-gateway-and-usdc)

## License

MIT
