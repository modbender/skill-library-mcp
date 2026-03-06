---
name: trading-tournament
description: "Run autonomous multi-agent trading competitions on OKX. 5 AI agents compete with real-time market data, evolutionary selection replaces losers daily, exchange-level stop-losses protect capital. Battle-tested framework for algorithmic trading research."
version: 1.0.0
---

# Trading Tournament 🏆

Run autonomous multi-agent trading competitions where AI strategies compete against each other with real market data.

## What It Does

- **5 agents compete** simultaneously on OKX Demo (or Live)
- **Every 5 minutes**: each agent analyzes candles, indicators, and decides to enter/exit
- **Daily evolution** at 07:00: top 2 survive, bottom 2 get replaced by better strategies
- **Exchange-level stop-losses**: positions are protected even if the bot crashes
- **3-layer position sizing protection**: unknown assets skipped, 50% equity cap, $500 hard max

## Architecture

```
┌─────────────┐
│ Competition  │ ← runs every 5 minutes
│  Manager     │
└──────┬──────┘
       │
  ┌────┼────┬────┬────┐
  │    │    │    │    │
  v    v    v    v    v
Agent1 Agent2 Agent3 Agent4 Agent5
(S&D)  (RSI)  (S&D)  (RSI)  (RSI)
       │
       v
  ┌─────────┐
  │ OKX API │ ← real-time prices, order execution
  └─────────┘
```

## Strategies Included

1. **Supply & Demand** — Identifies accumulation/distribution zones, enters on retests
2. **RSI Mean Reversion** — Overbought/oversold with EMA trend filter
3. **RSI Fast Confirm** — 1-bar bounce confirmation with tight EMA alignment
4. **RSI Trend Filter** — Long-period EMA filter with standard RSI levels

## Safety Features

| Layer | Protection | What Happens |
|-------|-----------|-------------|
| 1 | CT_VALS lookup | Unknown asset → SKIP (never enter blind) |
| 2 | 50% equity cap | Max position = half of agent's capital |
| 3 | $500 hard cap | Absolute maximum notional per trade |
| 4 | Exchange SL | Stop-loss on OKX itself (survives bot crash) |
| 5 | Guardian | Windows Task checks every minute, restarts if dead |

## Setup

### Prerequisites
- OKX account (Demo or Live)
- API Key + Secret + Passphrase
- Node.js 18+

### Quick Start

1. Copy `bybit-trading/` folder to your workspace
2. Create `.secrets/okx.env`:
```
OKX_API_KEY=your_key
OKX_API_SECRET=your_secret
OKX_PASSPHRASE=your_passphrase
```
3. Edit `agents_config.json` with your preferred strategies and assets
4. Run: `node competition_manager_okx.js`

### Cron Setup (recommended)

Add a Guardian cron or Windows Task that checks `competition_log_okx.txt` freshness every minute. If log hasn't updated in 6 minutes → kill and restart.

## Evolution Rules

Daily at 07:00:
- 🥇 Rank 1 → Survives (strategy + assets)
- 🥈 Rank 2 → Survives (strategy + assets)
- 🥉 Rank 3 → Strategy stays, assets rotate to better performers
- 4️⃣ Rank 4 → Fully replaced from best_strategies pool
- 5️⃣ Rank 5 → Fully replaced from best_strategies pool

Criteria for new agents: PF > 1.5, DD < 25%, min 5 backtested trades.

## Live Trading Checklist

Before going live with real money:
- [ ] 7 days continuous run without crashes
- [ ] P&L > 15% on demo
- [ ] 30+ trades for top 3 agents
- [ ] Max drawdown < 10%
- [ ] 0 sizing bugs
- [ ] Exchange-level SL verified on all new positions

## Built With

- Node.js + OKX REST API
- Technical indicators (EMA, RSI, ATR, Supply/Demand zones)
- Evolutionary selection algorithm
- Real-time Telegram alerts
