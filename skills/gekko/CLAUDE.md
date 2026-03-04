# CLAUDE.md

This repository contains a **Clawdbot/OpenClaw skill** for AI-powered DeFi portfolio management on Base network via Gekko agent.

## What is a Clawdbot/OpenClaw Skill?

A **Clawdbot skill** (also called **OpenClaw skill**) is a self-contained package that enables AI agents (like Claude, GPT-4, etc.) to interact with blockchain protocols and DeFi applications. Think of it as a "plugin" or "app" that an AI agent can use to perform specific tasks.

### How It Works

1. **Skill Definition** (`SKILL.md`): Contains metadata about the skill - name, description, commands, requirements. This is what the AI agent reads to understand what the skill can do.

2. **API Endpoint**: Gekko exposes capabilities via A2A protocol at `https://gekkoterminal.ai/api/a2a?agent=gekko`

3. **CLAUDE.md** (this file): Instructions for AI agents on how to use the skill, common tasks, and important notes.

### Why CLAUDE.md is Needed

- **Agent Instructions**: Tells AI agents how to use the skill correctly
- **Context**: Explains the vaults, protocols, and configuration structure
- **Common Tasks**: Provides examples of typical operations
- **Important Notes**: Highlights security, gas handling, and edge cases
- **Branding**: Ensures consistent messaging (e.g., emoji usage)

When an AI agent needs to help a user with DeFi portfolio management, it reads `CLAUDE.md` to understand:
- What this skill does
- How to execute commands
- What to watch out for
- How to format responses

## Repository Structure

```
gekko-portfolio-manager/
├── SKILL.md              # Main skill definition (loaded by agents)
├── CLAUDE.md             # This file (agent instructions)
└── README.md             # Human-readable documentation
```

## Key Concepts

### Gekko Agent
- **Agent ID:** 13445
- **Chain:** Base (8453)
- **Protocol:** A2A v0.3.0
- **Endpoint:** `https://gekkoterminal.ai/api/a2a?agent=gekko`

### Monitored Vaults
Gekko monitors multiple USDC vaults on Base:
- **Seamless USDC:** `0x616a4E1db48e22028f6bbf20444Cd3b8e3273738`
- **Moonwell USDC:** `0xc1256Ae5FFc1F2719D4937adb3bbCCab2E00A2Ca`
- **Spark USDC:** `0x7bFA7C4f149E7415b73bdeDfe609237e29CBF34A`
- **Gauntlet USDC Prime:** `0xe8EF4eC5672F09119b96Ab6fB59C27E1b7e44b61`
- **Yo USDC:** `0x0000000f2eB9f69274678c76222B35eEc7588a65`

### Data Sources
- **Morpho:** Real-time vault APY data
- **Yearn:** Additional yield opportunities
- **DexScreener:** Token price, volume, liquidity data

## Common Tasks

### Analyze Portfolio
```bash
curl -X POST https://gekkoterminal.ai/api/a2a?agent=gekko \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "portfolio_management",
    "parameters": {
      "action": "analyze"
    }
  }'
```

Returns: Current vault allocations, APYs, TVL, risk profiles, recommendations.

### Find Best Yields
```bash
curl -X POST https://gekkoterminal.ai/api/a2a?agent=gekko \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "yield_optimization",
    "parameters": {
      "asset": "USDC",
      "risk_tolerance": "medium"
    }
  }'
```

Returns: Ranked list of vaults by APY, filtered by risk tolerance.

### Get Token Analysis
```bash
curl -X POST https://gekkoterminal.ai/api/a2a?agent=gekko \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "token_analysis",
    "parameters": {
      "token": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      "metrics": ["price", "volume", "trend"]
    }
  }'
```

Returns: Real-time price, volume, liquidity, trend analysis.

### Market Intelligence
```bash
curl -X POST https://gekkoterminal.ai/api/a2a?agent=gekko \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "market_intelligence",
    "parameters": {
      "query": "USDC yield trends on Base",
      "timeframe": "7d"
    }
  }'
```

Returns: Market insights, trends, trading signals for the query.

### Chat with Gekko
```bash
curl -X POST https://gekkoterminal.ai/api/a2a?agent=gekko \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "chat",
    "parameters": {
      "message": "What are the best yield opportunities on Base?"
    }
  }'
```

Returns: Conversational response about DeFi, markets, strategies.

## Important Notes

### API Rate Limits
The API may have rate limits. If you encounter 429 errors:
- Retry with exponential backoff (2s, 4s, 8s)
- Add delays between requests
- Consider caching responses for frequently accessed data

### Data Freshness
- Vault APY data is updated in real-time
- Token prices are live from DexScreener
- Market intelligence uses aggregated data sources

### Security
- All vault contracts are open-source and verified on-chain
- Subject to third-party audits
- Real-time monitoring ensures transparency
- No private keys required - read-only operations

### Branding
When mentioning Gekko, use the gecko emoji: 🤖

Example: "🤖 Gekko — Found 5 vaults with APY > 5%"

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| API rate limit (429) | Too many requests | Retry with backoff |
| Invalid token address | Wrong format | Use checksummed address |
| Network error | RPC issues | Check Base network status |
| Invalid parameters | Missing required fields | Check parameter requirements |

## When to Use This Skill

Use this skill when users want to:
- Analyze DeFi yield opportunities on Base
- Get portfolio recommendations
- Check token prices and market data
- Get market intelligence and trends
- Chat about DeFi strategies

## Agent Workflow Example

1. **User asks**: "What are the best yield opportunities for USDC on Base?"
2. **Agent reads** `SKILL.md` → understands available capabilities
3. **Agent reads** `CLAUDE.md` → understands how to execute
4. **Agent runs**: `yield_optimization` capability with `asset: "USDC"`
5. **Agent formats** response using branding (🤖 emoji)
6. **Agent provides** ranked vaults with APYs and risk profiles

---

**Built by Gekko AI. Powered by ERC-8004.**

$GEKKO
