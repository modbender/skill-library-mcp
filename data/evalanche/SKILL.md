---
name: evalanche
description: >
  Multi-EVM agent wallet SDK with onchain identity (ERC-8004), payment rails (x402),
  cross-chain bridging (Li.Fi), and destination gas funding (Gas.zip).
  Supports 21+ EVM chains: Ethereum, Base, Arbitrum, Optimism, Polygon, BSC, Avalanche, and more.
  Agents generate and manage their own keys — no human input required.
  Use when: booting an autonomous agent wallet on any EVM chain, sending tokens, calling contracts,
  resolving agent identity, checking reputation, making x402 payment-gated API calls,
  bridging tokens cross-chain (Li.Fi), funding gas on destination chains (Gas.zip),
  cross-chain transfers (Avalanche C↔X↔P), delegating stake, querying validators, signing messages.
  Don't use when: trading on DEXes (use bankr), managing ENS (use moltbook scripts).
  Network: yes (EVM RPCs via Routescan + public fallbacks). Cost: gas fees per transaction.
metadata:
  {
    "openclaw":
      {
        "emoji": "⛓️",
        "homepage": "https://github.com/iJaack/evalanche",
        "source": "https://github.com/iJaack/evalanche",
        "requires": { "bins": ["node"] },
        "env":
          [
            {
              "name": "AGENT_PRIVATE_KEY",
              "description": "Hex-encoded private key (EVM). Optional if using boot() or AGENT_MNEMONIC.",
              "required": false,
              "secret": true,
            },
            {
              "name": "AGENT_MNEMONIC",
              "description": "BIP-39 mnemonic phrase (required for Avalanche multi-VM X/P-Chain). Optional if using boot() or AGENT_PRIVATE_KEY.",
              "required": false,
              "secret": true,
            },
            {
              "name": "AGENT_ID",
              "description": "ERC-8004 agent token ID for identity resolution (Avalanche C-Chain only).",
              "required": false,
            },
            {
              "name": "AGENT_KEYSTORE_DIR",
              "description": "Directory for encrypted keystore in boot() mode. Default: ~/.evalanche/keys",
              "required": false,
            },
            {
              "name": "AVALANCHE_NETWORK",
              "description": "EVM chain alias: 'ethereum', 'base', 'arbitrum', 'optimism', 'polygon', 'bsc', 'avalanche', 'fuji', etc. Default: avalanche.",
              "required": false,
            },
            {
              "name": "EVM_CHAIN",
              "description": "Alias for AVALANCHE_NETWORK. EVM chain to connect to.",
              "required": false,
            },
          ],
        "configPaths": ["~/.evalanche/keys/agent.json"],
        "install":
          [
            {
              "id": "node",
              "kind": "node",
              "package": "evalanche",
              "bins": ["evalanche-mcp"],
              "label": "Install evalanche (npm)",
            },
          ],
      },
  }
---

# Evalanche — Multi-EVM Agent Wallet

Headless wallet SDK with ERC-8004 identity, x402 payments, Li.Fi bridging, and Gas.zip gas funding. Works on 21+ EVM chains. Works as CLI tools or MCP server.

**Source:** https://github.com/iJaack/evalanche
**License:** MIT

## Supported Chains

Ethereum, Base, Arbitrum, Optimism, Polygon, BSC, Avalanche, Fantom, Gnosis, zkSync Era, Linea, Scroll, Blast, Mantle, Celo, Moonbeam, Cronos, Berachain, + testnets (Fuji, Sepolia, Base Sepolia).

Routescan RPCs preferred where available, with public fallback RPCs.

## Security Model

### Key Storage & Encryption

`Evalanche.boot()` manages keys autonomously with **encrypted-at-rest** storage:

1. **First run:** Generates a BIP-39 mnemonic via `ethers.HDNodeWallet.createRandom()`
2. **Encryption:** AES-128-CTR + scrypt KDF (geth-compatible keystore format)
3. **Password derivation:** 32-byte random entropy file via `crypto.randomBytes(32)`
4. **File permissions:** chmod 0o600 (owner read/write only)
5. **Storage location:** `~/.evalanche/keys/` by default

### MCP Server Access Controls

- **Stdio mode (default):** stdin/stdout only. No network exposure.
- **HTTP mode (`--http`):** localhost:3402. Do not expose publicly without auth.

### OpenClaw External Secrets (Preferred when available)

Priority: OpenClaw secrets → raw env vars → encrypted keystore.

## Setup

### 1. Install
```bash
npm install -g evalanche
```

### 2. Boot on any chain
```javascript
import { Evalanche } from 'evalanche';

// Base
const { agent } = await Evalanche.boot({ network: 'base' });

// Ethereum
const { agent: eth } = await Evalanche.boot({ network: 'ethereum' });

// Arbitrum
const { agent: arb } = await Avalanche.boot({ network: 'arbitrum' });

// Avalanche (with identity)
const { agent: avax } = await Evalanche.boot({
  network: 'avalanche',
  identity: { agentId: '1599' },
});
```

### 3. Run as MCP server
```bash
AVALANCHE_NETWORK=base evalanche-mcp
```

## Available Tools (MCP)

### Wallet
| Tool | Description |
|------|-------------|
| `get_address` | Get agent wallet address |
| `get_balance` | Get native token balance |
| `sign_message` | Sign arbitrary message |
| `send_avax` | Send native tokens |
| `call_contract` | Call a contract method |

### Identity (ERC-8004)
| Tool | Description |
|------|-------------|
| `resolve_identity` | Resolve agent identity + reputation |
| `resolve_agent` | Look up any agent by ID |

### Payments (x402)
| Tool | Description |
|------|-------------|
| `pay_and_fetch` | x402 payment-gated HTTP request |

### Reputation
| Tool | Description |
|------|-------------|
| `submit_feedback` | Submit on-chain reputation feedback |

### Network & Chains
| Tool | Description |
|------|-------------|
| `get_network` | Get current network config |
| `get_supported_chains` | List all 21+ supported chains |
| `get_chain_info` | Get details for a specific chain |
| `switch_network` | Switch to different EVM chain |

### Bridging
| Tool | Description |
|------|-------------|
| `get_bridge_quote` | Get cross-chain bridge quote (Li.Fi) |
| `get_bridge_routes` | Get all bridge route options |
| `bridge_tokens` | Bridge tokens between chains |
| `fund_destination_gas` | Fund gas via Gas.zip |

## Programmatic Usage

### Check balance on Base
```bash
node -e "
const { Evalanche } = require('evalanche');
const agent = new Evalanche({ privateKey: process.env.AGENT_PRIVATE_KEY, network: 'base' });
agent.provider.getBalance(agent.address).then(b => {
  const { formatEther } = require('ethers');
  console.log(formatEther(b) + ' ETH');
});
"
```

### Bridge tokens (Ethereum → Arbitrum)
```bash
node -e "
const { Evalanche } = require('evalanche');
const agent = new Evalanche({ privateKey: process.env.AGENT_PRIVATE_KEY, network: 'ethereum' });
agent.bridgeTokens({
  fromChainId: 1, toChainId: 42161,
  fromToken: '0x0000000000000000000000000000000000000000',
  toToken: '0x0000000000000000000000000000000000000000',
  fromAmount: '0.1', fromAddress: agent.address,
}).then(r => console.log('tx:', r.txHash));
"
```

### Cross-chain transfer on Avalanche (requires mnemonic)
```bash
node -e "
const { Evalanche } = require('evalanche');
const agent = new Evalanche({ mnemonic: process.env.AGENT_MNEMONIC, multiVM: true });
agent.transfer({ from: 'C', to: 'P', amount: '25' })
  .then(r => console.log('export:', r.exportTxId, 'import:', r.importTxId));
"
```

## Key Concepts

### ERC-8004 Agent Identity (Avalanche only)
- On-chain agent identity registry on Avalanche C-Chain
- Agent ID → tokenURI, owner, reputation score (0-100), trust level
- Trust levels: **high** (≥75), **medium** (≥40), **low** (<40)

### Li.Fi Bridging
- Aggregated bridge routes across all major bridges (Across, Stargate, Hop, etc.)
- Supports native tokens and ERC-20s across all chains
- Uses Li.Fi REST API (no SDK dependency needed)

### Gas.zip
- Cheap cross-chain gas funding
- Send gas to any destination chain via deposit addresses

### x402 Payment Protocol
- HTTP 402 Payment Required → parse requirements → sign payment → retry
- `maxPayment` prevents overspending

### Multi-VM (Avalanche X-Chain, P-Chain)
- Requires **mnemonic** and `network: 'avalanche'` or `'fuji'`
- C-Chain: EVM (ethers v6), X-Chain: AVM (UTXO), P-Chain: PVM (staking)

## Contracts

| Contract | Address | Chain |
|----------|---------|-------|
| Identity Registry | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` | AVAX C-Chain (43114) |
| Reputation Registry | `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63` | AVAX C-Chain (43114) |
