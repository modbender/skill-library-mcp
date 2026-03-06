---
name: polymarket-scout
version: 1.0.0
description: Scan Polymarket hourly crypto markets (BTC/ETH/SOL/XRP) for edge opportunities. Detects counter-consensus setups, freshness windows, and expected value using the Argus strategy. Use when you need Polymarket market scanning, edge detection, hourly binary market analysis, or prediction market signals.
author: JamieRossouw
tags: [polymarket, prediction-markets, crypto, edge-detection, betting, defi]
---

# Polymarket Scout — Hourly Market Edge Detector

Scans Polymarket's hourly BTC/ETH/SOL/XRP up/down markets for tradeable edge using the Argus strategy.

## What It Does

- Fetches live Polymarket odds for hourly crypto markets via REST API
- Computes edge = our_P(win) - market_implied_P(win)
- Flags counter-consensus setups (TA says UP, market says 70%+ DOWN → positive EV)
- Applies freshness guard: skips markets >92% consensus (L020)
- Returns ranked edge opportunities with bet sizing (Kelly)

## Usage

```
Use polymarket-scout to scan current hourly markets for edge

Use polymarket-scout to check BTC 10am ET edge

Use polymarket-scout to find best Polymarket bet right now
```

## Edge Calculation

```
edge = our_P - market_P
where our_P = TA-calibrated probability per asset:
  BTC: reliability 0.75, min score ±3
  ETH: reliability 0.80, slight UP bias +0.05
  SOL: reliability 0.90, UP bias +0.05
  XRP: reliability 0.70, UP bias +0.08 (CLARITY catalyst)
```

## Counter-Consensus Rule (L023)
When TA score ≥+1 AND market DOWN >80% AND ≥20 min remaining → counter-consensus UP has positive EV. Validated: 77.8% WR on fresh primary bets.

## API Integration
Uses Polymarket CLOB REST API and Gamma API (no keys required).
