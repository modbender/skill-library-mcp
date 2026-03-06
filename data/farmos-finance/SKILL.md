---
name: farmos-finance
description: Query farm financial data — cash flow projections, cost tracking, breakeven analysis. Requires admin authentication. Highly sensitive data.
tags: [farming, finance, cash-flow, costs]
---

# FarmOS Finance

Forward-looking cash flow planning and cost management. Projects future cash flows based on planned costs and expected revenue.

## Data Completeness

1. **Always state totals** when reporting financial data: "Total operating costs: $892,000 across 12 categories."
2. **Cash flow projections combine multiple sources.** If the marketing revenue side fails, say so — don't present costs without revenue as a complete picture.
3. **If an endpoint returns an error**, report the failure to the user rather than presenting partial financial data. Partial financial data is worse than no data.
4. **For cost item listings**, use `/api/cost-items` with crop_year — this returns all items without pagination.

## When This Skill Triggers

- "What's our cash flow look like?"
- "Cost per acre this year?"
- "Breakeven price for corn?"
- "Monthly expense projection"
- "Show cost categories"
- "What are our biggest expenses?"

## Authentication

**ADMIN ONLY.** This skill accesses sensitive financial data. Always use admin-level auth.

```bash
TOKEN=$(~/clawd/scripts/farmos-auth.sh admin)
```

**Role mapping:** Check `~/.clawdbot/farmos-users.json`. If the sender is not admin, respond: "Financial data is restricted to farm owners. I can't access that for your account."

## API Base

http://100.102.77.110:8010

## Integration Endpoints (No Auth — if AI access toggle is enabled)

### Cost Summary
GET /api/integration/summary?crop_year=2025

Returns: Total costs by category for the crop year.

### Cash Flow (Simplified)
GET /api/integration/cash-flow-simple?crop_year=2025

Returns: Monthly outflow projections.

### Breakeven Analysis
GET /api/integration/breakeven?crop_year=2025

Returns: Cost per acre and cost per bushel by crop and entity. This tells you the minimum price needed to cover costs.

## Authenticated Endpoints (JWT Required)

### Cost Categories
GET /api/categories
Authorization: Bearer {token}

Returns: Cost category definitions (fertilizer, seed, chemicals, fuel, insurance, etc.)

### Cost Items
GET /api/cost-items?crop_year=2025
Authorization: Bearer {token}

Returns: Individual cost line items with amounts, timing, entity allocation.

### Cash Flow Projection (Full)
GET /api/cash-flow/projection?crop_year=2025
Authorization: Bearer {token}

Returns: Complete monthly cash flow with costs AND revenue (from Marketing module). Shows when money goes out and comes in.

### Cash Flow Summary
GET /api/cash-flow/summary?crop_year=2025
Authorization: Bearer {token}

Returns: Summarized by category and month.

## Key Concepts

- **Cost categories:** Per-unit (fertilizer, seed — calculated from rate x acres) vs annual totals (insurance, labor).
- **Timing:** Costs are assigned to specific months. Multiple months = split evenly.
- **Entity allocation:** Costs can be assigned to one entity, split across all by crop acres, or manually allocated.
- **Breakeven:** Total costs / expected bushels = minimum price per bushel to cover costs.

## Usage Notes

- Always specify crop_year parameter.
- Breakeven is the most-asked question — answer it quickly and clearly.
- Cash flow projection combines costs (this module) with revenue (marketing module).
- NEVER share financial data with non-admin users. This includes cost per acre, breakeven, cash flow, or any cost details.
