---
name: olo-dcf-valuation
version: 1.0.0
description: DCF valuation methodology for M&A due diligence — projections, sensitivity analysis, and terminal value calculation
author: ololand.ai
author_url: https://ololand.ai
license: MIT
triggers:
  - dcf
  - discounted cash flow
  - wacc
  - terminal value
  - enterprise value
  - intrinsic valuation
  - equity value
  - free cash flow
tags:
  - finance
  - valuation
  - m-and-a
  - due-diligence
---

# DCF Valuation for M&A Due Diligence

Build discounted cash flow models for target company valuation in M&A contexts.

## Unit System (Critical)

- **Storage**: Absolute dollars (raw financial data)
- **Calculation**: Millions (DCF models expect this)
- **Display**: Smart formatting (B/M/K based on magnitude)
- Never pass raw stored values directly into DCF calculations without unit conversion

## Validation Before Calculation

1. Verify base revenue exists and is non-zero
2. Confirm WACC is between 5-25% (flag outliers with explanation)
3. Terminal growth must be less than WACC (Gordon Growth Model constraint)
4. Projection period: 5-10 years (default 5)
5. Verify EBITDA margins are within plausible industry range

## Default Assumptions

| Parameter | Default | Rationale |
|-----------|---------|-----------|
| Tax rate | 21% (US) / 17% (SG) | Adjust per jurisdiction |
| CapEx as % of revenue | 5% | Adjust per industry (SaaS ~3%, manufacturing ~8-12%) |
| Terminal growth | 2.5% | Should not exceed long-term GDP growth |
| WACC | CAPM-calculated | Fallback: 10-12% for mid-market |
| Depreciation | % of CapEx | Match to industry capital intensity |
| Working capital change | % of revenue delta | Use historical average if available |

## WACC Calculation (CAPM)

```
Cost of Equity = Risk-Free Rate + Beta × Equity Risk Premium
WACC = (E/V × Cost of Equity) + (D/V × Cost of Debt × (1 - Tax Rate))
```

- Risk-free rate: 10-year Treasury yield
- Equity risk premium: 5-7% (Damodaran)
- Beta: Use comparable public companies, unlever/relever for target capital structure
- Size premium: Add 2-4% for small/mid-market targets

## Projection Methodology

1. **Revenue**: Start from last reported, apply growth rates (declining toward terminal)
2. **EBITDA**: Apply margin assumptions (converge toward industry median)
3. **Free Cash Flow**: EBITDA - Taxes - CapEx - Change in Working Capital
4. **Terminal Value**: Gordon Growth Model or Exit Multiple method
5. **Discount**: Apply WACC to each year's FCF + terminal value

## Terminal Value

Prefer **Exit Multiple method** for M&A (matches how buyers think):
- Apply EV/EBITDA multiple to terminal year EBITDA
- Cross-check with Gordon Growth implied multiple
- Flag if implied perpetuity growth exceeds 3%

## Required Output

Always present:
- **Enterprise Value** range (low / base / high)
- **Equity Value** (EV - net debt)
- **Implied EV/EBITDA multiple** (sanity check against comparables)
- **Sensitivity table**: WACC (rows) vs Terminal Growth or Exit Multiple (columns)
- **Football field chart** if multiple valuation methods available

## M&A-Specific Considerations

- Apply a **control premium** (20-40%) if valuing for acquisition vs. minority stake
- Consider **synergy value** separately from standalone DCF
- Discount rate should reflect **buyer's cost of capital**, not target's
- Model **integration costs** as a deduction from synergy value
- Present **with-synergies** and **without-synergies** valuations separately
