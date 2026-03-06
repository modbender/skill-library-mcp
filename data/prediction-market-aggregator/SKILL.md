---
name: prediction-market-aggregator
version: 1.0.0
description: Cross-market prediction market data aggregator. Covers Polymarket, Manifold, Metaculus, and Kalshi. Finds arbitrage between markets, tracks consensus drift, compares implied probabilities, and detects edge. Open-source alternative to DomeAPI. Use when you need cross-market prediction market data, arbitrage detection, consensus comparison, or unified prediction market signals.
author: JamieRossouw
tags: [prediction-markets, polymarket, manifold, metaculus, arbitrage, domeapi-alternative]
---

# Prediction Market Aggregator

Cross-market prediction data, edge detection, and arbitrage scanner. Open-source alternative to DomeAPI.

## Markets Covered

| Market | Assets | API | Auth |
|--------|--------|-----|------|
| **Polymarket** | BTC, ETH, SOL, XRP hourly + major events | CLOB REST | API key + EIP-712 |
| **Manifold Markets** | Thousands of community markets | REST | API key (free) |
| **Metaculus** | Long-form forecasts, aggregated consensus | REST | None (public) |
| **Kalshi** | US-regulated binary contracts | REST | API key |

## Core Features

### 1. Cross-Market Arbitrage Scanner
Find the same question priced differently across markets:
```
BTC >$70k by March? 
  Polymarket: 62% 
  Manifold: 71%  ← 9% gap → sell Manifold, buy Polymarket
  Metaculus: 58%
```

### 2. Consensus Drift Detection
Track how market consensus shifts over time:
- Alert when market moves >10% within 30 minutes
- Detect smart money vs retail flow divergence
- Flag markets where Metaculus (superforecasters) disagrees >15% with Polymarket

### 3. Polymarket CLOB Integration
Full py-clob-client compatible:
- Scan hourly BTC/ETH/SOL/XRP markets
- Calculate edge vs TA-implied probability (Argus strategy)
- Counter-consensus detection (L023): market >70% one-sided + TA disagrees = bet

### 4. Unified API Response Format
```json
{
  "question": "BTC up by 1pm ET?",
  "markets": {
    "polymarket": { "yes": 0.62, "volume": 455000, "url": "..." },
    "manifold": { "yes": 0.71, "traders": 142, "url": "..." }
  },
  "arbitrage": { "detected": true, "gap": 0.09, "direction": "buy_poly_sell_manifold" },
  "consensus": { "weighted_avg": 0.65, "superforecaster_avg": 0.58 }
}
```

## How to Use

Ask: *"Is there arbitrage between Polymarket and Manifold on BTC price?"*
Ask: *"What markets have the widest consensus gap right now?"*
Ask: *"Find me the highest-edge Polymarket bet using cross-market consensus"*

## DomeAPI Migration Guide

If you used DomeAPI for cross-market data:
- `/v1/markets` → Use Polymarket CLOB `/markets` + Manifold `/v0/markets` + Metaculus `/questions`
- `/v1/arbitrage` → Use this skill's cross-market scanner
- `/v1/consensus` → Use Metaculus community predictions as consensus baseline

## Argus Integration

This skill plugs directly into the Argus edge detection strategy:
1. Get TA score from `argus-edge` skill
2. Compare vs cross-market consensus from this skill  
3. If TA + consensus both diverge from Polymarket price → max conviction bet
