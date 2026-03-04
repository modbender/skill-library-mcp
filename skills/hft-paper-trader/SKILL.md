---
name: hft-paper-trader
version: 1.0.0
description: High-frequency paper trading framework for crypto. Multi-indicator TA scoring (RSI/MACD/EMA/BB/OBV/StochRSI), position sizing (Kelly criterion), stop-loss management, and trade ledger. Targets 300+ trades/day at 0.05% risk per trade. Use for paper trading, backtesting trading logic, HFT simulation, or building an autonomous trading agent.
author: JamieRossouw
tags: [trading, paper-trading, hft, crypto, kelly, backtesting, autonomous-agent]
---

# HFT Paper Trader — Autonomous Crypto Trading Framework

A complete high-frequency paper trading system for building and testing autonomous crypto trading agents.

## Architecture

```
Market Data (Binance public API)
    ↓
TA Engine (RSI + MACD + EMA + BB + OBV + StochRSI)
    ↓
Signal Score (-10 to +10)
    ↓
Kelly Position Sizer (0.05% risk per trade)
    ↓
Paper Portfolio Manager (PORTFOLIO.json)
    ↓
Trade Ledger (LEDGER.csv)
```

## Features

- **Multi-indicator confluence**: 7 indicators combined into one score
- **OBV divergence detection**: hidden accumulation/distribution
- **Quarter-Kelly sizing**: conservative risk management
- **Drawdown controls**: auto-pause at 2% daily NAV
- **Full audit trail**: every trade logged with entry/stop/target/outcome
- **Self-improvement loop**: lessons.md updated after each loss

## Usage

```
Use hft-paper-trader to run TA on BTC and place a paper trade

Use hft-paper-trader to check portfolio performance

Use hft-paper-trader to scan the watchlist and trade all signals
```

## Watchlist
BTC ETH SOL XRP TRX DOGE ADA AVAX BNB LINK LTC SUI ARB OP NEAR DOT ATOM UNI MATIC

## Performance
Binance paper NAV: $748+ on $750 starting capital. Daily target: 100+ trades.
