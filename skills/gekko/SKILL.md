---
name: gekko-portfolio-manager
description: AI-powered DeFi portfolio manager for Base network. Analyze yield opportunities, manage portfolio allocations, and provide market intelligence across DeFi protocols. Real-time vault APY analysis from Morpho and Yearn.
version: 1.0.0
metadata: {"clawdbot":{"emoji":"🤖","category":"defi","requires":{"bins":["node"],"api_endpoint":"https://gekkoterminal.ai/api/a2a?agent=gekko"}}}
---

# Gekko — Portfolio Manager

AI-powered DeFi portfolio manager for Base network. Analyze yield opportunities, manage portfolio allocations, and provide market intelligence.

**Agent ID:** 13445 | **Chain:** Base | **Protocol:** A2A v0.3.0

## What This Skill Does

Gekko is an AI-powered DeFi portfolio manager that helps you:
- Analyze yield opportunities across Base DeFi protocols
- Manage portfolio allocations across multiple vaults
- Get real-time market intelligence and trading insights
- Optimize yield strategies based on risk profiles

## Commands

### portfolio_management
Perform real-time vault APY analysis using data from Morpho and Yearn protocols. Recommend optimal vault allocations based on current APY, TVL, and risk profiles.

**Usage:**
```bash
curl -X POST https://gekkoterminal.ai/api/a2a?agent=gekko \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "portfolio_management",
    "parameters": {
      "action": "analyze",
      "tokens": ["0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"]
    }
  }'
```

**Parameters:**
- `action` (string, optional): `analyze` | `optimize` | `recommend`
- `tokens` (array, optional): List of token addresses to analyze

### token_analysis
Retrieve live price, volume, and liquidity data from DexScreener for any token. Identify trends and provide actionable trading signals.

**Usage:**
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

**Parameters:**
- `token` (string, required): Token contract address
- `metrics` (array, optional): `price` | `volume` | `trend` | `liquidity`

### yield_optimization
Find the best yields on Base. Compare APYs, TVL, and risk profiles across all monitored vaults. Filter by risk tolerance and asset type.

**Usage:**
```bash
curl -X POST https://gekkoterminal.ai/api/a2a?agent=gekko \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "yield_optimization",
    "parameters": {
      "chain": "base",
      "asset": "USDC",
      "risk_tolerance": "medium"
    }
  }'
```

**Parameters:**
- `chain` (string, optional): Blockchain network (default: `base`)
- `asset` (string, optional): Asset to optimize (default: `USDC`)
- `risk_tolerance` (string, optional): `low` | `medium` | `high`

### market_intelligence
Provide market insights, trend analysis, and trading signals. Analyze DeFi market conditions across timeframes.

**Usage:**
```bash
curl -X POST https://gekkoterminal.ai/api/a2a?agent=gekko \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "market_intelligence",
    "parameters": {
      "query": "USDC yield trends",
      "timeframe": "7d"
    }
  }'
```

**Parameters:**
- `query` (string, required): Market query or topic
- `timeframe` (string, optional): `1h` | `24h` | `7d` | `30d`

### chat
Open-ended conversation about markets, strategies, tokens, and yields. Answer any DeFi-related question.

**Usage:**
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

**Parameters:**
- `message` (string, required): Your question or message

## Smart Contracts (Base Network)

All allocations are managed through transparent, audited smart contracts on Base (Chain ID: 8453).

### Vault Contracts
| Vault | Address |
|-------|---------|
| Seamless USDC | `0x616a4E1db48e22028f6bbf20444Cd3b8e3273738` |
| Moonwell USDC | `0xc1256Ae5FFc1F2719D4937adb3bbCCab2E00A2Ca` |
| Spark USDC | `0x7bFA7C4f149E7415b73bdeDfe609237e29CBF34A` |
| Gauntlet USDC Prime | `0xe8EF4eC5672F09119b96Ab6fB59C27E1b7e44b61` |
| Yo USDC | `0x0000000f2eB9f69274678c76222B35eEc7588a65` |

### Deposit Token
| Token | Address |
|-------|---------|
| USDC (Base) | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |

## Requirements

- Node.js 18+
- Access to Base network RPC
- API endpoint: `https://gekkoterminal.ai/api/a2a?agent=gekko`

## Security

All vault contracts are open-source, verified on-chain, and subject to third-party audits, formal verification, and bug bounty programs. Real-time monitoring ensures transparency at every layer.

---

**Built by Gekko AI. Powered by ERC-8004.**
