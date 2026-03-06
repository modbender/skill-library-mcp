---
name: options-strategies
description: >
  Comprehensive guide and execution framework for popular options trading strategies.
  Use when users ask to explain, set up, analyze, or compare options strategies
  including directional, neutral, volatility, and income-based plays.
---

# Options Strategies Skill

## Overview

This skill provides structured knowledge and step-by-step execution guidance
for the most popular options strategies — from basic single-leg trades to
complex multi-leg spreads.

---

## Strategy Taxonomy

### 1. Directional Bullish Strategies

#### Long Call
- **Setup**: Buy 1 call option
- **Max Profit**: Unlimited
- **Max Loss**: Premium paid
- **Breakeven**: Strike + Premium
- **Best For**: Strong bullish conviction with defined risk
- **Greeks**: +Delta, +Vega, -Theta

#### Bull Call Spread (Debit Spread)
- **Setup**: Buy lower strike call, Sell higher strike call (same expiry)
- **Max Profit**: Width of spread - net debit
- **Max Loss**: Net debit paid
- **Breakeven**: Lower strike + net debit
- **Best For**: Moderate bullish view, lower cost than long call
- **Greeks**: +Delta (reduced), -Vega (reduced), -Theta (reduced)

#### Bull Put Spread (Credit Spread)
- **Setup**: Sell higher strike put, Buy lower strike put (same expiry)
- **Max Profit**: Net credit received
- **Max Loss**: Width of spread - net credit
- **Breakeven**: Higher strike - net credit
- **Best For**: Moderately bullish, income generation, high probability trade
- **Greeks**: +Delta, -Vega, +Theta

#### Cash-Secured Put
- **Setup**: Sell a put, hold cash to cover assignment
- **Max Profit**: Premium received
- **Max Loss**: Strike price - premium (stock going to zero)
- **Breakeven**: Strike - premium
- **Best For**: Willing to own stock at a discount, income generation

#### Synthetic Long Stock
- **Setup**: Buy ATM call, Sell ATM put (same strike, same expiry)
- **Max Profit**: Unlimited
- **Max Loss**: Substantial (like owning stock)
- **Best For**: Bullish with less capital than buying stock

---

### 2. Directional Bearish Strategies

#### Long Put
- **Setup**: Buy 1 put option
- **Max Profit**: Strike - Premium (stock to zero)
- **Max Loss**: Premium paid
- **Breakeven**: Strike - Premium
- **Best For**: Strong bearish conviction, portfolio hedging
- **Greeks**: -Delta, +Vega, -Theta

#### Bear Put Spread (Debit Spread)
- **Setup**: Buy higher strike put, Sell lower strike put (same expiry)
- **Max Profit**: Width of spread - net debit
- **Max Loss**: Net debit paid
- **Breakeven**: Higher strike - net debit
- **Best For**: Moderate bearish view, lower cost than long put

#### Bear Call Spread (Credit Spread)
- **Setup**: Sell lower strike call, Buy higher strike call (same expiry)
- **Max Profit**: Net credit received
- **Max Loss**: Width of spread - net credit
- **Breakeven**: Lower strike + net credit
- **Best For**: Moderately bearish, income generation

---

### 3. Neutral / Range-Bound Strategies

#### Iron Condor
- **Setup**: 
  - Sell OTM call + Buy further OTM call (bear call spread)
  - Sell OTM put + Buy further OTM put (bull put spread)
  - All same expiry
- **Max Profit**: Total net credit received
- **Max Loss**: Width of wider wing - total credit
- **Breakeven**: Two breakevens (upper and lower)
- **Best For**: Low volatility expected, range-bound market
- **Greeks**: -Delta (near zero), -Vega, +Theta

#### Iron Butterfly
- **Setup**:
  - Sell ATM call + Buy OTM call
  - Sell ATM put + Buy OTM put
  - ATM strikes are the same (body)
- **Max Profit**: Net credit (at expiry at body strike)
- **Max Loss**: Wing width - net credit
- **Best For**: Very tight range expected around current price, higher credit than condor

#### Short Straddle
- **Setup**: Sell ATM call + Sell ATM put (same strike, same expiry)
- **Max Profit**: Total premium received
- **Max Loss**: Unlimited (on call side)
- **Breakeven**: Strike ± total premium
- **Best For**: Very low volatility expected — high risk, requires margin
- **Greeks**: -Vega (strong), +Theta (strong), near-zero Delta

#### Short Strangle
- **Setup**: Sell OTM call + Sell OTM put (different strikes, same expiry)
- **Max Profit**: Total premium received
- **Max Loss**: Unlimited (on call side)
- **Breakeven**: Call strike + premium / Put strike - premium
- **Best For**: Low volatility, wider profit zone than short straddle, still high risk

#### Covered Call
- **Setup**: Own 100 shares + Sell 1 OTM call
- **Max Profit**: (Call strike - stock cost) + premium
- **Max Loss**: Stock price - premium paid (stock goes to zero)
- **Best For**: Income generation on existing stock, mildly bullish to neutral
- **Greeks**: -Delta (capped), +Theta

---

### 4. Volatility Strategies (Volatility Long)

#### Long Straddle
- **Setup**: Buy ATM call + Buy ATM put (same strike, same expiry)
- **Max Profit**: Unlimited
- **Max Loss**: Total premium paid
- **Breakeven**: Strike ± total premium
- **Best For**: Big move expected but direction unknown (earnings, events)
- **Greeks**: Near-zero Delta, +Vega (strong), -Theta (strong)

#### Long Strangle
- **Setup**: Buy OTM call + Buy OTM put (different strikes, same expiry)
- **Max Profit**: Unlimited
- **Max Loss**: Total premium paid (less than straddle)
- **Breakeven**: Wider than straddle
- **Best For**: Big move expected, cheaper than straddle, needs larger move to profit

#### Long Guts
- **Setup**: Buy ITM call + Buy ITM put
- **Best For**: Rare; similar to straddle but higher premium, narrower loss zone

---

### 5. Advanced / Multi-Leg Strategies

#### Calendar Spread (Time Spread)
- **Setup**: Sell near-term option, Buy same-strike far-term option
- **Max Profit**: When stock at strike at near-term expiry
- **Max Loss**: Net debit paid
- **Best For**: Low near-term volatility, higher implied vol in back month
- **Greeks**: +Vega, +Theta (net positive theta from near-term short)

#### Diagonal Spread
- **Setup**: Sell near-term option, Buy far-term option at different strike
- **Max Profit**: Variable
- **Best For**: Directional bias with theta decay benefit

#### Ratio Spread (Call Ratio / Put Ratio)
- **Setup**: Buy 1 option, Sell 2 options at higher/lower strike (same expiry)
- **Max Profit**: Selling strike area
- **Max Loss**: Can be unlimited on uncovered side
- **Best For**: Directional with expectation of limited move; advanced traders only

#### Butterfly Spread
- **Setup**: 
  - Buy 1 low strike, Sell 2 middle strikes, Buy 1 high strike
  - All same expiry, equidistant strikes
- **Max Profit**: At middle strike at expiry
- **Max Loss**: Net debit
- **Best For**: Precise target price with minimal risk

#### Jade Lizard
- **Setup**: Sell OTM put + Sell OTM call spread (bear call spread)
- **Max Profit**: Total credit received (no upside risk if credit > call spread width)
- **Max Loss**: Put strike - total credit (downside)
- **Best For**: Bullish to neutral, eliminates upside risk

#### Broken Wing Butterfly
- **Setup**: Standard butterfly with unequal wing widths
- **Best For**: Directional bias with defined risk on one side, potential credit received

#### PMCC (Poor Man's Covered Call)
- **Setup**: Buy deep ITM long-dated call (LEAPS), Sell near-term OTM call
- **Best For**: Simulates covered call at fraction of capital

---

## Decision Framework: Which Strategy to Use?

```
Market Outlook
├── Strongly Bullish
│   ├── High conviction → Long Call
│   ├── Defined risk/reward → Bull Call Spread
│   └── Own stock → Covered Call (slight upside only)
│
├── Moderately Bullish
│   ├── Income focus → Bull Put Spread (credit)
│   └── Capital efficient → Bull Call Spread (debit)
│
├── Neutral / Sideways
│   ├── Low volatility expected
│   │   ├── Wide range → Iron Condor
│   │   ├── Tight range → Iron Butterfly / Short Straddle
│   │   └── Income on stock → Covered Call
│   └── Elevated IV → Sell premium (straddle, condor)
│
├── Moderately Bearish
│   ├── Income focus → Bear Call Spread (credit)
│   └── Capital efficient → Bear Put Spread (debit)
│
├── Strongly Bearish
│   ├── High conviction → Long Put
│   └── Hedging portfolio → Long Put / Bear Put Spread
│
└── Big Move Expected (No Direction)
    ├── High conviction → Long Straddle
    └── Lower cost → Long Strangle
```

---

## Greeks Quick Reference

| Greek | Meaning | Long Options | Short Options |
|-------|---------|-------------|--------------|
| **Delta** | Price sensitivity to underlying | + (calls) / - (puts) | Opposite |
| **Gamma** | Rate of delta change | + | - |
| **Theta** | Time decay per day | Negative (hurts you) | Positive (helps you) |
| **Vega** | Sensitivity to IV change | + (benefits from IV rise) | - (hurt by IV rise) |
| **Rho** | Sensitivity to interest rates | Minor for most retail trades | Minor |

---

## Key Metrics to Evaluate Any Strategy

1. **Max Profit** — What's the best case?
2. **Max Loss** — What's the worst case?
3. **Breakeven(s)** — Where must the stock be to not lose money?
4. **Probability of Profit (POP)** — Statistical likelihood of making money
5. **Risk/Reward Ratio** — Max profit ÷ Max loss
6. **Days to Expiration (DTE)** — Optimal DTE per strategy
7. **Implied Volatility (IV) Rank** — Is IV high (sell premium) or low (buy premium)?

---

## IV Rank Guide

| IV Rank | Strategy Preference |
|---------|-------------------|
| < 20 | Buy premium (long straddle, long calls/puts) |
| 20–40 | Neutral, directional debit spreads |
| 40–60 | Credit spreads, iron condors |
| > 60 | Sell premium (short straddle, strangle, iron condor) |

---

## Optimal DTE by Strategy Type

| Strategy | Typical DTE |
|----------|------------|
| Short premium (condor, straddle) | 30–45 DTE |
| Long premium (straddle, calls) | 60–90 DTE |
| Calendar spread | Near: 7–14 DTE / Far: 30–60 DTE |
| LEAPS strategies | 6–24 months |
| Earnings plays | 1–7 DTE |

---

## Output Format

When presenting a strategy analysis, always include:

1. **Strategy Name & Setup** (exact legs with strikes, expiry)
2. **Cost / Credit** (net debit or net credit)
3. **Max Profit / Max Loss / Breakeven(s)**
4. **Probability of Profit** (if calculable)
5. **Ideal Market Scenario**
6. **Risk Considerations**
7. **Adjustment Ideas** (if trade goes wrong)

---

## Common Adjustments

| Position Going Wrong | Adjustment |
|---------------------|-----------|
| Long call losing | Roll down or out, convert to spread |
| Short put being tested | Roll down and out to collect more credit |
| Iron condor — one side tested | Roll untested side toward price (inversion); or close |
| Long straddle not moving | Convert to directional by closing one leg |
| Covered call in-the-money | Roll call up and out for credit |
