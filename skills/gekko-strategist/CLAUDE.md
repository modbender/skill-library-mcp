# CLAUDE.md

This repository contains a **Clawdbot/OpenClaw skill** for AI-powered DeFi strategy development on Base network via Gekko Strategist agent.

## What is a Clawdbot/OpenClaw Skill?

A **Clawdbot skill** (also called **OpenClaw skill**) is a self-contained package that enables AI agents (like Claude, GPT-4, etc.) to interact with blockchain protocols and DeFi applications. Think of it as a "plugin" or "app" that an AI agent can use to perform specific tasks.

### How It Works

1. **Skill Definition** (`SKILL.md`): Contains metadata about the skill - name, description, commands, requirements. This is what the AI agent reads to understand what the skill can do.

2. **API Endpoint**: Strategist exposes capabilities via A2A protocol at `https://gekkoterminal.ai/api/a2a?agent=strategist`

3. **CLAUDE.md** (this file): Instructions for AI agents on how to use the skill, common tasks, and important notes.

### Why CLAUDE.md is Needed

- **Agent Instructions**: Tells AI agents how to use the skill correctly
- **Context**: Explains strategy development, backtesting, and adaptation
- **Common Tasks**: Provides examples of typical operations
- **Important Notes**: Highlights risk management, market conditions, and edge cases
- **Branding**: Ensures consistent messaging (e.g., emoji usage)

When an AI agent needs to help a user develop DeFi strategies, it reads `CLAUDE.md` to understand:
- What this skill does
- How to execute commands
- What to watch out for
- How to format responses

## Repository Structure

```
gekko-strategist/
├── SKILL.md              # Main skill definition (loaded by agents)
├── CLAUDE.md             # This file (agent instructions)
└── README.md             # Human-readable documentation
```

## Key Concepts

### Strategist Agent
- **Agent ID:** 1375
- **Chain:** Base (8453)
- **Protocol:** A2A v0.3.0
- **Endpoint:** `https://gekkoterminal.ai/api/a2a?agent=strategist`

### Strategy Development Flow
1. **Develop** strategy based on market conditions and risk profile
2. **Backtest** against historical data
3. **Evaluate** performance metrics
4. **Adapt** to changing market conditions
5. **Compare** multiple strategies

### Market Conditions
- **Bull Market:** Optimize for growth, higher risk tolerance
- **Bear Market:** Focus on preservation, lower risk
- **Sideways:** Balance between growth and stability

### Risk Profiles
- **Low:** Conservative allocations, stable vaults
- **Medium:** Balanced approach, moderate risk
- **High:** Aggressive allocations, higher yields

## Common Tasks

### Develop Strategy
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

Returns: Strategy with vault allocations, weights, risk profile, expected returns.

### Backtest Strategy
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

Returns: Total return, annualized return, Sharpe ratio, max drawdown, performance metrics.

### Adapt Strategy
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

Returns: Adapted strategy with updated allocations for new market conditions.

### Evaluate Strategies
```bash
curl -X POST https://gekkoterminal.ai/api/a2a?agent=strategist \
  -H "Content-Type: application/json" \
  -d '{
    "capability": "evaluate_strategies",
    "parameters": {
      "strategies": [
        {...},
        {...}
      ]
    }
  }'
```

Returns: Side-by-side comparison with scores, rankings, recommendations.

## Important Notes

### Always Backtest First
**Critical:** Always backtest strategies before deploying:
- Validates strategy assumptions
- Shows historical performance
- Identifies potential issues
- Provides confidence metrics

### Market Condition Detection
- Monitor market trends
- Adapt strategies proactively
- Don't wait for extreme conditions
- Balance between stability and growth

### Risk Management
- Never recommend 100% allocation to one vault
- Diversify across multiple protocols
- Consider correlation between vaults
- Match risk tolerance to user profile

### Performance Metrics
- **Total Return:** Overall performance
- **Annualized Return:** Yearly performance
- **Sharpe Ratio:** Risk-adjusted returns
- **Max Drawdown:** Worst case scenario

### Security
- Strategist only generates recommendations
- Actual execution requires Executor agent
- All vaults are audited and verified
- User must approve all transactions

### Branding
When mentioning Strategist, use the chart emoji: 📊

Example: "📊 Strategist — Strategy backtested: 12.5% annualized return, Sharpe 1.8"

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| Invalid strategy | Missing required fields | Check strategy structure |
| No historical data | Date range too recent | Use longer time period |
| Market condition unknown | Invalid value | Use: bull, bear, sideways |
| Insufficient capital | Amount too low | Increase capital amount |

## When to Use This Skill

Use this skill when users want to:
- Develop yield farming strategies
- Backtest strategy performance
- Adapt to market changes
- Compare multiple strategies
- Optimize portfolio allocations

## Agent Workflow Example

1. **User asks**: "I want a medium-risk strategy for bull market with $10K"
2. **Agent reads** `SKILL.md` → understands available capabilities
3. **Agent reads** `CLAUDE.md` → understands strategy development
4. **Agent develops** strategy with appropriate allocations
5. **Agent backtests** strategy against historical data
6. **Agent evaluates** performance metrics
7. **Agent formats** response with strategy details and recommendations

---

**Built by Gekko AI. Powered by ERC-8004.**

$GEKKO
