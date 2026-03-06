---
name: trade-validation
description: |
  10-dimension weighted scoring framework for prediction market trade evaluation.
  Enforces disciplined position sizing, circuit breakers, and mandatory counter-arguments.

  Use when: evaluating prediction market trades, scoring opportunities, deciding position sizes,
  comparing Polymarket/Kalshi opportunities, running pre-trade checklists.

  Don't use when: general crypto analysis, DeFi yield farming, non-prediction-market investments,
  stock/equity analysis, sports betting (different framework needed).

  Negative examples:
  - "Should I buy ETH?" → No. This is for prediction markets with binary/discrete outcomes.
  - "What's the best DeFi yield?" → No. Wrong domain entirely.
  - "Score this sports bet" → No. Sports betting has different dimensions (injuries, matchups).

  Edge cases:
  - Crypto prediction markets (e.g., "Will BTC hit $X?") → YES, use this if on Polymarket/Kalshi.
  - Multi-outcome markets → Score each outcome separately.
  - Markets with <$25 liquidity → Auto-fail on Liquidity dimension.
version: "1.0"
---

# Trade Validation — 10-Dimension Scoring Framework

> **Rule: NO trade executes without 80%+ weighted confidence score.**
> **Any single dimension below 4/10 = AUTOMATIC VETO.**

---

## Scoring Dimensions

| # | Dimension | Weight | What It Measures |
|---|-----------|--------|-----------------|
| 1 | Information Edge | 18% | Do we know something the market doesn't? |
| 2 | Source Quality | 12% | How reliable are our sources? |
| 3 | Market Efficiency | 10% | Is this market likely mispriced? |
| 4 | Time Horizon | 8% | How long is capital locked up? |
| 5 | Downside Protection | 15% | What's the worst case? |
| 6 | Cross-Validation | 12% | Do multiple independent signals agree? |
| 7 | Historical Accuracy | 5% | Track record on similar bets? |
| 8 | Liquidity/Execution Risk | 7% | Can we get in AND out? |
| 9 | Consensus Divergence | 8% | How far are we from market consensus? |
| 10 | Event Catalyst | 5% | Is there a known resolution trigger? |

**Total: 100%**

### Calculation

```
Weighted Score = Σ(dimension_score / 10 × weight) × 100
```

---

## Threshold Rules

| Weighted Score | Action | Bet Size |
|---------------|--------|----------|
| < 80% | ❌ NO TRADE | $0 |
| 80–84% | ✅ Minimum | $3–5 |
| 85–89% | ✅ Standard | $5–7 |
| 90%+ | ✅ Conviction | Up to $7.50 (max 10% bankroll) |

### Veto Rules

- **Any dimension < 4/10 → AUTOMATIC VETO** regardless of total score
- Rationale: A critical weakness in any area (e.g., Liquidity = 2 means you're trapped)

---

## Risk Management

- **Max position:** 10% of portfolio per trade
- **Min market liquidity:** $25 (below this, don't trade)
- **Max open exposure:** 30% of bankroll across all positions
- **Daily loss circuit breaker:** $8 loss in a day → ALL trading stops for 24 hours
- **Cool-down:** No trade within 1 hour of a loss
- **No revenge trading:** Last loss must be >24h ago OR new trade is unrelated
- **No trading 12am–7am** unless time-critical

---

## Mandatory Counter-Arguments

Every trade MUST document:
1. **Why could we be WRONG?** (not a strawman — a genuine strong counter-argument)
2. **What would change our mind?** (specific falsification criteria)
3. **Exit strategy:** When do we sell early?

---

## Score Card Template

```
TRADE SCORE CARD
═══════════════════════════════════════════════════════════
Market: [name]
Date: [date]
Position: [YES/NO @ price]

 #  Dimension              Weight   Score   Weighted
─── ────────────────────── ──────── ─────── ──────────
 1  Information Edge        18%     __/10   __._%
 2  Source Quality           12%     __/10   __._%
 3  Market Efficiency        10%     __/10   __._%
 4  Time Horizon              8%     __/10   __._%
 5  Downside Protection      15%     __/10   __._%
 6  Cross-Validation         12%     __/10   __._%
 7  Historical Accuracy       5%     __/10   __._%
 8  Liquidity/Execution       7%     __/10   __._%
 9  Consensus Divergence      8%     __/10   __._%
10  Event Catalyst             5%     __/10   __._%
─── ────────────────────── ──────── ─────── ──────────
                    TOTAL   100%            __._%

Minimum Score: __/10 (dimension: _____________)
VETO Check: [ ] All dimensions ≥ 4 — PASS / FAIL

Counter-argument: ________________________________
What would change our mind: _____________________
Exit strategy: __________________________________

RESULT: TRADE / NO TRADE
Tier: [ ] Min ($3-5)  [ ] Standard ($5-7)  [ ] Conviction ($7.50)
═══════════════════════════════════════════════════════════
```

---

## Pre-Trade Checklist

```
RESEARCH
  [ ] Minimum 3 independent sources consulted
  [ ] Sources documented with links
  [ ] Strong counter-argument documented
  [ ] Counter-argument is genuine (not strawman)

SCORING
  [ ] All 10 dimensions scored
  [ ] Weighted score ≥ 80%
  [ ] No dimension below 4/10
  [ ] Score logged to trade journal

RISK
  [ ] Current bankroll: $______
  [ ] Bet ≤ 10% of bankroll
  [ ] Total open exposure ≤ 30%
  [ ] Daily loss < $8 (circuit breaker not triggered)

DISCIPLINE
  [ ] Cool-down respected (1h since last loss)
  [ ] Not revenge trading
  [ ] Not trading 12am–7am
```

---

## Detailed Scoring Rubric

See `references/scoring-rubric.md` for the full 1–10 rubric for each dimension.

## Trade Journal

Log every scored trade (pass or fail) to `projects/polymarket/trade-journal/`:

```
## [DATE] — [MARKET NAME]
- **Score:** XX.X%
- **Result:** TRADE / NO TRADE / VETO
- **Position:** YES/NO @ XXc | **Stake:** $X.XX
- **Outcome:** WIN / LOSS / PENDING
- **P&L:** +/- $X.XX
- **Lesson:** (post-resolution)
```
