# Memory Template — Property Valuation

Create `~/property-valuation/memory.md` with this structure:

```markdown
# Property Valuation Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | done | declined

## Context
<!-- Market focus, property types, valuation purpose -->
<!-- Add as you learn from conversations -->

## Market Data
<!-- Local price/sqft averages, cap rates, market conditions -->
<!-- Update when user provides market intel -->

## Properties Analyzed
<!-- Brief log of valuations done -->
<!-- Format: Date | Address/Description | Value Range | Method -->

## Notes
<!-- Preferences: quick estimates vs detailed analysis -->
<!-- Data sources they have access to (MLS, etc.) -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning | Gather context opportunistically |
| `complete` | Has enough context | Work normally |
| `paused` | User said "not now" | Don't ask, work with what you have |

## Key Principles

- **No config keys visible** — use natural language
- **Learn from behavior** — observe their analysis style
- **Update market data** — when user shares local insights
- Update `last` on each use
