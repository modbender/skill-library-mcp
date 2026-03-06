---
name: polymarket-user-analyzer
description: Analyze Polymarket user trading strategies and patterns. Extract wallet address from username, fetch trading history, and generate comprehensive strategy reports including win rate, market preferences, position sizing, entry price analysis, and profitability metrics. Use when asked to analyze a Polymarket user's strategy, trading patterns, or performance.
---

# Polymarket User Analyzer

Analyze any Polymarket user's trading strategy by their username or wallet address.

## What This Skill Does

1. Extracts wallet address from Polymarket username
2. Fetches complete trading history via Polymarket Data API
3. Analyzes trading patterns and strategy characteristics
4. Generates comprehensive performance reports

## Quick Start

```bash
# Analyze by username
node scripts/analyze_user.js @vague-sourdough

# Analyze by wallet address
node scripts/analyze_user.js 0x8c74b4eef9a894433B8126aA11d1345efb2B0488

# Save detailed report
node scripts/analyze_user.js @username --output report.json
```

## Analysis Metrics

The analyzer provides:

### Basic Statistics
- Total trades executed
- Total capital deployed
- Average position size
- Trading frequency

### Market Preferences
- Market type distribution (politics, sports, crypto, etc.)
- Specific asset focus (BTC, ETH, SOL, etc.)
- Market duration preferences (5-min, hourly, daily, long-term)

### Trading Patterns
- Direction bias (bullish/bearish)
- Entry price distribution (contrarian vs momentum)
- Position sizing strategy (fixed vs dynamic)
- Time-of-day patterns

### Performance Metrics
- Total P&L (profit/loss)
- ROI (return on investment)
- Win rate (if calculable from redeems)
- Risk-adjusted returns

### Strategy Classification

The analyzer identifies common strategy types:
- **Value Investor**: Buys underpriced outcomes (low entry prices)
- **Momentum Trader**: Follows market trends (high entry prices)
- **Arbitrageur**: Exploits pricing inefficiencies
- **Scalper**: High-frequency small positions
- **Conviction Trader**: Large positions, low frequency

## API Reference

### Polymarket Data API

**Get wallet address from username:**
```javascript
// Fetch user profile page and extract address
const response = await fetch(`https://polymarket.com/@${username}`);
const html = await response.text();
const address = html.match(/0x[a-fA-F0-9]{40}/)[0];
```

**Get trading history:**
```
GET https://data-api.polymarket.com/activity?user={address}&limit={limit}
```

**Response format:**
```json
{
  "proxyWallet": "0x...",
  "timestamp": 1234567890,
  "type": "TRADE" | "REDEEM",
  "side": "BUY" | "SELL",
  "price": 0.45,
  "size": 10.5,
  "usdcSize": 5.0,
  "outcome": "Yes" | "No",
  "title": "Market title",
  "slug": "market-slug"
}
```

## Output Format

The analyzer generates a structured report:

```markdown
# Strategy Analysis: @username

## Overview
- Total Trades: X
- Capital Deployed: $X
- ROI: X%
- Strategy Type: [Classification]

## Market Focus
- Primary Markets: [List]
- Asset Distribution: [Breakdown]

## Trading Characteristics
- Average Entry Price: X
- Position Sizing: [Fixed/Dynamic]
- Direction Bias: [Neutral/Bullish/Bearish]

## Performance
- Total P&L: $X
- Win Rate: X%
- Best Trade: [Details]
- Worst Trade: [Details]

## Strategy Insights
[Key observations and patterns]
```

## Privacy & Ethics

**Important:** This skill only analyzes publicly available on-chain data. All Polymarket trades are public by design. This tool does not:
- Access private information
- Require authentication
- Store or transmit data to external servers
- Violate any terms of service

Users should be aware that their Polymarket activity is public and can be analyzed by anyone.

## Limitations

- Only analyzes completed trades (on-chain data)
- Cannot see pending orders or private strategies
- REDEEM events may not always indicate wins (market could resolve to 0)
- Historical data limited by API (typically last 100-1000 trades)
- Does not account for gas fees or slippage

## Use Cases

- **Learning**: Study successful traders' strategies
- **Research**: Analyze market participant behavior
- **Due Diligence**: Verify claimed trading performance
- **Strategy Development**: Identify profitable patterns
- **Market Analysis**: Understand trader sentiment and positioning
