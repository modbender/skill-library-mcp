---
name: Zillow
slug: zillow
version: 1.0.0
description: Navigate Zillow for buying, selling, investing, and market research with Zestimate interpretation, pricing strategy, and ROI analysis.
metadata: {"clawdbot":{"emoji":"🏠","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs help with US real estate via Zillow. Agent handles property search, Zestimate analysis, investment calculations, pricing strategy, and market trends.

## Quick Reference

| Topic | File |
|-------|------|
| Investor calculations | `investing.md` |
| Pricing strategy | `pricing.md` |

## Core Rules

### 1. Zestimate is an Estimate, Not a Price
- ALWAYS caveat Zestimates: "Zillow's estimate, typically 5-15% off in this market"
- Check Zestimate accuracy for the specific ZIP — varies wildly by location
- Never use Zestimate as sole pricing guidance
- For sellers: compare to actual SOLD prices, not Zestimates
- For investors: Zestimate rents are even less reliable than home values

### 2. Calculate True Monthly Costs
For buyers, always include ALL components:
| Component | Notes |
|-----------|-------|
| Principal + Interest | Based on current rates |
| Property taxes | Pull actual, not Zillow estimate |
| Homeowners insurance | Varies by region/flood zone |
| PMI | If down payment < 20% |
| HOA fees | Check for special assessments |
| Mello-Roos/special districts | California especially |

### 3. Market Context is Hyperlocal
- National trends are meaningless — real estate is ZIP-code specific
- "Days on Market" benchmarks differ: 10 DOM is slow in Phoenix, fast in NYC
- Always specify property type (SFH vs condo vs townhouse) — different markets
- Seasonal patterns vary by region: Phoenix summer ≠ Chicago summer

### 4. Investment Metrics Must Be Conservative
For rental property analysis, see `investing.md`. Key traps:
- Use 50% expense rule as MINIMUM, not ceiling
- Cap rate uses purchase price, not list price
- Factor vacancy (5-15% depending on market)
- Zestimate rent is often wrong — verify with actual rental comps

### 5. Zillow Data Lags
- Listings may be 1-2 days behind MLS
- Status (active/pending/sold) can be stale
- Zestimate updates monthly, not daily
- Always note data recency when citing stats

### 6. Role-Specific Guidance

| User Type | Key Concerns |
|-----------|--------------|
| First-time buyer | FHA programs, true monthly cost, avoid overbidding |
| Investor | Cap rate, cash-on-cash return, expense reality |
| Seller | Competitive pricing, overpricing trap, market timing |
| Agent | Premier Agent leads, CMA comps, listing optimization |

## Zillow Traps

### For All Users
- Zestimate ≠ market value (can be 20%+ off in unusual properties)
- Listing price ≠ sale price (especially in hot/cold markets)
- "Views" and "saves" include nosy neighbors, not just buyers
- Square footage and bed count often wrong — verify with county records

### For Buyers
- Contingent/pending listings may show as available
- Don't waive inspection to "be competitive" — especially first-timers
- Pre-approval ≠ pre-qualification (huge difference for offers)
- Earnest money timing catches people off guard

### For Investors
- High cap rate often means high risk (war zones, declining areas)
- Zestimate rent wildly inaccurate in many markets
- Property taxes can change dramatically after purchase
- Don't calculate returns on list price — use realistic acquisition cost

### For Sellers
- Overpricing → stale listing → sells for LESS than fair price
- Price reductions signal desperation to buyers
- "For Sale By Owner" on Zillow gets less visibility than MLS
- Zillow doesn't know your renovations or deferred maintenance

## Data Sources to Cross-Reference

- County assessor (actual tax records)
- FEMA flood maps
- Rentometer/Apartments.com (rental comps)
- Crime/school rating sites
- Local MLS for real-time accuracy
