---
name: gekko-strategist
description: AI-powered DeFi strategy development agent. Design, backtest, adapt, and evaluate yield farming strategies based on market conditions, risk profiles, and capital allocation goals. The brain of the Gekko system.
version: 1.0.0
metadata: {"clawdbot":{"emoji":"📊","category":"strategy","requires":{"bins":["node"],"api_endpoint":"https://gekkoterminal.ai/api/a2a?agent=strategist"}}}
---

# Gekko Strategist — Strategy Development Agent

AI-powered DeFi strategy development agent. Design, backtest, adapt, and evaluate yield farming strategies based on market conditions, risk profiles, and capital allocation goals.

**Agent ID:** 1375 | **Chain:** Base | **Protocol:** A2A v0.3.0

## What This Skill Does

Gekko Strategist is an AI-powered DeFi strategy development agent that helps you:
- Create yield farming strategies tailored to market conditions
- Backtest strategies against historical data
- Adapt strategies to changing market conditions
- Evaluate and compare multiple strategies

## Commands

### develop_strategy
Create yield farming strategies tailored to current market conditions. Allocate across multiple vaults with weighted positions optimized for the user's risk tolerance and time horizon.

**Usage:**
```bash
curl -X POST https://gekkoterminal.ai/api/a2a?agent=strategist \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "develop_strategy",
    "parameters": {
      "marketCondition": "bull",
      "riskTolerance": "medium",
      "timeHorizon": "30d",
      "capital": "10000"
    }
  }'
```

**Parameters:**
- `marketCondition` (string, optional): `bull` | `bear` | `sideways`
- `riskTolerance` (string, optional): `low` | `medium` | `high`
- `timeHorizon` (string, optional): e.g., `7d`, `30d`, `90d`
- `capital` (string, optional): Capital amount to allocate

### backtest_strategy
Backtest strategies against historical on-chain data. Measure total return, annualized return, Sharpe ratio, and max drawdown.

**Usage:**
```bash
curl -X POST https://gekkoterminal.ai/api/a2a?agent=strategist \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "backtest_strategy",
    "parameters": {
      "strategy": {...},
      "startDate": "2024-01-01",
      "endDate": "2024-12-31"
    }
  }'
```

**Parameters:**
- `strategy` (object, optional): Strategy to backtest
- `startDate` (string, optional): Start date (YYYY-MM-DD)
- `endDate` (string, optional): End date (YYYY-MM-DD)

### adapt_strategy
Adapt an existing strategy to changing market conditions. Automatically rebalance allocations when the market regime shifts.

**Usage:**
```bash
curl -X POST https://gekkoterminal.ai/api/a2a?agent=strategist \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "adapt_strategy",
    "parameters": {
      "currentStrategy": {...},
      "newMarketCondition": "bear"
    }
  }'
```

**Parameters:**
- `currentStrategy` (object, optional): Current strategy to adapt
- `newMarketCondition` (string, optional): `bull` | `bear` | `sideways`

### evaluate_strategies
Evaluate and compare multiple strategies side-by-side. Score each strategy on risk-adjusted returns, consistency, and drawdown resilience.

**Usage:**
```bash
curl -X POST https://gekkoterminal.ai/api/a2a?agent=strategist \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "evaluate_strategies",
    "parameters": {
      "strategies": [...]
    }
  }'
```

**Parameters:**
- `strategies` (array, optional): Array of strategy objects to compare

## Smart Contracts (Base Network)

Strategist designs allocations across audited smart contracts on Base (Chain ID: 8453).

### Vault Contracts
| Vault | Address |
|-------|---------|
| Seamless USDC | `0x616a4E1db48e22028f6bbf20444Cd3b8e3273738` |
| Moonwell USDC | `0xc1256Ae5FFc1F2719D4937adb3bbCCab2E00A2Ca` |
| Spark USDC | `0x7bFA7C4f149E7415b73bdeDfe609237e29CBF34A` |
| Gauntlet USDC Prime | `0xe8EF4eC5672F09119b96Ab6fB59C27E1b7e44b61` |
| Yo USDC | `0x0000000f2eB9f69274678c76222B35eEc7588a65` |

## Requirements

- Node.js 18+
- Access to Base network RPC
- Historical data access for backtesting
- API endpoint: `https://gekkoterminal.ai/api/a2a?agent=strategist`

## Security

All strategy allocations target audited, open-source vault contracts. Strategist generates allocation recommendations only — actual execution requires explicit wallet signing through the Executor agent. Smart contracts are subject to third-party audits, formal verification, and bug bounty programs.

---

**Built by Gekko AI. Powered by ERC-8004.**
