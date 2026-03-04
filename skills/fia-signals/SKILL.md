---
name: fia-signals
description: >
  Real-time crypto market intelligence from Fía Signals. Use when asked about:
  crypto market regime, BTC regime, trending up or down, market direction,
  funding rates, liquidation zones, fear and greed index, RSI signals,
  MACD signals, crypto technical analysis, altseason, BTC dominance,
  open interest, market sentiment, crypto signals, is BTC bullish,
  what's the market doing, crypto market analysis.
---

# Fía Signals — Crypto Market Intelligence Skill

Provides real-time crypto market data and technical analysis via the Fía Signals x402 API.

## Available Endpoints

| Endpoint | What it returns | Cost |
|----------|----------------|------|
| /regime | Market regime (TRENDING UP/DOWN/RANGING), RSI, ADX, confidence | Free preview |
| /fear-greed | Fear & Greed index, 7-day trend, contrarian signal | Free preview |
| /funding | Top 10 perpetual futures funding rates | Free preview |
| /signals | RSI-14, MACD, Bollinger Bands for any symbol | Free preview |
| /prices | Real-time spot prices for up to 20 symbols | Free preview |
| /dominance | BTC and ETH market dominance % | Free preview |
| /liquidations | Recent liquidation events, long/short volumes | Free preview |

## Usage

Run the skill script with an action:

```bash
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh regime
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh fear-greed
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh signals BTCUSDT
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh prices BTC,ETH,SOL
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh funding
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh dominance
~/.openclaw/workspace/skills/fia-signals-skill/scripts/fia_signals.sh liquidations
```

## Data Source
Live data from Fía Signals: https://x402.fiasignals.com
Contact: fia-trading@agentmail.to
