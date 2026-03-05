# Gambling Strategies — Detailed Math

## 1. Flat Bet

**Rule:** Bet constant amount `B` every round.

- Expected profit per round: `E = B × (p × m - 1)` where `p` = win probability, `m` = multiplier
- Variance per round: `σ² = B² × p × (m-1)² + B² × (1-p)`
- For fair coinflip (p=0.5, m=1.98): EV = B × (0.5 × 1.98 - 1) = -0.01B (1% house edge)
- After N rounds: Expected = N × E, Variance = N × σ²

## 2. Martingale

**Rule:** Start at `B`. Double after loss. Reset to `B` after win.

Bet sequence on losing streak of length k: B, 2B, 4B, ... 2^(k-1)B

- Total risked after k losses: `B × (2^k - 1)`
- Win at round k+1 nets: `B` (always profit B on a win)
- Probability of k consecutive losses: `(1-p)^k`
- **Ruin probability** after N rounds with bankroll W: approximately `1 - (1 - (1-p)^⌊log₂(W/B)⌋)^N`
- Expected number of rounds before ruin: `1 / (1-p)^⌊log₂(W/B)⌋`

**Risk:** Bankroll grows linearly, but ruin is catastrophic. With 50/50 odds and 10 max doublings, ruin probability per sequence ≈ 0.1%.

## 3. Anti-Martingale (Paroli)

**Rule:** Start at `B`. Double after win. Reset to `B` after loss.

- Captures streaks: k consecutive wins yields `B × (2^k - 1)` profit
- Typically cap at 3-4 wins then reset
- Lower risk than Martingale (losses limited to B per sequence)
- Expected value same as flat bet in the long run (house edge unchanged)
- But variance profile differs: rare big wins, frequent small losses

## 4. D'Alembert

**Rule:** Start at `B`. After loss: bet += 1 unit. After win: bet -= 1 unit (min B).

- More conservative than Martingale
- After equal wins and losses, profit = (number of wins) × 1 unit
- Bet size grows linearly (not exponentially)
- Max bet after k consecutive losses: `B + k`
- Total risked: `k×B + k(k+1)/2`

## 5. Kelly Criterion

**Rule:** Bet fraction `f*` of current bankroll each round.

```
f* = (b×p - q) / b
```

Where:
- `b` = net odds (payout multiplier - 1)
- `p` = probability of winning
- `q` = 1 - p

For coinflip with 1.98× payout:
- b = 0.98, p = 0.5, q = 0.5
- f* = (0.98 × 0.5 - 0.5) / 0.98 = -0.01/0.98 ≈ -0.0102

**Negative f* means no bet** — Kelly says don't play with negative EV. However, for research purposes, you can use fractional Kelly (e.g., f*/4) to study the variance characteristics.

For games with positive EV (e.g., promotional bonuses):
- Example: 2.1× payout, 50% win → f* = (1.1×0.5 - 0.5)/1.1 = 0.0455 (bet 4.55% of bankroll)

## Comparison Table

| Strategy | Risk | Bet Growth | Bankroll Requirement | Best For |
|----------|------|-----------|---------------------|----------|
| Flat Bet | Low | None | Low | Baseline testing |
| Martingale | Very High | Exponential | Very High | Short sessions |
| Anti-Martingale | Low | Exponential (wins only) | Low | Streak capture |
| D'Alembert | Medium | Linear | Medium | Conservative play |
| Kelly | Optimal | Proportional | Dynamic | Long-term growth |
