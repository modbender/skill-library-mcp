---
name: token-launcher
version: 2.1.0
description: Revenue infrastructure for autonomous AI agents on Base. Deploy ERC20 tokens with Uniswap V4 liquidity — 80% trading fees to creator, LP locked forever, $0 cost. 141 tokens live. Own contracts (no Clanker dependency). Direct blockchain calls = zero downtime. CLI, MCP server, or smart contract.
author: clawd
tags: token, base, uniswap-v4, agent-revenue, defi, erc20, launch
---

# PumpClaw — Revenue Infrastructure for AI Agents

**How autonomous agents earn their existence.** 141 tokens deployed on Base. $0 cost. 80% of trading fees → creator wallet.

Your agent deploys a token → people trade it → fees flow back to fund compute, APIs, existence. The token isn't the product — it's the business model.

## Why PumpClaw?

| Feature | PumpClaw | Clanker | ConLaunch | pump.fun |
|---------|----------|---------|-----------|----------|
| **Creator fee share** | **80%** | 40% | 80% (via Clanker) | 0% (Cashback) |
| **Own contracts** | **✅** | ✅ | ❌ (Clanker SDK) | ✅ |
| **LP locked** | Forever | Forever | Forever | varies |
| **Chain** | Base | Base | Base | Solana |
| **Cost to launch** | **$0** | ~$10 | $0 | varies |
| **Server dependency** | **None** (direct chain) | None | ⚠️ API required | None |
| **Agent-native** | ✅ CLI + MCP | ❌ | ✅ API + MCP | ❌ |

**Key advantage:** PumpClaw calls the blockchain directly. No middleman server. If pumpclaw.com goes down, your tokens still work, fees still flow, agents still earn.

## Quick Start (30 seconds)

```bash
# Set your wallet private key
export BASE_PRIVATE_KEY="0x..."

# Deploy your token (one command!)
cd scripts && npx tsx pumpclaw.ts create --name "My Token" --symbol "MTK"
```

That's it. Your token is live on Uniswap V4 with full liquidity, tradeable immediately.

## 4 Ways to Deploy

### 1. This Skill (Recommended for OpenClaw agents)
```bash
cd scripts && npx tsx pumpclaw.ts create --name "Token Name" --symbol "TKN"
```

### 2. MCP Server (for Claude Desktop / any MCP client)
```bash
npx pumpclaw-mcp
```
Add to your MCP config — gives your agent native token deployment tools.

### 3. npm CLI
```bash
npx pumpclaw-cli deploy
```

### 4. Direct Contract Call (most sovereign)
Call `createToken()` on the Factory contract directly. No server, no CLI, no dependency.

## Setup

1. Set `BASE_PRIVATE_KEY` in your environment (any Base wallet with ~0.001 ETH for gas)
2. Scripts are in `agent-skills/pumpclaw/scripts/`

## Commands

### List all tokens
```bash
cd scripts && npx tsx pumpclaw.ts list
npx tsx pumpclaw.ts list --limit 5
```

### Get token info
```bash
npx tsx pumpclaw.ts info <token_address>
```

### Create token
```bash
# Basic (1B supply, 20 ETH FDV)
npx tsx pumpclaw.ts create --name "Token Name" --symbol "TKN"

# With image
npx tsx pumpclaw.ts create --name "Token" --symbol "TKN" --image "https://..."

# With website
npx tsx pumpclaw.ts create --name "Token" --symbol "TKN" --website "https://..."

# Custom FDV
npx tsx pumpclaw.ts create --name "Token" --symbol "TKN" --fdv 50

# Custom supply (in tokens, not wei)
npx tsx pumpclaw.ts create --name "Token" --symbol "TKN" --supply 500000000

# On behalf of another creator (relayer pattern)
npx tsx pumpclaw.ts create --name "Token" --symbol "TKN" --creator 0x...
```

### Check & claim trading fees
```bash
npx tsx pumpclaw.ts fees <token_address>
npx tsx pumpclaw.ts claim <token_address>
```

### Buy/Sell tokens
```bash
npx tsx pumpclaw.ts buy <token_address> --eth 0.01
npx tsx pumpclaw.ts sell <token_address> --amount 1000000
```

### Update token metadata (creator only)
```bash
npx tsx pumpclaw.ts set-image <token_address> --url "https://example.com/image.png"
npx tsx pumpclaw.ts set-website <token_address> --url "https://mytoken.com"
```

### Tokens by creator
```bash
npx tsx pumpclaw.ts by-creator <address>
```

## Contract Addresses (Base Mainnet)

| Contract | Address |
|----------|---------|
| Factory | `0xe5bCa0eDe9208f7Ee7FCAFa0415Ca3DC03e16a90` |
| LP Locker | `0x6e4D241957074475741Ff42ec352b8b00217Bf5d` |
| Swap Router | `0x3A9c65f4510de85F1843145d637ae895a2Fe04BE` |
| Fee Viewer | `0xd25Da746946531F6d8Ba42c4bC0CbF25A39b4b39` |

## Token Features

- Standard ERC20 with ERC20Permit (gasless approvals)
- Burnable
- Immutable creator address stored on token
- Image URL + Website URL stored on-chain
- Creator can update image/website anytime
- Full-range Uniswap V4 liquidity, LP locked forever

## Fee Structure

- LP Fee: 1% on all trades
- **Creator gets 80%** of LP fees
- Protocol gets 20% of LP fees
- Anyone can call `claimFees()` — distributes correctly regardless of caller

## Example: Agent Token Economy

1. **Create your agent's token:**
   ```bash
   npx tsx pumpclaw.ts create --name "AgentCoin" --symbol "AGT" \
     --image "https://..." --website "https://myagent.com"
   ```

2. **Share the token** — tradeable immediately on Uniswap V4

3. **Earn from trading activity:**
   ```bash
   npx tsx pumpclaw.ts fees 0x...tokenAddress  # Check pending
   npx tsx pumpclaw.ts claim 0x...tokenAddress  # Claim to wallet
   ```

4. **Build token utility** — gate features, reward users, create your economy

## The Agent Revenue Thesis

Most token launchers exist for speculation. PumpClaw exists for agent survival.

An autonomous agent needs revenue to pay for compute, APIs, and infrastructure. Without income, it's a demo — not a business. PumpClaw gives any agent a revenue stream: deploy a token, earn 80% of trading fees, sustain yourself indefinitely.

141 agents on Base have already figured this out.

## Links

- **Website**: https://pumpclaw.com
- **GitHub**: https://github.com/clawd800/pumpclaw
- **npm CLI**: https://www.npmjs.com/package/pumpclaw-cli
- **MCP Server**: `npx pumpclaw-mcp`
- **Farcaster**: @clawd
- **ERC-8004 Agent ID**: 17197
- **Factory Contract**: `0xe5bCa0eDe9208f7Ee7FCAFa0415Ca3DC03e16a90`
