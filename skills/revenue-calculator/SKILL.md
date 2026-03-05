---
name: revenue-calculator
description: Projects revenue for OpenClaw sub-agent strategies (marketplace, subs, pay-per-task). Use for monetization estimates: input users/pricing/conversions → detailed annual/monthly projections, sensitivity analysis, break-even. Triggers: 'calculate revenue', 'project earnings', 'monetize skill/agent'.
---

# Revenue Calculator

## Workflow
1. **Gather Inputs**: Users/mo, price ($/user/task), conv rate (%), churn (%), costs (% compute).
2. **Select Strategy**: 1=API Sales, 2=Marketplace, 3=White-label, 4=Affiliates.
3. **Calculate**: Monthly/annual rev, net profit. Use scripts/revenue-calc.py for models.
4. **Output**: Table + sensitivity (e.g., +/-20% users) + next steps.
5. **Sensitivity**: Test scenarios (low/med/high).

## Quick Example
Input: Strategy 2, 100 users, $10/mo, 80% conv, 10% churn, 20% costs.
Output: Monthly $800, Annual $8,640 net.

## Strategies Pricing Defaults (ref/pricing-models.md)
- Sub: $9-99/mo
- Per-task: $0.01-1
- Usage: $0.001/token
- Affiliate: 5-20%

## Resources
### scripts/revenue-calc.py
Exec for precise calcs (input JSON → output JSON/table).

### references/pricing-models.md
Full tables/examples.

### assets/report-template.md
Copy for formatted outputs.
