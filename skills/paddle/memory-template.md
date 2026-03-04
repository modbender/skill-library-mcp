# Memory Template — Paddle

Create `~/paddle/memory.md` with this structure:

```markdown
# Paddle Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | done | declined

## Environment
<!-- sandbox | production | both -->

## Product
<!-- Their product type, pricing model, trial setup -->

## Tech Stack
<!-- Languages, frameworks, hosting for integration recommendations -->

## Price IDs
<!-- Map of their prices for reference -->
<!-- Example: basic_monthly: pri_xxx, pro_annual: pri_yyy -->

## Notes
<!-- Specific requirements, edge cases, decisions made -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning their setup | Gather context opportunistically |
| `complete` | Has enough context | Work normally |
| `paused` | User said "not now" | Don't ask, work with what you have |
| `never_ask` | User said stop | Never ask for more context |

## Key Principles

- **No config keys visible** — use natural language descriptions
- **Learn from behavior** — observe their code, don't interrogate
- **Most integrations stay `ongoing`** — always learning new edge cases
- Update `last` on each use
