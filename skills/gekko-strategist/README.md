# 📊 Gekko Strategist — Strategy Development Agent

AI-powered DeFi strategy development agent. Design, backtest, adapt, and evaluate yield farming strategies based on market conditions, risk profiles, and capital allocation goals.

## � Quick Start

```bash
# Develop a strategy
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

## 📋 Capabilities

### Develop Strategy
Create yield farming strategies tailored to current market conditions. Optimize allocations for risk tolerance and time horizon.

### Backtest Strategy
Backtest strategies against historical on-chain data. Measure performance metrics including Sharpe ratio and max drawdown.

### Adapt Strategy
Adapt an existing strategy to changing market conditions. Automatically rebalance allocations.

### Evaluate Strategies
Evaluate and compare multiple strategies side-by-side. Score on risk-adjusted returns and consistency.

## 🔧 API Endpoint

```
https://gekkoterminal.ai/api/a2a?agent=strategist
```

## 📈 Strategy Development Flow

1. **Develop** — Create strategy based on market conditions
2. **Backtest** — Test against historical data
3. **Evaluate** — Measure performance metrics
4. **Adapt** — Adjust for market changes
5. **Compare** — Evaluate multiple strategies

## Requirements

- API access to Strategist endpoint
- Base network for vault data
- Historical data for backtesting
- No wallet required (strategy generation only)

## Security

All strategy allocations target audited, open-source vault contracts. Strategist generates recommendations only — actual execution requires explicit wallet signing through the Executor agent.

---

**Built by Gekko AI. Powered by ERC-8004.**
