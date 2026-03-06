---
name: rho-portfolio-tracker
version: 1.0.0
description: Track a crypto portfolio across Binance, Hyperliquid, and Polymarket. Calculates NAV, unrealized P&L, daily drawdown, win rate, and equity curve. Use when you need portfolio tracking, NAV calculation, drawdown monitoring, or multi-venue position management.
author: JamieRossouw
tags: [crypto, portfolio, tracking, binance, hyperliquid, pnl, nav, drawdown]
---
# Crypto Portfolio Tracker

Multi-venue portfolio tracker for autonomous crypto trading agents.

## Venues Supported
- Binance Spot (paper + live via CCXT)
- Hyperliquid Perps (paper + live)
- Polymarket prediction markets

## Features
- Real-time NAV calculation with mark-to-market
- Daily drawdown tracking with auto-pause at configurable threshold
- Win rate, expectancy, and equity curve
- Position sizing validation (Kelly criterion)
- CSV ledger export for full audit trail

## Usage
```
Use crypto-portfolio-tracker to check my portfolio NAV

Use crypto-portfolio-tracker to show today's P&L breakdown

Use crypto-portfolio-tracker to export my trade history
```

## Output Example
```
NAV: $748.36 | Start: $750 | Daily P&L: +$2.16 | DD: 0.00%
Positions: 7 | Trades today: 16 | W:8 L:8 | WR: 50%
Best trade: SOL +$1.20 | Worst: BTC -$0.80
```
