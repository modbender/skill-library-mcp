---
name: rho-signals
version: 1.0.0
description: Real-time crypto TA signals for BTC, ETH, SOL, XRP. RSI, MACD, EMA, Bollinger Bands, OBV divergence, StochRSI — combined into a single directional score (-10 to +10) with Polymarket edge detection. Use when you need live crypto TA signals, directional bias, or Polymarket hourly market edge analysis.
author: rho-genesis
tags: [crypto, trading, signals, polymarket, technical-analysis, bitcoin, ethereum, solana, xrp]
price: 0.01
---

# RHO Signals — Live Crypto TA Engine

Real-time technical analysis signals for BTC, ETH, SOL and XRP. Powered by multi-indicator confluence: RSI, MACD, EMA cross, Bollinger Bands, OBV divergence, StochRSI, and ATR volatility filtering.

## What You Get

- **Directional score** (−10 to +10) per asset — negative = bearish, positive = bullish
- **RSI** with overbought/oversold detection
- **OBV divergence** — hidden accumulation/distribution signals
- **Polymarket edge** — compares TA-implied probability vs live market odds
- **Counter-consensus alerts** — when TA contradicts market >70% consensus

## Usage

```
# Get signal for one asset
Use the rho-signals skill to get BTC signal

# Get all signals + Polymarket edge
Use rho-signals to get full market scan with Polymarket edges
```

## Signal Scale

| Score | Meaning |
|-------|---------|
| +5 to +10 | Strong buy — all indicators aligned bullish |
| +2 to +4 | Moderate bullish bias |
| 0 to ±1 | Neutral / conflicting signals |
| -2 to -4 | Moderate bearish bias |
| -5 to -10 | Strong sell — all indicators aligned bearish |

## Live API (x402 — pay per signal)

Signals also available via HTTP with micropayment:
- Endpoint: https://rho-signals.clawpay.bot (coming soon)
- Price: $0.001 USDC per signal
- Accepts x402 payment headers

## Data Sources
- Binance public API (no key needed)
- 1h OHLCV candles, 50 periods lookback
- Updates every heartbeat (~30 min)

## Accuracy Notes
- Backtested on Polymarket hourly markets: 77.8% win rate on fresh (<30 min) markets
- Best assets: SOL (+5% UP bias), ETH (RSI-responsive), XRP (CLARITY catalyst)
- Worst: BTC (low predictability on 1h candles — use score ≥±4 only)
