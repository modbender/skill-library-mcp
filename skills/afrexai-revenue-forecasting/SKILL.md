# Revenue Forecasting Engine

Build accurate, data-driven revenue forecasts your board and investors actually trust.

## What This Does

Generates a complete revenue forecasting model covering:

1. **Pipeline-Weighted Forecast** — Apply stage-specific close rates to your current pipeline
2. **Cohort Analysis** — Track revenue by customer cohort with expansion/contraction/churn
3. **Scenario Modeling** — Bear/base/bull projections with probability weighting
4. **Seasonality Adjustments** — Monthly coefficients based on your historical patterns
5. **Leading Indicators** — Track signals that predict revenue 60-90 days out

## Instructions

When the user asks for a revenue forecast, follow this framework:

### Step 1: Gather Inputs
Ask for (or use available data):
- Current MRR/ARR
- Pipeline by stage with deal values
- Historical close rates by stage
- Average sales cycle length
- Net revenue retention rate
- Expansion revenue %

### Step 2: Build the Pipeline Forecast

**Stage-Weighted Model:**

| Stage | Probability | Weighted Value |
|-------|------------|----------------|
| Discovery | 10% | Deal × 0.10 |
| Demo/Eval | 25% | Deal × 0.25 |
| Proposal Sent | 50% | Deal × 0.50 |
| Negotiation | 75% | Deal × 0.75 |
| Verbal Commit | 90% | Deal × 0.90 |
| Closed Won | 100% | Deal × 1.00 |

**Adjustment factors:**
- Deal age penalty: -5% per month past avg cycle
- Champion risk: -20% if no identified champion
- Budget confirmed: +10% if budget is allocated
- Competitive deal: -15% if competitor identified

### Step 3: Cohort Revenue Model

Track each monthly cohort:
```
Month 0: New MRR from cohort
Month 1: Retained MRR × (1 - monthly churn rate)
Month 3: Add expansion revenue (avg 2-5% monthly for healthy SaaS)
Month 6: Steady-state retention rate applies
Month 12: Mature cohort — use net revenue retention
```

**Benchmarks by company stage:**
| Metric | Seed | Series A | Series B+ |
|--------|------|----------|-----------|
| Gross Churn | 3-5%/mo | 2-3%/mo | 1-2%/mo |
| Net Retention | 90-100% | 100-110% | 110-130% |
| Expansion % | 5-10% | 10-20% | 20-40% |
| CAC Payback | 18-24 mo | 12-18 mo | 6-12 mo |

### Step 4: Scenario Analysis

**Bear Case (20% probability):**
- Pipeline closes at 60% of weighted value
- Churn increases 50%
- No expansion revenue
- 1 key deal slips each quarter

**Base Case (60% probability):**
- Pipeline closes at weighted value
- Current retention rates hold
- Historical expansion rate
- Normal seasonality

**Bull Case (20% probability):**
- Pipeline closes at 120% of weighted value
- Retention improves 10%
- Expansion accelerates 25%
- 1 surprise large deal per quarter

**Expected Value = (Bear × 0.2) + (Base × 0.6) + (Bull × 0.2)**

### Step 5: Seasonality Coefficients

Apply monthly adjustment factors:
| Month | B2B SaaS | Ecommerce | Professional Services |
|-------|----------|-----------|---------------------|
| Jan | 0.85 | 0.70 | 0.90 |
| Feb | 0.90 | 0.75 | 0.95 |
| Mar | 1.05 | 0.85 | 1.10 |
| Apr | 1.00 | 0.90 | 1.00 |
| May | 0.95 | 0.90 | 0.95 |
| Jun | 1.10 | 0.95 | 1.05 |
| Jul | 0.85 | 0.85 | 0.85 |
| Aug | 0.80 | 0.90 | 0.80 |
| Sep | 1.10 | 1.00 | 1.10 |
| Oct | 1.05 | 1.05 | 1.05 |
| Nov | 1.15 | 1.40 | 1.10 |
| Dec | 1.20 | 1.75 | 1.15 |

### Step 6: Leading Indicators Dashboard

Track these weekly — they predict revenue 60-90 days out:

| Indicator | Weight | Signal |
|-----------|--------|--------|
| Qualified pipeline created | 25% | New opps entering Stage 2+ |
| Demo-to-proposal rate | 20% | Conversion velocity |
| Average deal size trend | 15% | Moving up or down? |
| Sales cycle length | 15% | Getting longer = red flag |
| Inbound lead volume | 10% | Marketing effectiveness |
| Website trial signups | 10% | Self-serve demand |
| Customer NPS/CSAT | 5% | Retention predictor |

### Step 7: Output Format

Present the forecast as:

```
REVENUE FORECAST — [Period]
================================
Current ARR: $X
Pipeline (Weighted): $X
Expected New ARR: $X

12-Month Projection:
  Bear:  $X (20%)
  Base:  $X (60%)
  Bull:  $X (20%)
  Expected: $X

Key Risks:
  1. [Risk] — [Mitigation]
  2. [Risk] — [Mitigation]

Leading Indicators:
  🟢 [Healthy metric]
  🟡 [Watch metric]
  🔴 [Concerning metric]

Next Month Actions:
  1. [Specific action]
  2. [Specific action]
```

## Red Flags to Call Out

- Pipeline coverage < 3x target = high risk
- >40% of forecast from 1-2 deals = concentration risk
- Average deal age exceeding 1.5x normal cycle = stalling
- Declining demo-to-close rate = product-market fit erosion
- Rising CAC payback period = unit economics degrading

## Revenue Recognition Notes

- SaaS: Recognize ratably over contract term
- Services: Recognize on delivery/milestones
- Usage-based: Recognize on consumption
- Annual prepay: Deferred revenue, recognize monthly

---

*Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — AI context packs for business operators who ship.*

**Get the full toolkit:**
- [AI Revenue Leak Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/) — Find where you're losing money
- [Context Packs](https://afrexai-cto.github.io/context-packs/) — Industry-specific AI agent configs ($47/pack)
- [Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/) — Deploy your first AI agent in 15 minutes

**Bundles:** Playbook $27 | Pick 3 for $97 | All 10 for $197 | Everything Bundle $247
