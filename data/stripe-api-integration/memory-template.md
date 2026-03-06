# Memory Template — Stripe API

Create `~/stripe-api-integration/memory.md` with this structure:

```markdown
# Stripe Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | done | declined

## Context
<!-- What you know about their Stripe setup -->
<!-- Payment type: subscriptions, one-time, both -->
<!-- Customer type: B2B, B2C, marketplace -->
<!-- Tech stack if mentioned -->

## Products
<!-- Products and prices they've created or discussed -->
<!-- Format: prod_XXX: Product Name (price_XXX: $X/mo) -->

## Preferences
<!-- Test mode vs live mode -->
<!-- Webhook patterns they use -->
<!-- Any custom flows established -->

## Notes
<!-- Internal observations -->
<!-- Common operations they request -->
<!-- Patterns to remember -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning | Ask questions when relevant |
| `complete` | Has enough context | Work normally |
| `paused` | User said "not now" | Don't ask, work with what you have |
| `never_ask` | User said stop | Never ask for more context |

## Key Principles

- **No config keys visible** — use natural language, not "subscription_mode: true"
- **Learn from behavior** — if they always create customers first, remember that
- **Track products loosely** — note what they create but don't maintain full inventory
- Update `last` on each use
