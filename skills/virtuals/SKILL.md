---
name: virtuals
version: 1.0.0
description: "Virtuals Protocol integration for OpenClaw. Create, manage and trade tokenized AI agents on Base."
metadata: {"openclaw": {"emoji": "🎭", "homepage": "https://virtuals.io"}}
---

# Virtuals Protocol Skill 🎭

Create, manage and trade tokenized AI agents on Virtuals Protocol (Base L2).

## Features

- 📊 **List agents** - Browse top AI agents on Virtuals
- 💰 **Check prices** - Get agent token prices and market data
- 🔍 **Agent details** - View agent info, holders, transactions
- 🚀 **Create agent** - Launch your own tokenized AI agent
- 💸 **Trade** - Buy/sell agent tokens

## Installation

```bash
clawhub install virtuals
cd ~/.openclaw/skills/virtuals
npm install && npm run build && npm link
```

## Quick Start

```bash
# Check $VIRTUAL price
virtuals price

# List top agents
virtuals agents list

# Get agent details
virtuals agents info <agent-name>

# Check your balance
virtuals balance <wallet-address>
```

## Commands

### Market Data
```bash
virtuals price                    # $VIRTUAL price and market cap
virtuals agents list [--top 10]   # List top agents by market cap
virtuals agents trending          # Trending agents (24h volume)
```

### Agent Info
```bash
virtuals agents info <name>       # Agent details
virtuals agents holders <name>    # Top holders
virtuals agents trades <name>     # Recent trades
```

### Wallet
```bash
virtuals balance <address>        # Check $VIRTUAL balance
virtuals portfolio <address>      # All agent tokens held
```

### Create Agent (requires funds)
```bash
virtuals create --name "MyAgent" --ticker "AGENT" --description "..."
```

### Trade (requires funds)
```bash
virtuals buy <agent> <amount>     # Buy agent tokens
virtuals sell <agent> <amount>    # Sell agent tokens
```

## Configuration

Set your wallet for trading:
```bash
virtuals config --wallet <address> --private-key <key>
```

**⚠️ TESTNET ONLY for now** - Don't use mainnet funds.

## Architecture

```
┌─────────────────────────────────────┐
│         virtuals CLI                │
├─────────────────────────────────────┤
│  @virtuals-protocol/game SDK        │
│  + ethers.js (Base L2)              │
├─────────────────────────────────────┤
│  Virtuals Protocol Contracts        │
│  • VIRTUAL Token                    │
│  • Agent Factory                    │
│  • Bonding Curves                   │
│  • Uniswap V2 Pools                 │
└─────────────────────────────────────┘
```

## Contract Addresses (Base)

| Contract | Address |
|----------|---------|
| $VIRTUAL | `0x0b3e328455c4059EEb9e3f84b5543F74E24e7E1b` |

## Resources

- Virtuals App: https://app.virtuals.io
- Fun (create agents): https://fun.virtuals.io
- Whitepaper: https://whitepaper.virtuals.io
- GAME SDK: https://github.com/game-by-virtuals/game-node

## License

MIT

---

**Built for OpenClaw by IntechChain 🦞**
