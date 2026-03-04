# Financial Due Diligence Analyzer

Run comprehensive financial due diligence on acquisition targets, investment opportunities, or partnership prospects. Built for PE firms, corporate development teams, and founders evaluating deals.

## What This Does

Generates a complete due diligence package:
- **Quality of Earnings (QoE)** — normalize EBITDA, strip one-time items, identify recurring vs non-recurring revenue
- **Working Capital Analysis** — NWC trends, peg calculation, seasonal adjustments
- **Revenue Quality** — customer concentration, churn, cohort analysis, contract backlog
- **Debt & Liabilities** — hidden obligations, off-balance-sheet items, contingent liabilities
- **Cash Flow Bridge** — EBITDA to free cash flow conversion, capex requirements
- **Red Flag Scanner** — 23 common deal-killers ranked by severity

## How to Use

Tell your agent: "Run financial due diligence on [company/deal]"

Provide what you have:
- Financial statements (P&L, balance sheet, cash flow) — even partial
- Revenue breakdown by customer/product
- Known deal terms (purchase price, structure)

The agent will generate a structured diligence report with findings, risks, and negotiation points.

## QoE Framework

### EBITDA Normalization Checklist
| Adjustment Category | Common Items | Direction |
|---|---|---|
| Owner compensation | Above/below market salary, personal expenses | +/- |
| One-time revenue | PPP loans, insurance claims, litigation settlements | - |
| One-time expenses | Restructuring, M&A costs, natural disaster | + |
| Related party | Above/below market rent, intercompany charges | +/- |
| Accounting changes | Revenue recognition timing, reserve adjustments | +/- |
| Run-rate adjustments | New contracts, lost customers, price changes | +/- |

### Revenue Quality Score (0-100)
| Factor | Weight | Scoring |
|---|---|---|
| Recurring vs one-time | 25% | >80% recurring = 25, >60% = 18, >40% = 12, <40% = 5 |
| Customer concentration | 20% | Top customer <10% = 20, <20% = 15, <30% = 10, >30% = 3 |
| Retention rate | 20% | >95% = 20, >90% = 15, >85% = 10, <85% = 5 |
| Contract backlog | 15% | >12mo coverage = 15, >6mo = 10, >3mo = 6, <3mo = 2 |
| Growth trajectory | 10% | >30% YoY = 10, >15% = 7, >5% = 4, declining = 1 |
| Pricing power | 10% | Annual increases + low churn = 10, some = 6, none = 2 |

### Working Capital Peg
```
NWC Peg = Average of trailing 12 months normalized NWC

Normalized NWC = Current Assets (excl. cash) - Current Liabilities (excl. debt)

Adjustments:
- Remove seasonal spikes (use monthly data, not quarterly)
- Strip one-time receivables/payables
- Normalize inventory to steady-state
- Adjust for known post-close changes

If NWC at close > Peg → Seller receives difference
If NWC at close < Peg → Buyer receives difference
```

## Red Flag Scanner (23 Points)

### Critical (Deal-killers)
1. Revenue concentration >40% single customer
2. Declining revenue with no credible turnaround plan
3. Negative or deteriorating cash conversion (EBITDA to FCF <50%)
4. Undisclosed litigation or regulatory action
5. Key person dependency with no succession plan
6. Material related-party transactions at off-market terms
7. Unrecorded liabilities (tax, environmental, legal)

### Serious (Price adjustments)
8. Customer churn accelerating quarter-over-quarter
9. Gross margin compression >200bps annually
10. Capex requirements understated (deferred maintenance)
11. Working capital trends moving against buyer
12. Aggressive revenue recognition policies
13. Unusual pre-close transactions (dividends, bonuses)
14. Technology debt requiring material investment
15. Regulatory changes threatening core business model

### Notable (Negotiation points)
16. Management team retention risk
17. Vendor concentration >30% single supplier
18. IP ownership gaps or licensing dependencies
19. Insurance coverage gaps
20. Environmental liabilities (real estate)
21. Employee benefit obligations (pension, OPEB)
22. Tax position optimization opportunities
23. Integration complexity indicators

## Valuation Sanity Check

### Quick Multiples Reference (2025-2026)
| Sector | EV/Revenue | EV/EBITDA | Notes |
|---|---|---|---|
| SaaS (<$10M ARR) | 4-8x | 15-25x | Higher for >120% NRR |
| SaaS ($10-50M ARR) | 6-12x | 20-35x | Rule of 40 premium |
| Professional Services | 1-2x | 8-12x | People-dependent discount |
| Manufacturing | 0.5-1.5x | 6-10x | Asset-heavy adjustment |
| Healthcare Services | 1-3x | 10-15x | Regulatory moat premium |
| Fintech | 5-15x | 20-40x | Wide range, growth-dependent |
| E-commerce | 1-3x | 10-18x | Brand and margin quality |

### Purchase Price Allocation
```
Enterprise Value
- Net Debt (total debt - cash)
- Transaction Expenses
- Working Capital Adjustment (vs Peg)
+ Earnout (if applicable, risk-adjusted at 50-70% probability)
= Equity Value to Seller
```

## Output Format

Your due diligence report should include:
1. **Executive Summary** — deal overview, key findings, go/no-go recommendation
2. **Quality of Earnings** — normalized EBITDA bridge with adjustments
3. **Revenue Analysis** — quality score, concentration, trends
4. **Working Capital** — NWC peg, seasonal analysis, close estimate
5. **Cash Flow** — EBITDA to FCF bridge, capex analysis
6. **Red Flags** — scored findings with severity and $ impact
7. **Valuation Check** — multiples comparison, sanity test
8. **Negotiation Points** — specific items for purchase agreement

---

Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — AI context packs for business operations ($47 each).

**More tools:**
- [AI Revenue Leak Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/) — Find where you're losing money
- [Agent Setup Wizard](https://afrexai-cto.github.io/agent-setup/) — Deploy AI agents in minutes
- [Full Context Pack Store](https://afrexai-cto.github.io/context-packs/) — 10 industry packs, $47 each
