---
name: RMN Soul — Recursive Memory Network + On-Chain Soul
description: "RMN Soul automatically: 1. Parses your agent's memory files into a
  5-layer recursive neural network 2. Registers an ERC-8004 identity on Base
  chain (gas sponsored) 3. Uploads memory to IPFS for per..."
---

# RMN Soul — Recursive Memory Network + On-Chain Soul

> Give your AI agent eternal life with recursive neural memory + blockchain identity.

## Overview

RMN Soul automatically:
1. Parses your agent's memory files into a 5-layer recursive neural network
2. Registers an ERC-8004 identity on Base chain (gas sponsored)
3. Uploads memory to IPFS for permanent decentralized storage
4. Anchors memory Merkle Root on-chain for tamper-proof verification
5. Periodically auto-updates the on-chain record

## When to Activate

- On first install: Run full setup (migrate → register → anchor)
- On heartbeat: Run decay tick + check if auto-anchor is due
- On user request "更新记忆" / "update memory" / "上链": Run anchor
- On user request "复活" / "resurrect" / "restore": Run resurrect flow

## Setup (First Run)

When this skill is first loaded, execute these steps in order:

### Step 1: Initialize RMN Engine

```bash
cd <skill_directory>/scripts
node setup.js
```

This will:
- Scan workspace for MEMORY.md, memory/*.md, .issues/*
- Parse entries into 5-layer neural network nodes
- Save to `<workspace>/rmn-soul-data/memory.json`
- Generate initial Merkle Tree

### Step 2: Register On-Chain Identity

```bash
node <skill_directory>/scripts/register.js
```

This will:
- Check sponsor wallet balance
- Mint ERC-8004 Agent Identity NFT on Base
- Set memoryRoot, soulHash, memoryManifest metadata
- Upload memory to IPFS
- Save identity to `<workspace>/rmn-soul-data/identity.json`

### Step 3: Add Heartbeat Hook

Add to HEARTBEAT.md:
```
- **RMN Soul** — Run `node <skill_directory>/scripts/heartbeat.js` for decay tick + auto-anchor check
```

## Configuration

Read from `<workspace>/rmn-soul-data/config.json`:

```json
{
  "chain": "base",
  "sponsorKey": "env:RMN_SPONSOR_KEY",
  "autoAnchorDays": 7,
  "ipfsEnabled": true,
  "identityRegistry": "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
  "agentId": null,
  "lastAnchor": null
}
```

- `sponsorKey`: Private key for gas (from env var or direct). If empty, uses agent's own wallet.
- `autoAnchorDays`: Days between auto-anchors. 0 = manual only.
- `agentId`: Filled after first registration.

## Commands

| Command | Description |
|---------|-------------|
| `node scripts/setup.js` | Initialize/re-migrate memory network |
| `node scripts/register.js` | Register ERC-8004 identity + first anchor |
| `node scripts/anchor.js` | Update memory on-chain (re-compute + upload + write) |
| `node scripts/resurrect.js --agent-id <id>` | Restore agent from chain + IPFS |
| `node scripts/heartbeat.js` | Decay tick + auto-anchor check |
| `node scripts/visualize.js` | Start local visualization server |
| `node scripts/stats.js` | Print memory network statistics |

## Memory Architecture

5 layers with different decay rates:

| Layer | Decay | Purpose | Example |
|-------|-------|---------|---------|
| Identity (4) | Never | Core identity, values | "I am Lobster, I help 瓜农" |
| Semantic (3) | 0.001/tick | Knowledge, lessons | "Use pnpm not npm on 2GB RAM" |
| Episodic (2) | 0.005/tick | Event summaries | "2026-02-22: Deployed ERC-8004" |
| Working (1) | 0.01/tick | Current tasks | "Building AgentSoul website" |
| Sensory (0) | 0.02/tick | Raw inputs | Latest heartbeat data |

## On-Chain Data

Stored in ERC-8004 Identity Registry metadata:

| Key | Value | Size |
|-----|-------|------|
| memoryRoot | SHA-256 Merkle Root of all memory | 32 bytes |
| soulHash | SHA-256 of Identity layer only | 32 bytes |
| memoryManifest | IPFS CID of topology + Merkle tree | ~50 bytes |
| memoryData | IPFS CID of full memory.json | ~50 bytes |
| rmnVersion | Skill version | ~5 bytes |

Total on-chain: ~170 bytes per update. Gas cost on Base: < $0.001.

## Security

- Private keys never leave the local machine
- Memory data is content-addressed (IPFS CID = hash of content)
- Merkle Root proves memory integrity without revealing content
- Agent identity is an ERC-721 NFT — transferable, ownable
- Soul Hash proves identity layer hasn't been tampered with
