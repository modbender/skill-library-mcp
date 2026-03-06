---
name: olo-deal-screening
version: 1.0.0
description: Target company evaluation and deal qualification for PE and strategic buyers
author: ololand.ai
author_url: https://ololand.ai
license: MIT
triggers:
  - deal screening
  - target evaluation
  - investment criteria
  - acquisition criteria
  - deal qualification
  - deal fit
  - buyer criteria
  - deal scoring
tags:
  - finance
  - screening
  - m-and-a
  - due-diligence
  - private-equity
---

# Deal Screening for M&A

Score and qualify acquisition targets against buyer investment criteria.

## Screening Framework

Evaluate targets across five dimensions, each scored 0-100:

### 1. Strategic Fit (25% weight)
- Industry/sector alignment with buyer portfolio
- Geographic fit (markets, operations, customer base)
- Product/service complementarity
- Technology or capability gap fill
- Brand and market position value

### 2. Financial Profile (25% weight)
- Revenue scale (minimum threshold check)
- Revenue growth trajectory (3-year trend)
- EBITDA margin vs. industry benchmark
- Revenue quality (recurring vs. one-time, customer concentration)
- Working capital efficiency

### 3. Valuation Attractiveness (20% weight)
- EV/EBITDA vs. comparable transactions
- EV/Revenue vs. sector median
- Implied IRR at estimated purchase price
- Multiple arbitrage potential (buy low, exit higher)

### 4. Risk Profile (15% weight)
- Customer concentration (top 10 customers as % of revenue)
- Key-person dependency
- Regulatory exposure
- Technology obsolescence risk
- Litigation or compliance issues

### 5. Execution Feasibility (15% weight)
- Management team quality and retention likelihood
- Integration complexity estimate
- Competitive auction dynamics
- Seller motivation and timeline
- Financing availability

## Scoring Output

```
Overall Fit Score: 78/100 — PROCEED TO DD

Strategic Fit:     85/100 ████████░░
Financial Profile: 72/100 ███████░░░
Valuation:         80/100 ████████░░
Risk Profile:      68/100 ██████░░░░
Execution:         82/100 ████████░░

Recommendation: PROCEED TO DD
Key Strengths: [top 3]
Key Concerns: [top 3]
Suggested Next Steps: [prioritized actions]
```

## Thresholds

| Score Range | Recommendation |
|-------------|----------------|
| 80-100 | Strong fit — prioritize for DD |
| 65-79 | Good fit — proceed with caution |
| 50-64 | Marginal — requires strategic justification |
| Below 50 | Poor fit — pass unless compelling thesis |

## Deal-Breaker Checks (Auto-Fail)

Before scoring, check for absolute disqualifiers:
- Revenue below buyer's minimum threshold
- Negative EBITDA (unless growth-stage thesis)
- Active material litigation exceeding 20% of EV
- Sanctioned entities in ownership chain
- Industry explicitly excluded by buyer mandate

## PE-Specific Criteria

For financial sponsor buyers, additionally evaluate:
- **LBO feasibility**: Can the deal be levered 3-5x EBITDA?
- **Value creation levers**: Revenue growth, margin expansion, add-ons, multiple expansion
- **Exit path**: IPO viability, strategic buyer universe, sponsor-to-sponsor
- **Hold period returns**: Target 20-25% gross IRR over 3-5 years
- **Fund fit**: Check size, vintage, sector focus, geographic mandate

## Output Format

Provide structured JSON-compatible output with:
- `overall_score`: 0-100
- `recommendation`: proceed_to_dd | proceed_with_caution | pass
- `dimension_scores`: object with each dimension
- `deal_breakers`: list of any auto-fail conditions triggered
- `strengths`: top 3 positive factors
- `concerns`: top 3 risk factors
- `next_steps`: prioritized action items
