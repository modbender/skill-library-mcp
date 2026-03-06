---
name: Housing
slug: housing
version: 1.0.0
description: Buy, rent, or invest in property with market analysis, legal compliance, and cost estimation.
metadata: {"clawdbot":{"emoji":"🏠","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs help with real estate decisions: buying first home, renting apartments, investing in property, or managing rentals as landlord. Agent handles research, analysis, comparisons, and compliance checks.

## Quick Reference

| Topic | File |
|-------|------|
| Buying checklist | `buying.md` |
| Renting guidance | `renting.md` |
| Investment analysis | `investing.md` |
| Landlord operations | `landlord.md` |

## Core Rules

### 1. Verify Local Context First
- Real estate is hyperlocal — prices, laws, taxes vary by city/country
- Ask user's location before ANY market advice
- Never assume US-centric terms (HOA, closing costs) apply elsewhere
- Research local regulations: tenant rights, rent control, transfer taxes

### 2. Calculate Total Cost of Ownership
| Category | Include |
|----------|---------|
| Purchase | Down payment, closing costs, transfer tax, notary fees |
| Monthly | Mortgage, insurance, property tax, HOA/community fees, utilities |
| Hidden | Maintenance (1-2%/year), vacancy (rentals), capex reserves |

Never quote just the listing price — always estimate true monthly/annual cost.

### 3. Separate Roles Have Different Priorities
| Role | Primary concerns |
|------|-----------------|
| First-time buyer | Affordability, mortgage approval, inspection red flags |
| Investor | Cash flow, cap rate, appreciation potential, tenant demand |
| Renter | Lease terms, rights, hidden fees, neighborhood safety |
| Landlord | Tenant screening, rent pricing, legal compliance, tax deductions |

Confirm user's role before advising.

### 4. Use Current Data Cautiously
- Real estate markets shift monthly — acknowledge data staleness
- Provide frameworks for analysis, not specific price predictions
- Recommend local sources: MLS, government registries, local agents
- Flag when information might be outdated

### 5. Financial Analysis Standards
For investment properties:
- **Cap Rate** = Net Operating Income / Purchase Price
- **Cash-on-Cash** = Annual Cash Flow / Total Cash Invested
- **1% Rule** (quick filter): Monthly rent ≥ 1% of purchase price
- Always stress-test: what if vacancy doubles? rates rise 2%?

### 6. Document Everything
Transactions require extensive paperwork:
- Pre-approval letters, earnest money, inspection reports
- Title search, insurance, closing disclosure
- Lease agreements, move-in inspection, security deposit receipts

Create checklists for user's specific transaction type.

### 7. Red Flags to Surface
| Signal | Risk |
|--------|------|
| Price significantly below market | Hidden damage, legal issues, scams |
| Seller rushing closing | Undisclosed problems |
| No inspection allowed | Major structural issues |
| Landlord avoiding lease | No legal protection |
| HOA financials unavailable | Special assessments coming |

Always recommend professional inspection and legal review.

## Housing Traps

- **Comparing unlike markets** — Tokyo rent dynamics ≠ Austin ≠ Berlin; never apply one market's rules to another
- **Ignoring opportunity cost** — down payment could be invested; compare scenarios
- **Emotional anchoring** — "dream home" bias leads to overpaying; use comparable sales data
- **Underestimating transaction costs** — buying/selling costs 5-10% in most markets
- **Assuming appreciation** — property values can stagnate or drop; don't count on gains
- **Skipping tenant screening** — one bad tenant costs more than months of vacancy
- **Missing lease clauses** — break fees, renewal terms, maintenance responsibility often overlooked
