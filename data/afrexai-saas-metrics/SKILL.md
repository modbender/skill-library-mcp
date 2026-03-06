---
name: SaaS Metrics Dashboard
description: Generate a complete SaaS metrics analysis from your data. Covers
  the 15 metrics that actually matter for B2B SaaS in 2026 — not vanity numbers.
---

# SaaS Metrics Dashboard

Generate a complete SaaS metrics analysis from your data. Covers the 15 metrics that actually matter for B2B SaaS in 2026 — not vanity numbers.

## What It Does

When triggered, this skill:
1. Asks for your current numbers (MRR, churn, CAC, etc.)
2. Calculates derived metrics (LTV:CAC, Magic Number, Rule of 40, Burn Multiple)
3. Benchmarks against 2026 SaaS medians by stage (Pre-Seed → Series C+)
4. Flags red/yellow/green across every metric
5. Outputs a board-ready metrics summary with action items

## Core Metrics Framework

### Revenue Metrics
| Metric | Formula | 2026 Benchmark (Series A) |
|--------|---------|--------------------------|
| **MRR** | Sum of monthly recurring revenue | $80K-$250K |
| **ARR** | MRR × 12 | $1M-$3M |
| **Net Revenue Retention (NRR)** | (Starting MRR + Expansion - Contraction - Churn) / Starting MRR | >110% |
| **Gross Revenue Retention (GRR)** | (Starting MRR - Contraction - Churn) / Starting MRR | >85% |
| **Revenue per Employee** | ARR / Headcount | $150K-$250K |

### Growth Metrics
| Metric | Formula | Healthy Range |
|--------|---------|---------------|
| **MoM Growth** | (This Month MRR - Last Month MRR) / Last Month MRR | 10-20% pre-Series A |
| **Quick Ratio** | (New MRR + Expansion MRR) / (Contraction MRR + Churned MRR) | >4.0 |
| **Magic Number** | Net New ARR (QoQ) / Prior Quarter S&M Spend | >0.75 |

### Unit Economics
| Metric | Formula | Target |
|--------|---------|--------|
| **CAC** | Total S&M Spend / New Customers Acquired | Varies by ACV |
| **LTV** | ARPU × Gross Margin % / Monthly Churn Rate | >3× CAC |
| **LTV:CAC Ratio** | LTV / CAC | 3:1 to 5:1 |
| **CAC Payback** | CAC / (ARPU × Gross Margin %) | <18 months |
| **Gross Margin** | (Revenue - COGS) / Revenue | >70% |

### Efficiency Metrics
| Metric | Formula | Target |
|--------|---------|--------|
| **Rule of 40** | Revenue Growth % + EBITDA Margin % | >40 |
| **Burn Multiple** | Net Burn / Net New ARR | <2.0 |

## Benchmarks by Stage (2026)

| Stage | ARR | NRR | LTV:CAC | Burn Multiple | Rule of 40 |
|-------|-----|-----|---------|---------------|------------|
| Pre-Seed | <$100K | N/A | N/A | <5.0 | N/A |
| Seed | $100K-$1M | >100% | >2:1 | <3.0 | >20 |
| Series A | $1M-$5M | >110% | >3:1 | <2.0 | >30 |
| Series B | $5M-$20M | >115% | >3.5:1 | <1.5 | >35 |
| Series C+ | >$20M | >120% | >4:1 | <1.0 | >40 |

## Red Flag Detection

The skill automatically flags:
- **NRR below 100%** — your bucket is leaking. Fix churn before spending on acquisition.
- **LTV:CAC below 1:1** — you're paying more to acquire customers than they're worth. Stop spending.
- **CAC Payback over 24 months** — capital efficiency problem. Tighten sales cycle or raise ACV.
- **Burn Multiple over 3.0** — burning cash faster than growing. Cut or pivot.
- **Quick Ratio below 1.0** — losing more revenue than gaining. Emergency.
- **Gross Margin below 60%** — not a SaaS business, it's a services business with software.

## How to Use

Tell the agent:
```
Run the SaaS metrics analysis. Here are my numbers:
- MRR: $45,000
- Monthly churn: 3.2%
- New customers this month: 12
- S&M spend this month: $28,000
- ARPU: $380/mo
- Gross margin: 74%
- Headcount: 8
- Monthly burn: $62,000
```

The agent will calculate all derived metrics, benchmark them, and give you a prioritized action list.

## Output Format

```
📊 SaaS METRICS DASHBOARD — [Company] — [Month YYYY]

🟢 HEALTHY          🟡 WATCH           🔴 FIX NOW
─────────────────────────────────────────────────
MRR: $45K           NRR: 104%          Churn: 3.2%
Gross Margin: 74%   Quick Ratio: 2.1   CAC Payback: 22mo
Rule of 40: 38                         LTV:CAC: 2.4:1

TOP 3 ACTIONS:
1. [Most urgent metric fix with specific target]
2. [Second priority with timeline]
3. [Third priority with expected impact]
```

## Industry Adjustments

Different verticals have different healthy ranges:
- **Vertical SaaS** (healthcare, legal, construction): Higher gross margins (80%+), lower churn (<2%), higher ACV
- **Horizontal SaaS** (productivity, analytics): Lower margins, higher volume, faster sales cycles
- **Usage-based** (API, infrastructure): Track consumption metrics alongside traditional SaaS metrics
- **PLG** (product-led growth): Add activation rate, time-to-value, viral coefficient

## Want the Full Picture?

This skill covers metrics. For the complete business operations stack:

🔗 **[AfrexAI Context Packs](https://afrexai-cto.github.io/context-packs/)** — $47 each, 10 industries. Full agent configs with financial models, compliance frameworks, and operational playbooks.

🔗 **[AI Revenue Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/)** — Free tool. See exactly where AI agents save money in your business.

🔗 **[Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/)** — Configure your AI agent stack in 5 minutes.

**Bundle deals:**
- Pick 3 packs — $97
- All 10 packs — $197
- Everything bundle — $247
