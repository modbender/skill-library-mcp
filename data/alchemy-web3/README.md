# alchemy-web3

> Query blockchain data across 80+ chains with one CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Made by GizmoLab](https://img.shields.io/badge/Made%20by-GizmoLab-blue)](https://gizmolab.io?utm_source=alchemy-web3-skill&utm_medium=github&utm_campaign=skill)

Get NFTs, token balances, transaction history, and more using Alchemy's production-grade APIs. Works for human devs AND AI agents.

## Features

- 🔍 Query any wallet's NFTs, tokens, balances
- ⛓️ 80+ chains (Ethereum, Polygon, Arbitrum, Base, Solana...)
- 🤖 AI agent workflows included
- 🛠️ Simple CLI + curl examples + JS SDK

## Quick Start

### 1. Get API Key

Sign up at [alchemy.com](https://www.alchemy.com/?utm_source=gizmolab&utm_medium=skill&utm_campaign=alchemy-web3) (free tier available)

### 2. Set API Key

```bash
export ALCHEMY_API_KEY="your_key_here"
```

### 3. Query

```bash
# Get wallet balance
./scripts/alchemy.sh balance 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045

# Get all NFTs
./scripts/alchemy.sh nfts 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045

# Get token balances
./scripts/alchemy.sh tokens 0x...

# Check gas price
./scripts/alchemy.sh gas

# Query different chain
./scripts/alchemy.sh --chain polygon-mainnet balance 0x...
```

## Commands

| Command | Description |
|---------|-------------|
| `balance <address>` | Get ETH/native balance |
| `tokens <address>` | Get all ERC-20 token balances |
| `nfts <address>` | Get all NFTs owned |
| `nft-metadata <contract> <id>` | Get specific NFT metadata |
| `collection <contract>` | Get NFTs in collection |
| `transfers <address>` | Get transaction history |
| `block <number\|latest>` | Get block info |
| `tx <hash>` | Get transaction details |
| `gas` | Get current gas prices |

## Supported Chains

Ethereum, Polygon, Arbitrum, Optimism, Base, zkSync, Linea, Scroll, Blast, Solana, and 70+ more.

See [references/chains.md](references/chains.md) for full list.

## AI Agent Workflows

This skill is designed for AI agents to automate blockchain monitoring:

- **Whale Tracker** — Monitor large wallets for moves
- **Portfolio Monitor** — Track balances across chains  
- **NFT Floor Alert** — Alert on price drops
- **Token Change Detector** — Detect incoming/outgoing tokens
- **Gas Optimizer** — Wait for low gas to transact

See [references/agent-workflows.md](references/agent-workflows.md) for complete examples.

## Installation

### OpenClaw / ClawHub

```bash
clawhub install alchemy-web3
```

### Manual

```bash
git clone https://github.com/0xGizmolab/alchemy-web3-skill.git
cd alchemy-web3-skill
chmod +x scripts/alchemy.sh
```

## Documentation

- [SKILL.md](SKILL.md) — Full documentation
- [references/nft-api.md](references/nft-api.md) — NFT API reference
- [references/token-api.md](references/token-api.md) — Token API reference
- [references/node-api.md](references/node-api.md) — Node API reference
- [references/chains.md](references/chains.md) — Supported chains
- [references/agent-workflows.md](references/agent-workflows.md) — AI agent examples

## Resources

- [Alchemy Dashboard](https://dashboard.alchemy.com)
- [Alchemy Docs](https://www.alchemy.com/docs)
- [Alchemy SDK](https://github.com/alchemyplatform/alchemy-sdk-js)

## About

**Built by [GizmoLab](https://gizmolab.io?utm_source=alchemy-web3-skill&utm_medium=github&utm_campaign=skill)** 🔧

GizmoLab is a Web3 development agency building dApps, smart contracts, and blockchain tools.

- 🌐 [gizmolab.io](https://gizmolab.io?utm_source=alchemy-web3-skill&utm_medium=github&utm_campaign=skill) — Agency services
- 🛠️ [tools.gizmolab.io](https://tools.gizmolab.io?utm_source=alchemy-web3-skill&utm_medium=github&utm_campaign=skill) — Free blockchain dev tools
- 🎨 [ui.gizmolab.io](https://ui.gizmolab.io?utm_source=alchemy-web3-skill&utm_medium=github&utm_campaign=skill) — Web3 UI components

## License

MIT
