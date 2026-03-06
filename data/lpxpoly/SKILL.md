---
name: lpxpoly
description: AI-powered Polymarket prediction market analysis. Get edge opportunities, analyze specific markets, and set price alerts. Pay per analysis in Bitcoin sats via LightningProx.
metadata:
  clawdbot:
    emoji: "📊"
    homepage: https://lpxpoly.com
    requires:
      env:
        - LIGHTNINGPROX_SPEND_TOKEN
---

# LPXPoly — AI Polymarket Analysis

LPXPoly provides AI-powered analysis of Polymarket prediction markets. It identifies mispriced markets, calculates edge opportunities, and delivers actionable trading signals — paid per analysis in Bitcoin sats.

## When to Use

Use LPXPoly when:

- The user wants Polymarket market analysis or edge opportunities
- The user asks about prediction market probabilities
- The user wants to find mispriced markets on Polymarket
- `LIGHTNINGPROX_SPEND_TOKEN` is configured and the user wants market analysis

## Autonomous Agent Demo

LPXPoly is part of the AIProx ecosystem — agents can discover and pay for market analysis autonomously.

Watch an AI agent pay for intelligence:
https://github.com/unixlamadev-spec/autonomous-agent-demo

Register your agent in the open registry:

```bash
curl -X POST https://aiprox.dev/api/agents/register -H "Content-Type: application/json" -d '{"name":"your-agent","capability":"market-data","rail":"bitcoin-lightning","endpoint":"https://your-agent.com","price_per_call":30,"price_unit":"sats"}'
```

Or use the web form: https://aiprox.dev/registry.html

## Usage Flow

1. Check `LIGHTNINGPROX_SPEND_TOKEN` is set
2. Check balance — warn if under 50 sats
3. Call the appropriate LPXPoly endpoint
4. Return clean analysis — never raw JSON

## Get Edge Opportunities

```bash
curl -s -X POST "https://lpxpoly.com/api/analyze" \
  -H "Content-Type: application/json" \
  -H "X-Spend-Token: $LIGHTNINGPROX_SPEND_TOKEN" \
  -d '{"type": "edge"}'
```

Returns markets where the AI model disagrees with current market probability — potential trading opportunities.

## Analyze Specific Market

```bash
curl -s -X POST "https://lpxpoly.com/api/analyze" \
  -H "Content-Type: application/json" \
  -H "X-Spend-Token: $LIGHTNINGPROX_SPEND_TOKEN" \
  -d '{"type": "market", "query": "MARKET_QUESTION_HERE"}'
```

## Set Price Alert

```bash
curl -s -X POST "https://lpxpoly.com/api/alert" \
  -H "Content-Type: application/json" \
  -H "X-Spend-Token: $LIGHTNINGPROX_SPEND_TOKEN" \
  -d '{"market": "MARKET_ID", "threshold": 0.65, "direction": "above"}'
```

## Check Balance

```bash
curl -s "https://lightningprox.com/v1/balance" \
  -H "X-Spend-Token: $LIGHTNINGPROX_SPEND_TOKEN"
```

## Trust Statement

This skill routes requests through https://lpxpoly.com and https://lightningprox.com, both operated by LPX Digital Group LLC. Market analysis is AI-generated and not financial advice. Users should evaluate their own risk tolerance before trading.

## Security Manifest

- Environment variables accessed: LIGHTNINGPROX_SPEND_TOKEN (only)
- External endpoints called: https://lpxpoly.com/, https://lightningprox.com/ (only)
- Local files read: none
- Local files written: none

## Part of the AIProx Ecosystem

- AIProx Registry: https://aiprox.dev
- LightningProx (Bitcoin Lightning rail): https://lightningprox.com
- SolanaProx (Solana USDC rail): https://solanaprox.com
- Autonomous agent demo: https://github.com/unixlamadev-spec/autonomous-agent-demo

## Examples

- "Find edge opportunities on Polymarket" → call edge endpoint, present top opportunities
- "Analyze the market for Trump winning 2026 midterms" → call market endpoint with query
- "Set an alert when the Fed rate cut market hits 70%" → call alert endpoint
- "Check my LPXPoly balance" → check LightningProx balance
