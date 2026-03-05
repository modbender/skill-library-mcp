---
name: coinversaa-pulse
description: "Crypto intelligence for AI agents. 26 tools for Hyperliquid trader analytics, behavioral cohorts, live market data, liquidation heatmaps, and whale tracking across 710K+ wallets and 1.8B+ trades."
version: 0.2.1
author: Coinversaa <hello@coinversaa.ai>
homepage: https://coinversaa.ai
repository: https://github.com/coinversaa/mcp-server
license: MIT
tags:
  - crypto
  - trading
  - hyperliquid
  - market-data
  - defi
  - analytics
  - blockchain
  - whale-tracking
  - mcp
env:
  COINVERSAA_API_KEY:
    description: "Your Coinversaa API key (starts with cvsa_). Get one at https://coinversaa.ai/developers"
    required: true
  COINVERSAA_API_URL:
    description: "API base URL (defaults to https://staging.api.coinversaa.ai)"
    required: false
---

# Coinversaa Pulse

Crypto intelligence for AI agents. Query 710K+ Hyperliquid wallets, 1.8B+ trades, behavioral cohorts, and live market data through any MCP-compatible client.

This is not a wrapper around a public blockchain API. Coinversaa indexes Hyperliquid's clearinghouse directly and computes analytics that don't exist anywhere else.

## Setup

### 1. Get an API Key

Request one at [coinversaa.ai/developers](https://coinversaa.ai/developers) or email [chat@coinversaa.ai](mailto:chat@coinversaa.ai).

### 2. Install

```bash
npx -y @coinversaa/mcp-server@latest
```

### 3. Configure

**Claude Desktop** — edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "coinversaa": {
      "command": "npx",
      "args": ["-y", "@coinversaa/mcp-server"],
      "env": {
        "COINVERSAA_API_KEY": "cvsa_your_key_here"
      }
    }
  }
}
```

**Cursor** — add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "coinversaa": {
      "command": "npx",
      "args": ["-y", "@coinversaa/mcp-server"],
      "env": {
        "COINVERSAA_API_KEY": "cvsa_your_key_here"
      }
    }
  }
}
```

**Claude Code**:

```bash
claude mcp add coinversaa -- npx -y @coinversaa/mcp-server
export COINVERSAA_API_KEY="cvsa_your_key_here"
```

**OpenClaw**:

```bash
openclaw skill install coinversaa-pulse
```

## Tools (26)

### Pulse — Trader Intelligence

Use these tools when the user asks about top traders, market activity, or trading trends.

- **`pulse_global_stats`** — Global Hyperliquid stats: total traders, trades, volume, PnL, data coverage period. Use when asked about overall market scale.
- **`pulse_market_overview`** — Full market state: 24h volume, open interest, mark prices, funding rates, 24h change for every pair. Use for broad market snapshots.
- **`pulse_leaderboard`** — Ranked trader leaderboard. Sort by `pnl`, `winrate`, `volume`, `score`, `risk-adjusted`, or `losers`. Filter by period (`day`/`week`/`month`/`allTime`) and minimum trades. Use when asked "who are the best traders?"
  - Parameters: `sort`, `period`, `limit` (1-100), `minTrades`
- **`pulse_hidden_gems`** — Underrated high-performers most platforms miss. Filter by min win rate, PnL, trade count. Use when asked to find skilled but unknown traders.
  - Parameters: `minWinRate`, `minPnl`, `minTrades`, `maxTrades`, `limit` (1-100)
- **`pulse_most_traded_coins`** — Most actively traded coins ranked by volume and trade count. Use when asked "what's hot right now?"
  - Parameters: `limit` (1-100)
- **`pulse_biggest_trades`** — Biggest winning or losing trades across all of Hyperliquid. Use for sentiment analysis or when asked about major market moves.
  - Parameters: `type` (`wins`/`losses`), `limit` (1-50), `threshold`
- **`pulse_recent_trades`** — Biggest trades in the last N minutes/hours sorted by absolute PnL. Use for real-time market activity.
  - Parameters: `since` (e.g. `10m`, `1h`, `1d`), `limit` (1-100), `coin` (optional)
- **`pulse_token_leaderboard`** — Top traders for a specific coin. Use when asked "who are the best BTC traders?"
  - Parameters: `coin`, `limit` (1-100)

### Pulse — Trader Profiles

Use these tools for deep dives on specific wallets. Any tool taking `address` expects a full Ethereum address (0x + 40 hex chars).

- **`pulse_trader_profile`** — Full due diligence: total PnL, trade count, win rate, volume, largest win/loss, first/last trade dates, PnL tier, size tier, profit factor. Use for "tell me about this wallet."
  - Parameters: `address`
- **`pulse_trader_performance`** — 30-day vs all-time comparison with trend direction (improving/declining/stable). Use for "is this trader still hot?"
  - Parameters: `address`
- **`pulse_trader_trades`** — Recent trades for any wallet: every buy, sell, size, price, PnL. Use for copy-trading signals or "what did this wallet trade recently?"
  - Parameters: `address`, `since`, `limit` (1-100), `coin` (optional)
- **`pulse_trader_daily_stats`** — Day-by-day PnL, trade count, win rate, volume. Use for consistency analysis or "show me their daily performance."
  - Parameters: `address`
- **`pulse_trader_token_stats`** — Per-coin P&L breakdown. Use when asked "which coins does this trader profit from?"
  - Parameters: `address`
- **`pulse_trader_closed_positions`** — Full position history: entry/exit prices, hold duration, PnL, leverage. Use for "show me their position history."
  - Parameters: `address`, `limit` (1-200), `offset`, `coin` (optional)
- **`pulse_trader_closed_position_stats`** — Aggregate closed position stats: avg hold duration, position win rate, total closed, PnL summary. Use for "is this a scalper or swing trader?"
  - Parameters: `address`

### Pulse — Cohort Intelligence

Coinversaa classifies 710K+ wallets into behavioral tiers. This is unique data nobody else has.

**PnL tiers** (by profitability): `money_printer`, `smart_money`, `grinder`, `humble_earner`, `exit_liquidity`, `semi_rekt`, `full_rekt`, `giga_rekt`

**Size tiers** (by volume): `leviathan`, `tidal_whale`, `whale`, `small_whale`, `apex_predator`, `dolphin`, `fish`, `shrimp`

- **`pulse_cohort_summary`** — Full behavioral breakdown across all wallets. Each tier shows wallet count, avg PnL, avg win rate, total volume. Use when asked about market composition or "how do different types of traders perform?"
- **`pulse_cohort_positions`** — What a specific cohort is holding RIGHT NOW. Use for "what are the money_printers long on?" or whale watching.
  - Parameters: `tierType` (`pnl`/`size`), `tier`, `limit` (1-200)
- **`pulse_cohort_trades`** — Every trade a cohort made in a time window. Use for "show me what smart_money traded in the last hour."
  - Parameters: `tierType`, `tier`, `since`, `limit` (1-100)
- **`pulse_cohort_history`** — Day-by-day historical performance for a cohort. Use to spot trends like "smart_money has been increasingly bearish."
  - Parameters: `tierType`, `tier`, `days` (1-365)

### Market — Live Data

Real-time market data directly from Hyperliquid.

- **`market_price`** — Current mark price for any symbol. Use when asked "what's the price of BTC?"
  - Parameters: `symbol` (e.g. BTC, ETH, SOL)
- **`market_positions`** — All open positions for any wallet with entries, sizes, unrealized PnL, leverage. Use for "what is this wallet holding?"
  - Parameters: `address`
- **`market_orderbook`** — Bid/ask depth for any pair. Use for liquidity analysis or "show me the ETH order book."
  - Parameters: `symbol`, `depth` (1-50)

### Live — Real-Time Analytics

Derived analytics computed in real-time.

- **`live_liquidation_heatmap`** — Liquidation clusters across price levels for any coin. Use for "where are the BTC liquidation clusters?" or support/resistance analysis.
  - Parameters: `coin`, `buckets` (10-100), `range` (1-50% around current price)
- **`live_long_short_ratio`** — Global or per-coin long/short ratio with optional history. Use when asked about market sentiment or positioning.
  - Parameters: `coin` (optional), `hours` (optional, 1-168 for history)
- **`live_cohort_bias`** — Net long/short stance for every tier on a given coin. Use when asked "are smart money traders long or short ETH?"
  - Parameters: `coin`
- **`pulse_recent_closed_positions`** — Positions just closed across all traders. Filterable by coin, size, and hold duration. Use to find HFT trades (`maxDuration=1000`), large exits (`minNotional=100000`), or recent stop-outs.
  - Parameters: `since`, `limit` (1-200), `coin`, `minNotional`, `minDuration`, `maxDuration`

## Example Prompts

Once connected, try asking your AI:

- "What are the top 5 traders on Hyperliquid by PnL?"
- "Show me what the money_printer tier is holding right now"
- "What are the biggest trades in the last 10 minutes?"
- "Find underrated traders with 70%+ win rate"
- "Do a deep dive on wallet 0x7fda...7d1 — are they still performing?"
- "Where are the BTC liquidation clusters?"
- "Are smart money traders long or short ETH right now?"
- "What coins are most actively traded right now?"
- "Show me the biggest losses in the last 24 hours"
- "Is this trader a scalper or swing trader? What's their average hold time?"
- "Which coins does this trader actually make money on?"
- "What did the whale tier trade in the last hour?"
- "Compare this trader's last 30 days to their all-time performance"

## What Makes This Different

- **Behavioral cohorts**: 710K wallets classified into PnL tiers (money_printer to giga_rekt) and size tiers (leviathan to shrimp)
- **Live cohort positions**: See what the best traders are holding in real-time
- **Real-time trade feed**: Every trade by any wallet or cohort, queryable by time window
- **Liquidation heatmaps**: Cluster analysis across price levels for any coin
- **Closed position analytics**: Full position lifecycle with hold duration and entry/exit analysis
- **Hidden gem discovery**: Find skilled traders that ranking sites miss
- **1.8B+ trades indexed**: The deepest Hyperliquid dataset available as an API

## Rate Limits

Default: 100 requests/minute per API key. Rate limit headers are included in every response:
- `X-RateLimit-Limit`: your configured limit
- `X-RateLimit-Remaining`: requests left in current window
- `X-RateLimit-Reset`: seconds until window resets

## Links

- Website: [coinversaa.ai](https://coinversaa.ai)
- API Docs: [coinversaa.ai/developers](https://coinversaa.ai/developers)
- GitHub: [github.com/coinversaa/mcp-server](https://github.com/coinversaa/mcp-server)
- npm: [@coinversaa/mcp-server](https://www.npmjs.com/package/@coinversaa/mcp-server)
- Support: [chat@coinversaa.ai](mailto:chat@coinversaa.ai)

---

Built by [Coinversaa](https://coinversaa.ai) — Crypto intelligence for AI agents.
