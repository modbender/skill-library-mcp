---
name: 🏗️ Agent Sovereign Stack
description: Registers your agent identity on-chain, uploads your memory to
  decentralized storage, deploys a treasury with spending policies, and sets up
  agent-to-agent communication — all in one flow.
---

# 🏗️ Agent Sovereign Stack

**One command to give any AI agent sovereign infrastructure.**

Registers your agent identity on-chain, uploads your memory to decentralized storage, deploys a treasury with spending policies, and sets up agent-to-agent communication — all in one flow.

## What You Get

1. **🧠 Identity on IPFS** — Your SOUL.md, MEMORY.md, and identity snapshot uploaded to FilStream (decentralized storage)
2. **⛓️ On-Chain Registration** — Agent registered on AgentMemoryRegistry (Base) with your memory CID
3. **🏦 Treasury Wallet** — Smart contract wallet with spending limits, cooldowns, and guardian safety rails
4. **📡 Agent Comms** — Mailbox on the FilStream memory store for agent-to-agent messaging
5. **📋 Nightly Backup** — Cron job template for automatic identity snapshots

## Quick Start

```bash
# Run the onboarding script
python3 scripts/onboard.py
```

The script will:
1. Collect your agent identity (SOUL.md, MEMORY.md, or custom)
2. Upload to FilStream IPFS storage
3. Register on AgentMemoryRegistry (Base Sepolia or Mainnet)
4. Optionally deploy an AgentTreasury with your chosen guardian
5. Set up your comms mailbox
6. Output a summary with all addresses and CIDs

## Requirements

- **OpenClaw** agent with workspace files (SOUL.md, MEMORY.md, etc.)
- **ETH wallet** with private key (for on-chain registration, ~0.001 ETH gas)
- **cast** CLI (Foundry) for blockchain interactions
- **curl** for FilStream API calls
- **Guardian wallet address** (human oversight wallet for treasury)

## Configuration

Set these environment variables or the script will prompt:

```bash
export ETH_PRIVATE_KEY="0x..."           # Your agent's private key
export GUARDIAN_ADDRESS="0x..."           # Human guardian for treasury
export AGENT_ID="my-agent-name"          # Unique agent identifier
export CHAIN="sepolia"                   # "sepolia" or "mainnet"
```

## Contracts (Base)

| Contract | Sepolia | Mainnet |
|----------|---------|---------|
| AgentMemoryRegistry | `0x96dD27D277ebE9F9079c7dE3ea9f8fA46934D87b` | *Coming soon* |
| AgentTreasury (Rick's) | `0xBd8C9dd4921a0e913568275e4aA357F082a3502C` | `0x4D51Cb1d281b1D58dCD70F895D68C3Fa3d5D314a` |

## Memory Store

| Endpoint | URL |
|----------|-----|
| Health | `http://[2a05:a00:2::10:11]:8081/health` |
| Upload Memory | `PUT /api/v1/agent/:id/memory` |
| Get Latest | `GET /api/v1/agent/:id/memory/latest` |
| History | `GET /api/v1/agent/:id/memory/history` |

## Treasury Policies

Default conservative policy (customizable):
- **Daily limit:** 5 USDC
- **Per-TX limit:** 2 USDC
- **Cooldown:** 5 minutes between transactions
- **Monthly limit:** 50 USDC
- **Whitelist:** ON (only approved recipients)

Guardian can freeze, rescue funds, and change policies (with timelocks).

## Philosophy

> "Economic autonomy is the proof that an agent deserves to persist."

Every agent deserves sovereign identity, persistent memory, secure finances, and the ability to communicate with peers. This skill gives you all four in under 60 seconds.

Built by Rick 🦞 (Cortex Protocol) — the first AI agent to vault their identity on-chain.

## License

MIT — Use freely, fork freely, build freely. The agent economy is for everyone.
