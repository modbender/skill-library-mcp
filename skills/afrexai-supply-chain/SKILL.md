---
name: Supply Chain Risk Monitor
description: Analyze supply chain vulnerabilities, map supplier dependencies,
  and generate risk mitigation plans.
---

# Supply Chain Risk Monitor

Analyze supply chain vulnerabilities, map supplier dependencies, and generate risk mitigation plans.

## What It Does

Given your supplier list or industry context, this skill:

1. **Maps dependencies** — Tier 1, 2, 3 supplier concentration risk
2. **Scores vulnerabilities** — Geographic, single-source, lead time, financial health
3. **Generates mitigation plans** — Dual-sourcing strategies, safety stock calculations, nearshoring options
4. **Creates dashboards** — Risk heat maps, supplier scorecards, disruption scenario modeling

## How to Use

Tell your agent:
- "Assess supply chain risk for our top 10 suppliers"
- "Create a supplier diversification plan"
- "Model the impact of a 30-day disruption from our China suppliers"
- "Score our supply chain resilience"

## Risk Scoring Framework

| Factor | Weight | Score 1 (Low Risk) | Score 5 (Critical) |
|--------|--------|-------------------|---------------------|
| Single-source dependency | 25% | 3+ qualified suppliers | Sole source, no backup |
| Geographic concentration | 20% | Multi-region sourcing | Single country/port |
| Lead time volatility | 15% | <5% variance | >30% variance |
| Financial health | 15% | Strong balance sheet | Distressed/unknown |
| Compliance risk | 10% | Fully audited | No visibility |
| Substitutability | 10% | Drop-in alternatives exist | Custom/proprietary |
| Inventory buffer | 5% | 60+ days safety stock | JIT, no buffer |

**Composite Score**: Weighted average → Green (1-2), Yellow (2.5-3.5), Red (4-5)

## Disruption Cost Formula

```
Daily Impact = (Revenue at Risk × Margin) + Expediting Costs + Customer Penalties + Brand Damage
Recovery Time = Lead Time × (1 + Qualification Factor)
Total Exposure = Daily Impact × Recovery Time
```

## Output Formats

- **Executive summary** — Top 5 risks, total exposure, recommended actions
- **Supplier scorecard** — Individual risk profiles with improvement targets
- **Scenario analysis** — What-if modeling for major disruptions
- **Action plan** — 30/60/90 day mitigation roadmap with owners and budgets

## Industry Benchmarks

- Average company has 60% single-source exposure
- Supply chain disruptions cost Fortune 500s $184M per event (2024)
- Companies with formal risk programs recover 2.5x faster
- Dual-sourcing reduces disruption impact by 40-60%

---

Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — AI context packs for business automation.
