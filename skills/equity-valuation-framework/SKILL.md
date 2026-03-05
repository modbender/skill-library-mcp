---
name: equity-valuation-framework
description: Provides a decision-grade equity valuation playbook and report standard (multiples, DCF, quality assessment, scenarios, margin of safety); used when users request valuation, best-stock comparison, investment thesis explanation, or structured risk review.
compatibility: Requires structured market and financial inputs (typically from vnstock workflows); no direct data fetching in this skill.
metadata: {"openclaw":{"emoji":"🧮"}}
---

# Equity Valuation Framework

Use this skill as the "rules of the game" for valuation decisions and report standardization.

## Scope and role
- Purpose: transform already-fetched data into a professional valuation view.
- This skill does **not** fetch data.
- Upstream data should come from:
  - `vnstock-free-expert` for company/price/ratio inputs
  - `nso-macro-monitor`, `us-macro-news-monitor`, `vn-market-news-monitor` for macro/news context

## When to trigger
- User asks: "value this stock", "is it cheap/expensive", "best stock between A/B/C", "give me bull/base/bear", "build an investment memo".
- User requests a decision-ready report, not only raw metrics.

## Required input contract
Accept an input bundle with these sections (missing fields allowed, but must be flagged):

```json
{
  "ticker": "HPG",
  "as_of_date": "YYYY-MM-DD",
  "currency": "VND",
  "financials": {
    "income_statement": {},
    "balance_sheet": {},
    "cash_flow": {},
    "ratios": {}
  },
  "price_history": {
    "daily": [],
    "returns": {
      "1m": null,
      "3m": null,
      "6m": null,
      "12m": null
    }
  },
  "peer_set": ["AAA", "BBB"],
  "macro_snapshot": {},
  "news_digest": {},
  "metadata": {
    "source": "kbs|vci",
    "data_quality_notes": []
  }
}
```

## Execution workflow (ordered)
1. Validate input bundle completeness and freshness.
2. Run the data quality gate and assign initial confidence.
3. Select valuation modules based on available data (`Multiples`, `DCF`, sector adaptation).
4. Build bull/base/bear scenarios with explicit assumptions.
5. Triangulate fair value, define safety zone, and list key risks.
6. Apply confidence rubric and disclose gaps that can change conclusions.
7. Return the report using the required section order.

## Data quality gate (must run first)
1. Check freshness: state report periods and price cutoff date.
2. Check completeness: identify missing key lines (revenue, EBIT, net income, CFO, debt, equity, shares).
3. Check consistency: basic identity checks (assets = liabilities + equity if available).
4. Mark confidence tier:
- `High`: complete + recent + internally consistent.
- `Medium`: minor gaps, valuation still usable.
- `Low`: major gaps; only directional view allowed.

## Shared confidence rubric (required)
Use this standardized interpretation:
- `High`: valuation triangulation is valid (>= 2 robust methods), assumptions are explicit, and key inputs are complete.
- `Medium`: only one robust method is usable or moderate gaps require wider valuation ranges.
- `Low`: major input gaps/quality issues force directional valuation only (no precise fair-value claim).

Always report:
1. Confidence level.
2. Which modules were actually run (`Multiples`, `DCF`, sector adaptations).
3. Critical missing inputs that would most likely change fair value.

## Valuation modules
Run modules based on available data. Prefer triangulation (2+ methods).

### 1) Relative valuation (Multiples)
Use when at least one of earnings/book/EBITDA is reliable.

- Core multiples:
  - `P/E` (earnings-based)
  - `P/B` (capital-intensive, banks/financials)
  - `EV/EBITDA` (operating comparison)
  - Optional: `EV/Sales`, `P/CF`
- Compare across:
  - peer median / percentile
  - company 3-5y own history
- Normalize for one-off items when possible.
- Output:
  - implied value range per multiple
  - weighted relative-value estimate

### 2) DCF valuation
Use only when cash-flow visibility is acceptable.

- Model setup:
  - Forecast horizon: 5-10 years (default 5 if uncertain)
  - Revenue growth path by scenario
  - Margin path (EBIT/FCF margin)
  - Reinvestment assumptions
  - WACC with explicit inputs (risk-free, ERP, beta, debt cost)
  - Terminal value: Gordon or exit multiple (state choice)
- Mandatory sensitivity grid:
  - WACC ±100 bps
  - terminal growth ±50 bps
- Output:
  - base/bull/bear fair value
  - sensitivity table

### 3) Sector-specific adaptation
#### Banks / Insurance / Financials
- Prioritize: `P/B`, `ROE`, asset quality proxies, capital adequacy proxies, funding cost/NIM proxies.
- De-emphasize EV/EBITDA.
- Evaluate sustainability of ROE and provisioning pressure.

#### Cyclicals (steel, chemicals, commodities, shipping)
- Use cycle-aware assumptions:
  - normalized margin, not peak margin
  - conservative terminal assumptions
- Add cycle-risk note as first-class risk item.

## Quality and business resilience checklist
Assess each item as `Strong / Neutral / Weak` with one-line evidence:
- Moat and pricing power
- Governance and capital allocation
- Earnings quality (cash conversion, accrual risk)
- Balance-sheet risk (leverage, maturity risk)
- Cyclicality and external dependency
- Execution track record

## Scenario framework (required)
Always provide three scenarios:
1. `Bull`: better macro + execution upside
2. `Base`: most likely path under current conditions
3. `Bear`: macro/industry shock + execution shortfall

For each scenario include:
- Key assumptions
- Expected fundamental trajectory
- Implied fair value range
- Probability weight (optional but preferred)

## Margin of safety rule
- Define `Fair Value` range from module triangulation.
- Define `Safety Zone` below fair value (default 15-30% depending on confidence and cyclicality).
- Avoid absolute buy/sell commands.
- Use language: "appears undervalued / fairly valued / stretched" and "requires margin-of-safety discipline".

## Decision policy (how to conclude)
Create an integrated view from:
- valuation outputs (multiples + DCF if valid)
- business quality checklist
- macro/news constraints

If the user is managing a watchlist/portfolio, end with **conditional action framing** suitable for `portfolio-risk-manager`:
- `Trigger to add risk` (what would increase conviction)
- `Trigger to reduce risk`
- `Invalidation` (what would make the thesis wrong)
- `Horizon` (ngắn/trung/dài)

Conclusion label:
- `Attractive` (valuation discount + acceptable quality/risk)
- `Watchlist` (mixed signals, wait for trigger)
- `Caution` (valuation unsupported or risk too high)

## Required report output template
Return exactly these sections in this order:

1. `Executive Summary`
- One paragraph: current valuation stance and why.

2. `What Data Was Used`
- Source, as-of date, statement periods, peer set.

3. `Core Thesis (Bull / Base / Bear)`
- Key drivers by scenario.

4. `Valuation Work`
- Multiples table (current vs peer vs implied)
- DCF summary (if run)
- Sensitivity table

5. `Business Quality Assessment`
- Checklist table with evidence lines.

6. `Risk Register`
- Ranked risks with impact, probability, and monitoring trigger.

7. `Fair Value and Safety Zone`
- Fair value range and margin-of-safety zone with rationale.

8. `Confidence and Gaps`
- Confidence level and exact missing data that could change the view.

9. `Disclaimer`
- Educational analysis only, not personalized investment advice.

## Formatting standards
- Use simple language and explain terms briefly.
- State all critical assumptions explicitly.
- Distinguish facts vs assumptions vs inference.
- Do not hide data gaps; surface them early.
- Keep numbers auditable and unit-consistent (VND bn/trn, %, x).

## Minimal scoring rubric (optional but recommended)
If user asks for ranking within this framework:
- `Valuation` 40%
- `Quality` 35%
- `Momentum/Revision` 15%
- `Risk penalty` 10%

Calibrate per sector and confidence.

## Fail-safe behavior
If data quality is low:
- downgrade confidence
- skip fragile modules (e.g., DCF)
- deliver directional valuation only
- list exact data needed for full valuation

## Trigger examples
- "Value HPG with bull/base/bear and margin of safety."
- "Compare VCB vs BID valuation and explain the thesis."
- "Prepare a structured valuation memo with sensitivity table and risk register."
