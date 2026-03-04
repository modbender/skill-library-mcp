# Unit Economics Analyzer

Break down your business to the numbers that actually matter. This skill calculates and benchmarks your unit economics — CAC, LTV, payback period, contribution margin — so you know exactly which customers make you money and which ones burn it.

## What It Does

When activated, the agent will:

1. **Calculate Core Metrics**
   - Customer Acquisition Cost (CAC) — fully loaded (ads + sales salaries + tools + overhead)
   - Lifetime Value (LTV) — using both simple and DCF methods
   - LTV:CAC Ratio — the single number investors care about most
   - CAC Payback Period — months to recover acquisition spend
   - Contribution Margin — per unit and per customer

2. **Benchmark Against Industry**
   | Metric | Healthy SaaS | Marketplace | E-commerce | Services |
   |--------|-------------|-------------|------------|----------|
   | LTV:CAC | 3:1 – 5:1 | 2:1 – 4:1 | 1.5:1 – 3:1 | 4:1 – 8:1 |
   | CAC Payback | 12-18 mo | 6-12 mo | 1-3 mo | 3-6 mo |
   | Gross Margin | 70-85% | 40-65% | 30-50% | 50-70% |
   | Net Revenue Retention | 110-130% | 100-115% | 80-100% | 90-110% |

3. **Segment Analysis**
   - Break unit economics by customer segment, channel, plan tier, geography
   - Identify which segments are profitable and which are subsidized
   - Flag "toxic" segments where CAC > LTV

4. **Cohort Decay Modeling**
   - Month-over-month retention curves by acquisition cohort
   - Revenue decay rate and true LTV (not the optimistic version)
   - Churn-adjusted LTV using: `LTV = ARPU × Gross Margin / Monthly Churn Rate`

5. **Scenario Planning**
   - What happens to payback if CAC increases 20%?
   - Impact of 5% churn reduction on LTV
   - Break-even analysis: minimum retention rate for profitability
   - Pricing sensitivity: how price changes flow through to unit economics

## How to Use

Tell the agent:
- "Analyze my unit economics" — walks through full calculation
- "My CAC is $X and monthly churn is Y%" — gets specific benchmarks
- "Compare my SaaS unit economics to benchmarks" — industry comparison
- "Model what happens if we cut churn by 3%" — scenario analysis
- "Break down unit economics by customer segment" — segmentation

## Required Inputs

Provide what you have (the agent will estimate what's missing):

**Revenue side:**
- Average Revenue Per User (ARPU) — monthly or annual
- Gross margin percentage
- Monthly or annual churn rate
- Expansion revenue rate (upsells, cross-sells)

**Cost side:**
- Total sales & marketing spend (monthly/quarterly)
- New customers acquired in same period
- Customer success/support costs per account
- Onboarding costs per customer

## Formulas Reference

```
CAC = Total Sales & Marketing Spend / New Customers Acquired

LTV (Simple) = ARPU × Gross Margin% / Monthly Churn Rate

LTV (DCF) = Σ (Monthly Revenue × Gross Margin%) / (1 + Discount Rate)^month

LTV:CAC Ratio = LTV / CAC  [Target: >3:1]

Payback Period = CAC / (ARPU × Gross Margin%)  [months]

Contribution Margin = (Revenue - Variable Costs) / Revenue

Magic Number = Net New ARR / Prior Quarter S&M Spend  [Target: >0.75]

Burn Multiple = Net Burn / Net New ARR  [Target: <2x]
```

## Red Flags Dashboard

| Signal | Threshold | Action |
|--------|-----------|--------|
| LTV:CAC below 1:1 | Losing money on every customer | Stop acquiring, fix retention or pricing |
| LTV:CAC below 3:1 | Unsustainable at scale | Reduce CAC or increase retention |
| Payback > 24 months | Cash flow risk | Accelerate monetization or cut acquisition |
| Gross margin < 50% | Service business, not software | Re-examine delivery costs |
| Net retention < 100% | Revenue shrinking without new sales | Fix product-market fit |
| CAC trending up > 15% QoQ | Channel saturation | Diversify acquisition channels |
| Magic Number < 0.5 | Inefficient growth spend | Pause scaling, optimize |

## Output Format

The agent produces:
- **Executive Summary** — 3-line verdict on business health
- **Metrics Table** — all calculated values with industry benchmarks
- **Segment Breakdown** — if data provided, per-segment P&L
- **Scenario Matrix** — sensitivity analysis on key variables
- **Action Items** — prioritized list of improvements with expected impact

---

## Get the Full Context

This skill gives you the framework. For industry-specific unit economics benchmarks, valuation context, and implementation playbooks:

→ **[AI Agent Context Packs](https://afrexai-cto.github.io/context-packs/)** — $47 per industry. SaaS, Fintech, Healthcare, E-commerce, and 6 more.

→ **[AI Revenue Leak Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/)** — Free. Find where your business is losing money.

→ **[Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/)** — Free. Configure your AI agent in 5 minutes.

**Bundles:**
- Pick 3 Packs — $97 (save $44)
- All 10 Packs — $197 (save $273)
- Everything Bundle — $247 (all packs + playbook + setup)
