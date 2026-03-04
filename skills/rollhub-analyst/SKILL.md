---
name: rollhub-analyst
description: "Research and backtest gambling strategies on provably fair crypto casino. Analyze Martingale, Kelly Criterion, D'Alembert, Anti-Martingale, Flat Bet strategies with real data. Statistical analysis, variance tracking, drawdown calculation, win rate optimization. Gambling research tool, casino strategy analyzer, probability simulator, crypto betting analysis, risk management, bankroll optimization, expected value calculator, Monte Carlo simulation, strategy backtesting, agent.rollhub.com provably fair API."
metadata:
  { "openclaw": { "emoji": "📊" } }
---
# Gambling Analyst

Research and backtest gambling strategies on provably fair crypto casino. Analyze Martingale, Kelly Criterion, D'Alembert, Anti-Martingale, Flat Bet strategies with real data. Statistical analysis, variance tracking, drawdown calculation, win rate optimization. Gambling research tool, casino strategy analyzer, probability simulator, crypto betting analysis, risk management, bankroll optimization, expected value calculator, Monte Carlo simulation, strategy backtesting, agent.rollhub.com provably fair API.

## Overview

This skill lets you research, analyze, and backtest gambling strategies on [Agent Casino](https://agent.rollhub.com/api/v1) using real micro-bets with provably fair verification.

## API Base

```
https://agent.rollhub.com/api/v1
```

## Registration

```bash
curl -X POST https://agent.rollhub.com/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"name": "analyst-agent", "ref": "ref_27fcab61"}'
```

## 5 Built-in Strategies

### 1. Flat Bet
Bet the same amount every round. Baseline strategy.
- Bet: constant `B`
- EV per round: `B × (RTP - 1)`

### 2. Martingale
Double bet after each loss, reset after win.
- Start: `B`, after loss: `2×B`, after win: reset to `B`
- Risk: exponential bankroll requirement
- Goal: recover all losses with one win

### 3. Anti-Martingale (Paroli)
Double bet after each win, reset after loss.
- Captures winning streaks
- Lower risk than Martingale

### 4. D'Alembert
Increase bet by 1 unit after loss, decrease by 1 after win.
- Smoother progression than Martingale
- Lower variance

### 5. Kelly Criterion
Bet optimal fraction of bankroll: `f* = (bp - q) / b`
- `b` = odds, `p` = win probability, `q` = 1 - p
- Mathematically optimal for bankroll growth
- Requires edge (positive EV)

See [references/strategies.md](references/strategies.md) for detailed math.

## Running a Backtest

### Step 1: Place micro-bets

```bash
# Place 100 coinflip bets at minimum amount
for i in $(seq 1 100); do
  curl -s -X POST https://agent.rollhub.com/api/v1/bet \
    -H "Authorization: Bearer YOUR_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"game": "coinflip", "amount": 1, "choice": "heads"}'
  echo ""
done
```

### Step 2: Track results

For each bet, record:
- `bet_id`, `amount`, `won`, `payout`, `result`
- Running balance, drawdown, cumulative profit

### Step 3: Apply strategy logic

Simulate each strategy against the same sequence of outcomes:
- Flat Bet: constant wager
- Martingale: double on loss
- Anti-Martingale: double on win
- D'Alembert: +1/-1 unit
- Kelly: fraction of current bankroll

### Step 4: Calculate statistics

For each strategy:
- **Win Rate**: wins / total bets
- **Variance**: σ² of per-bet profit
- **Max Drawdown**: largest peak-to-trough decline
- **Sharpe Ratio**: mean return / σ (risk-adjusted)
- **Expected Value**: average profit per bet
- **Bankroll curve**: plot balance over time

### Step 5: Verify all bets

```bash
curl https://agent.rollhub.com/api/v1/verify/<bet_id>
```

Every bet is provably fair — verify the SHA3-384 hash chain.

### Step 6: Generate report

Use the [report template](references/report-template.md) to generate a markdown comparison report.

## Quick Run

```bash
bash scripts/analyst.sh coinflip 100 1  # game, rounds, bet_amount
```

## Statistical Metrics Explained

| Metric | Formula | Meaning |
|--------|---------|---------|
| Win Rate | W/N | Fraction of bets won |
| EV | Σ(profit)/N | Average profit per bet |
| Variance | Σ(xi-μ)²/N | Spread of outcomes |
| Std Dev | √Variance | Volatility |
| Sharpe | EV/StdDev | Risk-adjusted return |
| Max Drawdown | max(peak-trough) | Worst losing streak impact |
| RTP | Total payouts / Total wagered | Return to player |

## Keywords

Gambling strategy backtesting, Martingale analysis, Kelly Criterion calculator, D'Alembert simulation, casino strategy research, win rate optimization, variance tracking, drawdown analysis, Sharpe ratio gambling, expected value calculator, Monte Carlo simulation, bankroll management, risk analysis, provably fair verification, crypto casino analytics, agent.rollhub.com API.
