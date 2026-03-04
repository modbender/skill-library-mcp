---
name: crypto-macro-regime
version: 1.0.0
description: Classify current crypto macro regime (Risk-On / Risk-Off / Neutral) using Fear & Greed Index, BTC dominance, Reddit sentiment, on-chain signals, and macro news. Returns regime label, bias direction, and asset-specific adjustments. Use for macro analysis, regime detection, portfolio bias, or market context.
author: JamieRossouw
tags: [macro, crypto, regime, fear-greed, sentiment, bitcoin, market-analysis]
---

# Crypto Macro Regime Classifier

Determines the current macro regime for crypto markets and adjusts trading bias accordingly.

## Regimes

| Regime | F&G | Signals | Bias |
|--------|-----|---------|------|
| A — Risk On | 50+ | Positive news, low dominance | Long bias +0.10 |
| B — Neutral | 25–50 | Mixed | No adjustment |
| C — Risk Off | <25 | Fear, macro shock | Short bias, reduce size |
| D — Extreme Fear | <15 | Capitulation | Contrarian long setup |

## What It Returns

- Current regime (A/B/C/D) with confidence
- Fear & Greed value + classification
- Asset-specific bias adjustments
- Key macro drivers (Fed, regulation, hack risks)
- Recommended portfolio allocation %

## Usage

```
Use crypto-macro-regime to get current market regime

Use crypto-macro-regime to check if now is a good time to go long BTC

Use crypto-macro-regime for today's macro briefing
```

## Data Sources
- alternative.me Fear & Greed API (free)
- Reddit r/CryptoCurrency, r/Bitcoin sentiment
- CoinDesk headlines
- BTC difficulty and dominance data

## Current Calibration
Regime D (Extreme Fear, F&G=8) = historically strong medium-term contrarian bullish signal. Best entries: RSI 35–55 range after panic selloff.
