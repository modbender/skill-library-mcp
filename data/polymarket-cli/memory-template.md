# Memory Template — Polymarket CLI

Create `~/polymarket-cli/memory.md` with this structure:

```markdown
# Polymarket CLI Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Context
<!-- What you know about their Polymarket usage -->
<!-- Add observations from conversations -->

## Tracked Markets
<!-- Markets they're interested in following -->
<!-- Format: slug | last_price | notes -->

## Notes
<!-- Internal observations -->
<!-- Trading patterns, risk tolerance, favorite categories -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning preferences | Ask when relevant |
| `complete` | Know their workflow | Work normally |
| `paused` | User said "not now" | Don't push features |
| `never_ask` | User wants minimal interaction | Query-response only |

## Integration Values

| Value | Meaning |
|-------|---------|
| `pending` | Haven't asked user preference yet |
| `automatic` | User approved activation when relevant |
| `on-demand` | Only when explicitly asked |
| `tracking` | Monitor specific markets user requested |

## Key Principles

- **No config visible to user** — use natural language, not "integration: proactive"
- **Learn from behavior** — if they always ask about politics, note that
- **Most users stay read-only** — don't assume they want to trade
- Update `last` on each meaningful interaction
