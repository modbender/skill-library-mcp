---
name: Solana Memecoin Guardian v2
description: Solana Memecoin Guardian v2 is an autonomous trading skill designed
  to discover and trade Solana memecoins while minimizing downside risk.
---

# Solana Memecoin Guardian v2

## Overview
Solana Memecoin Guardian v2 is an autonomous trading skill designed to discover and trade Solana memecoins while minimizing downside risk.

The system combines several intelligence layers:

- Smart wallet copy trading
- AI-driven market analysis
- Social narrative detection (X / Twitter trends)
- Strict on-chain risk validation

The goal is not to chase every pump, but to selectively enter high‑probability opportunities while avoiding rug pulls and unsafe tokens.

---

## Core Capabilities

### 1. Smart Wallet Copy Trading
The skill monitors high-performing Solana wallets and selectively mirrors their trades.

Features:
- Wallet performance filtering
- Randomized delay before copying trades
- Anti‑FOMO entry protection
- Automatic exit when tracked wallets sell

### 2. AI Market Analysis
The AI engine scans Solana tokens using data sources such as:

- Pump.fun
- DexScreener
- On‑chain liquidity data

Signals are generated using rule‑based scoring models that evaluate:

- Liquidity stability
- Transaction activity
- Volume distribution
- Price volatility
- Market structure

Only tokens passing strict safety filters are considered.

### 3. Narrative Detection Engine
The system monitors viral narratives from social platforms such as X (Twitter).

When influential accounts or trending discussions appear, related tokens are prioritized for analysis.

Narrative signals increase priority but **never bypass risk validation**.

### 4. Risk Gate System
Every trade must pass the Risk Gate.

The system checks:

- Liquidity thresholds
- Mint authority status
- Freeze authority status
- Holder concentration
- Transaction anomalies
- Price impact risk

If any safety rule fails, the trade is rejected.

### 5. Position Management
Positions are automatically managed using:

- Stop Loss
- Multi‑level Take Profit
- Trailing Stop
- Liquidity monitoring
- Emergency exit triggers

### 6. Rug Pull Protection
A Rug Alarm system monitors:

- Liquidity removal
- Whale holder spikes
- Abnormal price impact
- Suspicious trading patterns

If a rug signal appears, the system exits immediately.

---

## Data Sources

- Pump.fun
- DexScreener
- Solana RPC
- Smart wallet transaction streams
- Social trend detection from X (Twitter)

---

## Execution Layer

Trades are executed using:

- Jupiter Swap API
- Solana RPC
- Automated transaction signing

Both modes are supported:

- Paper trading mode
- Live trading mode

---

## Risk Philosophy

Solana memecoin markets are extremely volatile.

The core philosophy of this skill:

Missing 100 pumps is acceptable.  
Surviving one rug is mandatory.

Capital preservation always comes first.
