# Decision Engine Guide

## Overview

The decision engine combines historical JSON learning data to generate **trade decisions, scenario projections, and risk evaluations**.

| Feature | Description |
|---|---|
| **Lesson matching** | Checks for known avoid conditions before entering a trade |
| **Pattern recognition** | Identifies reusable successful patterns |
| **Scenario simulation** | Projects outcomes based on historical trade data |
| **Decision generation** | buy / sell / wait + confidence score + parameter suggestions |
| **Decision log** | Records every decision for post-trade review |

---

## Commands

### 1. Generate a trade decision

```bash
python3 okx_decision.py decision <coin> <signal> <market_regime> <price> [rsi]
```

**Examples:**
```bash
# BTC ranging market, SELL signal, price 67361, RSI 50
python3 okx_decision.py decision BTC-USDT-SWAP SELL ranging 67361 50

# ETH strong bull market, BUY signal, price 2235, RSI 45
python3 okx_decision.py decision ETH-USDT-SWAP BUY strong_bull 2235 45
```

**Sample output:**
```
============================================================
Decision
============================================================
Coin:          BTC-USDT-SWAP
Signal:        SELL
Market regime: ranging
Price:         67361.0
RSI:           50.0
------------------------------------------------------------
Decision:      WAIT
Confidence:    0%
------------------------------------------------------------
Warning: Avoid — lesson#signal_divergence: MA/MACD produced 61 consecutive false SELL signals in ranging market

Success patterns (2):
  - ETH-USDT-SWAP_BUY_strong_bull: win rate 80%, avg profit 8.50%
  - BUY signal in strong_bull returned +12.3%

Reasons:
  Ranging market — confidence weight reduced 50%
  Confidence below 30% — recommend wait

Suggested parameters:
  Position: 50 USDT
  Leverage: 3x
  Stop loss: 3.0%
  Take profit: 15.0%

Scenario simulation:
  Sample size: 25 historical trades
  Historical win rate: 58.0%
  Expected value: +12.50 USDT
  Bull case  (+30% probability): +15.0%
  Base case  (+50% probability): +2.5%
  Bear case  (+20% probability): -3.0%
============================================================
```

---

### 2. View decision history

```bash
python3 okx_decision.py summary [limit]
```

**Example:**
```bash
python3 okx_decision.py summary 10
```

**Output:**
```
Last 10 decisions:

2026-02-27T21:15:00 | BTC-USDT-SWAP   | WAIT   | 0%    | Ranging market — weight reduced
2026-02-27T21:00:00 | ETH-USDT-SWAP   | BUY    | 70%   | RSI 28.5 < 30 (oversold), strong bull + BUY signal aligned
2026-02-27T20:45:00 | SOL-USDT-SWAP   | AVOID  | 0%    | Failed pattern: win rate 25.0%
```

---

### 3. Scenario simulation

```bash
python3 okx_decision.py simulate <coin> <direction> <price> <position_usdt> <leverage> <sl> <tp>
```

**Example:**
```bash
python3 okx_decision.py simulate ETH-USDT-SWAP long 2235 50 3 0.03 0.15
```

**Output:**
```json
{
  "status": "simulated",
  "sample_size": 25,
  "historical_win_rate": "58.0%",
  "avg_win": "6.50%",
  "avg_loss": "-2.80%",
  "scenarios": {
    "bull_case":  { "probability": 0.3, "outcome": "+15.0%", "pnl_usdt": 22.5 },
    "base_case":  { "probability": 0.5, "outcome": "+2.5%",  "pnl_usdt": 3.75 },
    "bear_case":  { "probability": 0.2, "outcome": "-3.0%",  "pnl_usdt": -4.5 }
  },
  "expected_value_usdt": "8.40"
}
```

---

### 4. Check avoid conditions

```bash
python3 okx_decision.py avoid <coin> <signal> <market_regime>
```

**Example:**
```bash
python3 okx_decision.py avoid BTC-USDT-SWAP SELL ranging
```

**Output:**
```
Avoid: lesson#signal_divergence — MA/MACD produced 61 consecutive false SELL signals in ranging market
```

---

## Decision Logic

### Flow

```
1. Load JSON data (lessons, patterns, journal)
   ↓
2. Check avoid conditions (lessons.json)
   → match found → Decision: AVOID
   ↓
3. Check success patterns (patterns.json)
   → match found → confidence +30%
   ↓
4. RSI extremes
   → RSI < 30 → Decision: BUY,  confidence +30%
   → RSI > 70 → Decision: SELL, confidence +30%
   ↓
5. Market regime + signal alignment
   → strong_bull + BUY  → Decision: BUY,  confidence +40%
   → strong_bear + SELL → Decision: SELL, confidence +40%
   → ranging             → confidence ×50%
   ↓
6. Suggest parameters (based on historical optimals)
   ↓
7. Run scenario simulation (based on historical trades)
   ↓
8. Confidence < 30% → Decision: WAIT
   ↓
9. Log decision
```

---

### Confidence Calculation

| Factor | Weight |
|---|---|
| RSI extreme (< 30 or > 70) | +30% |
| Market regime + signal alignment | +40% |
| Successful pattern match (each) | +10–30% |
| Ranging market | ×50% |
| Avoid condition match | → AVOID |

**Decision thresholds:**
- ≥ 70%: High confidence — recommended to execute
- 30–70%: Medium confidence — can execute with caution
- < 30%: Low confidence — wait

---

## Data Files

| File | Purpose | How the engine uses it |
|---|---|---|
| `okx-learning-model.json` | Core learning model | Reads optimal parameters |
| `okx-trade-journal.json` | Trade records | Scenario simulation samples |
| `okx-lessons.json` | Learned lessons | Avoid condition checks |
| `okx-patterns.json` | Trade patterns | Success pattern matching |
| `okx-monitoring-log.json` | Monitor sessions | Market regime inference |
| `okx-decision-log.json` | Decision log | Records all decisions |

---

## Practical Examples

### Case 1: BTC ranging market, consecutive SELL signals

```bash
python3 okx_decision.py decision BTC-USDT-SWAP SELL ranging 67361 50
```

**Output:**
```
Decision:   AVOID
Confidence: 0%
Warning:    lesson#signal_divergence — 61 consecutive SELL signals, price moved +476 pts against signal
```

---

### Case 2: ETH strong bull market, oversold RSI

```bash
python3 okx_decision.py decision ETH-USDT-SWAP BUY strong_bull 2235 28
```

**Output:**
```
Decision:   BUY
Confidence: 85%
  RSI 28.0 < 30 (oversold)
  Strong bull + BUY signal aligned
  Success pattern: ETH_BUY_strong_bull win rate 80%

Suggested parameters:
  Position:    75 USDT (pattern bonus)
  Leverage:    3x
  Stop loss:   3.0%
  Take profit: 18.0% (pattern bonus)

Scenario simulation:
  Historical win rate: 80.0%
  Expected value: +18.50 USDT
```

---

### Case 3: SOL failed pattern

```bash
python3 okx_decision.py decision SOL-USDT-SWAP SELL ranging 84 45
```

**Output:**
```
Decision:   AVOID
Confidence: 0%
Warning:    Failed pattern — SOL SELL in ranging market win rate 25%
```

---

## Integration

Calling the decision engine from `okx.py`:

```python
from okx_decision import DecisionEngine

engine = DecisionEngine()
decision = engine.generate_decision(
    coin="BTC-USDT-SWAP",
    signal="BUY",
    market_regime="strong_bull",
    current_price=67000,
    rsi=35
)

if decision["decision"] == "buy" and decision["confidence"] > 0.7:
    execute_trade(decision["parameters"])
elif decision["decision"] == "avoid":
    print(f"Avoid: {decision['avoid_warning']}")
```

---

## Roadmap

1. **Backtesting** — validate decisions against historical price data
2. **A/B testing** — compare parameter combinations
3. **Auto-tuning** — adjust confidence weights based on decision accuracy
4. **Multi-timeframe** — combine 1H / 4H / 1D signals
5. **Sentiment overlay** — integrate external sentiment indicators
