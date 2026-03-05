---
name: travel-procurement
description: Source, compare, and recommend travel transport options (bus/train/shuttle/taxi/private transfer) from user-provided trip constraints. Use for route planning, quote comparison, and decision-ready recommendations.
---

# Travel Procurement

## Workflow
1. Collect constraints: date/time window, route, pax, luggage, budget, comfort constraints.
2. Source options in order: public transport first, then shared shuttle, then private transfer/taxi.
3. Normalize each option in a common format (price, duration, cancellation, fit/risk).
4. Recommend: best value, best convenience, best fallback.
5. Ask for explicit decision (A/B/C) and prepare next-step execution.

## Output Standard
- Keep concise and decision-ready.
- Every option must include total price and practical caveat.
- Always include one fallback.

## References
- Read `references/option-format.md` for option and recommendation templates.
