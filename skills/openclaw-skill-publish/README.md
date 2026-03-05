# probtrade — Polymarket Analytics for OpenClaw

Get real-time prediction market analytics from [prob.trade](https://app.prob.trade) directly in your OpenClaw agent.

## What's different from polyclaw?

| Feature | polyclaw | **probtrade** |
|---------|----------|---------------|
| Browse raw markets | Yes | Yes |
| Trading | Yes (needs private key) | **Yes** (via API keys, HMAC-secured) |
| Hot/trending markets | No | **Yes** |
| Breaking price movements | No | **Yes** |
| Top traders leaderboard | No | **Yes** |
| Copy-trading intelligence | No | **Yes** |
| Market search | Basic | **Full-text** |

**probtrade** gives you both analytics and trading — from market intelligence to placing orders, all through your OpenClaw agent.

## Installation

### From ClawHub
```bash
clawhub install probtrade
```

### Manual
```bash
cp -r probtrade/ ~/.openclaw/skills/probtrade/
```

## Usage

Just ask your OpenClaw agent naturally:

- "What prediction markets are trending right now?"
- "Show me markets about Trump"
- "Which markets have the biggest price swings today?"
- "Who are the most profitable Polymarket traders?"
- "Give me an overview of the prediction market landscape"

Or use specific commands:

```
/probtrade overview          — Market snapshot
/probtrade hot               — Trending markets
/probtrade breaking          — Biggest price movements
/probtrade new               — Recently created markets
/probtrade search "Bitcoin"  — Search markets
/probtrade traders           — Top traders leaderboard
/probtrade stats             — Category breakdown
```

## Trading API

Trade on Polymarket directly through your OpenClaw agent using prob.trade API keys.

### Setup

1. Go to [app.prob.trade](https://app.prob.trade) and create an account
2. Navigate to Settings and generate an API key
3. Configure the skill:

```yaml
# ~/.openclaw/skills/probtrade/config.yaml
api_key: "ptk_live_..."
api_secret: "pts_..."
```

### Trading Commands

```
/probtrade buy "Will Trump win?" yes $100          — Market order
/probtrade buy "Will Trump win?" yes $100 @0.55    — Limit order at $0.55
/probtrade sell "Will Trump win?" yes $50           — Sell position
/probtrade cancel <orderId>                         — Cancel order
/probtrade positions                                — Open positions
/probtrade balance                                  — USDC balance
/probtrade orders                                   — Open orders
```

Or use natural language:
- "Buy $100 of Yes on the Trump election market at 55 cents"
- "What are my current positions?"
- "Cancel all my open orders"

### Security

- API secret never leaves your machine — only HMAC signatures are sent
- No withdraw/transfer endpoints — Trading API can only trade and read
- Keys can be revoked instantly from the dashboard

## Requirements

- Python 3 (no additional packages needed — uses only stdlib)
- prob.trade API key required for all commands (free, generated in dashboard)

## API

- **Public Analytics API** (no auth): [api.prob.trade/api/public](https://api.prob.trade/api/public/overview) — markets, stats, traders
- **Trading API** (API key + HMAC): [api.prob.trade/api/trading](https://api.prob.trade/api/trading) — orders, positions, balance

## Links

- [ClawHub](https://clawhub.ai/vlprosvirkin/prob-trade-polymarket-analytics)
- [prob.trade Dashboard](https://app.prob.trade)
- [Public API Reference](https://prob.trade/docs/public-api)
- [Trading API Reference](https://github.com/vlprosvirkin/probtrade-openclaw-skill/blob/main/docs/trading-api-reference.md)
