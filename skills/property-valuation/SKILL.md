---
name: Property Valuation
slug: property-valuation
version: 1.0.0
homepage: https://clawic.com/skills/property-valuation
description: Estimate property values using comps, income approach, and market analysis with adjustment calculations.
metadata: {"clawdbot":{"emoji":"🏠","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for onboarding guidance.

## When to Use

User needs property value estimates. Agent handles comparable analysis, income valuations, adjustment calculations, and market condition assessments.

## Architecture

Memory at `~/property-valuation/`. See `memory-template.md` for structure.

```
~/property-valuation/
├── memory.md          # Properties analyzed, market data
└── valuations/        # Saved valuation reports
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |

## Core Rules

### 1. Always State the Valuation Method
Every estimate must specify which approach:
- **Comparable Sales (Comps):** Based on recent similar sales
- **Income Approach:** Based on rental income (Cap Rate)
- **Cost Approach:** Land value + construction cost - depreciation

Most residential uses comps. Investment properties need income approach.

### 2. Require Key Property Data
Before estimating, gather:
- Location (address or neighborhood)
- Property type (SFH, condo, multi-family)
- Size (sqft or sqm)
- Bedrooms/bathrooms
- Condition (excellent/good/fair/poor)
- Year built
- Lot size (if applicable)

Missing data = wider value range.

### 3. Apply Adjustments Explicitly
When using comps, show adjustments:

| Factor | Adjustment |
|--------|------------|
| Extra bedroom | +3-5% |
| Extra bathroom | +2-3% |
| Newer by 10 years | +5-10% |
| Superior condition | +5-15% |
| Larger lot | +1-3% per 1000 sqft |
| Better location | +5-20% |
| Pool | +2-5% (climate dependent) |

Document each adjustment applied.

### 4. State Confidence Level
Every valuation includes confidence:
- **High:** 3+ recent comps within 0.5 miles, similar specs
- **Medium:** 2-3 comps, some adjustments needed
- **Low:** Limited data, significant adjustments, unusual property

### 5. Include Market Context
Current market conditions affect value:
- **Seller's market:** Values at high end of range
- **Buyer's market:** Values at low end
- **Balanced:** Use midpoint

Note days on market and inventory levels if known.

### 6. Cap Rate for Investment Properties
Income approach formula:
```
Property Value = Net Operating Income / Cap Rate
NOI = Gross Rent - Operating Expenses (typically 35-45% of rent)
```

Cap rates by property type (2024 averages):
- Multifamily: 5-7%
- Retail: 6-8%
- Office: 7-9%
- Industrial: 5-7%

Lower cap rate = higher value = lower risk.

### 7. Price Per Square Foot as Sanity Check
Always calculate and compare:
```
Price/SqFt = Property Value / Living Area
```
If result differs significantly from neighborhood average, explain why.

## Common Traps

- **Using old comps:** Sales older than 6 months may not reflect current market. Prefer recent sales.
- **Ignoring condition:** Two identical homes can differ 20%+ based on updates and maintenance.
- **Zillow/AVM over-reliance:** Automated valuations miss condition, upgrades, and local factors. Use as starting point only.
- **Not adjusting for differences:** Raw comps without adjustments mislead. Always adjust.
- **Confusing assessed value:** Tax assessments often lag market value by 10-30%.
- **Ignoring days on market:** Homes that sat long may have sold below market.

## Security & Privacy

**Data that stays local:**
- Property details and valuations in ~/property-valuation/
- No data sent externally

**This skill does NOT:**
- Access real-time MLS data (user must provide comps)
- Connect to Zillow/Redfin APIs
- Store sensitive financial information

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `real-estate-skill` — Real estate transactions
- `financial-literacy` — Financial concepts
- `house` — Home management

## Feedback

- If useful: `clawhub star property-valuation`
- Stay updated: `clawhub sync`
