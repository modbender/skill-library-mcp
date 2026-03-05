# Equity Analysis Framework

This document details the strict evaluation framework used by the equity-analyst skill.

## Priority Order (Read First)

1. **Financial Fundamentals** (highest priority - has veto power)
2. **News & Outlook**
3. **Technical Chart Indicators** (lowest priority - timing only)

Financial score can NEVER be overridden by News or Technical factors.

---

## STEP 1: FINANCIAL SCORE (50% of final)

### Scoring Tables

#### A. Valuation (PER, PBR) - 30% weight

| PER Level | Score | Note |
|-----------|-------|------|
| < 10 | 90-100 | Exceptionally cheap |
| 10-15 | 80-89 | Very attractive |
| 15-20 | 70-79 | Fair value |
| 20-30 | 50-69 | Slightly expensive |
| 30-40 | 30-49 | Expensive |
| > 40 | 0-29 | Very expensive (unless >30% growth) |

| PBR Level | Score | Note |
|-----------|-------|------|
| < 0.8 | 90-100 | Deep discount to book |
| 0.8-1.2 | 80-89 | Near or below book |
| 1.2-2.0 | 70-79 | Slight premium |
| 2.0-3.0 | 50-69 | Moderate premium |
| 3.0-5.0 | 30-49 | High premium |
| > 5.0 | 0-29 | Very high premium |

**Combine PER and PBR**: Average the two scores for final ValuationScore.

#### B. Profitability (ROE, Operating Margin) - 30% weight

| ROE Level | Score | Note |
|-----------|-------|------|
| > 20% | 90-100 | Exceptional |
| 15-20% | 80-89 | Excellent |
| 10-15% | 70-79 | Good |
| 5-10% | 50-69 | Moderate |
| 3-5% | 30-49 | Weak |
| < 3% | 0-29 | Critically weak |

| Operating Margin Level | Score | Note |
|------------------------|-------|------|
| > 20% | 90-100 | High margin business |
| 15-20% | 80-89 | Good margins |
| 10-15% | 70-79 | Decent margins |
| 5-10% | 50-69 | Average |
| 0-5% | 30-49 | Low margins |
| < 0% | 0-29 | Negative (loss-making) |

**Combine**: Average ROE score and Operating Margin score.

#### C. Growth (Revenue Growth) - 25% weight

| Revenue Growth (YoY) | Score | Note |
|---------------------|-------|------|
| > 30% | 90-100 | Explosive growth |
| 20-30% | 80-89 | Strong growth |
| 10-20% | 70-79 | Good growth |
| 5-10% | 50-69 | Modest growth |
| 0-5% | 30-49 | Stagnation |
| < 0% | 0-29 | Decline |

**Use multi-year trend**: Prere consistent 3-year trend. If volatile, use average.

#### D. Stability (Debt Ratio) - 15% weight

| Debt Ratio | Score | Note |
|------------|-------|------|
| < 30% | 90-100 | Very low leverage |
| 30-50% | 80-89 | Conservative |
| 50-80% | 70-79 | Moderate |
| 80-100% | 50-69 | High |
| 100-150% | 30-49 | Very high |
| > 150% | 0-29 | Extreme leverage |

**Note**: Some industries (financial, utilities) naturally have higher debt. Adjust slightly if industry context is clear (max +10 points).

#### Financial Score Calculation

```
FinancialScore =
    ValuationScore × 0.30 +
    ProfitabilityScore × 0.30 +
    GrowthScore × 0.25 +
    StabilityScore × 0.15
```

**Special Rule (Veto Cap)**:
If **both** ProfitabilityScore < 30 **and** GrowthScore < 30, then MAXIMUM FinancialScore = 50.
This prevents low-quality companies from scoring high on valuation/stability alone.

---

## STEP 2: NEWS & OUTLOOK SCORE (25%)

### Evaluation Criteria

**Positive Catalysts** (raise score):
- Strong earnings beat/revenue upside
- New major contracts or partnerships
- Regulatory approvals, market expansion
- Industry tailwinds (e.g., AI boom, policy support)
- Analyst upgrades, positive sentiment shift

**Negative Catalysts** (lower score):
- Earnings miss, guidance cut
- Customer losses, litigation
- Regulatory setbacks, industry headwinds
- Analyst downgrades, negative sentiment

**Neutral/Uncertain**:
- Mixed signals, waiting for next earnings
- No major recent news
- Industry uncertain

### Scoring Guide

| News Tone | Score Range | Rationale |
|-----------|-------------|-----------|
| Very positive, multiple strong catalysts | 80-100 | High conviction |
| Positive, clear tailwinds | 65-79 | Favorable outlook |
| Neutral/mixed | 40-64 | Wait-and-see |
| Some concerns but not critical | 30-39 | Cautious |
| Very negative, major red flags | 0-29 | Avoid |

**Critical Rule**: Hype without financial backing (e.g., "metaverse", "AI buzzword" without revenue) MUST NOT score above 60. Score based on tangible impact.

---

## STEP 3: TECHNICAL / CHART SCORE (25%)

### What to Evaluate (Simple Only)

**Trend Direction**:
- Up: Higher highs and higher lows
- Sideways: Range-bound
- Down: Lower highs and lower lows

**Current Price Position** (relative to 52-week range):
- Near 52w low: potential accumulation
- Near 52w high: possible distribution
- Mid-range: neutral

**Volume**:
- Expanding volume on up moves: bullish
- Expanding volume on down moves: bearish
- Contracting volume: consolidation
- Average volume: neutral

**Timing Implication**:
- Good entry/exit points based on current chart

### Scoring Guide

| Chart Condition | Score | Rationale |
|-----------------|-------|-----------|
| Strong uptrend, good entry point | 70-100 | Buy on pullback |
| Emerging uptrend, early stage | 60-79 | Accumulating |
| Sideways consolidation | 40-59 | Wait for breakout |
| Downtrend but near support | 30-39 | Avoid or short |
| Strong downtrend, distribution | 0-29 | High risk |

**Critical Rule**: Technicals are TIMING-ONLY. A stock with terrible fundamentals (FinancialScore < 40) can NOT get high ChartScore. Maximum justified score for poor fundamentals is 40 (waiting for better entry is irrelevant if business is broken).

---

## FINAL SCORE & VERDICT

```
FinalScore = (FinancialScore × 0.50) + (NewsScore × 0.25) + (ChartScore × 0.25)
```

### Verdict Mapping

| FinalScore | Verdict | Action |
|------------|---------|--------|
| 80-100 | BUY | Strong conviction, consider significant allocation |
| 65-79 | BUY_LEAN | Cautious buy, small position or accumulate on dips |
| 45-64 | HOLD | Neutral, wait for better entry or exit |
| < 45 | AVOID | Too risky or unattractive |

---

## Output Format Checklist

- [ ] Financial Breakdown section with 5 lines (Valuation, Profitability, Growth, Stability, Financial)
- [ ] NewsScore line
- [ ] ChartScore line
- [ ] Final Investment Attractiveness Score: XX / 100
- [ ] Verdict: one of BUY, BUY_LEAN, HOLD, AVOID
- [ ] Reasoning Summary: ONE paragraph only, respecting priority order
- [ ] No investment advice (no "you should buy", use "score suggests")
- [ ] Conservative, logic-driven language
- [ ] No exaggeration

---

## Common Pitfalls to Avoid

1. **Reversing priority**: Never let News or Technicals override Financials.
2. **Hype traction**: Don't give high NewsScore for unproven stories.
3. **Chart over-analysis**: Keep it simple - trend + timing.
4. **Valuation ignoring growth**: High PER may be justified by >30% growth.
5. **Sector ignorance**: Adjust Stability for capital-intensive vs asset-light businesses (but only slight adjustment, max +10).

---

## Framework Philosophy

This framework is **conservative by design**:
- Financials are 50% weight and have veto power (special rule)
- News requires tangible catalysts, not speculation
- Technicals only matter for timing, not intrinsic value
- Low financial scores cap overall attractiveness regardless of hype

The goal: filter out hype, find fundamentally sound companies at reasonable valuations with positive catalysts.
