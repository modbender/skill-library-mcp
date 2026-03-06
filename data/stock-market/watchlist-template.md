# Watchlist Template — Stock Market

Use this structure for `~/stock-market/watchlist.md`.

```markdown
# Watchlist

## Date
YYYY-MM-DD

## Priority A (Actionable Soon)
| Ticker | Setup | Catalyst Window | Trigger | Invalidation | Notes |
|--------|-------|-----------------|---------|--------------|-------|
|        |       |                 |         |              |       |

## Priority B (Needs Confirmation)
| Ticker | Missing Evidence | Next Check | Risk Note |
|--------|------------------|------------|-----------|
|        |                  |            |           |

## Priority C (Theme Tracking)
| Ticker/Sector | Theme | Why Track | Revisit Date |
|---------------|-------|-----------|--------------|
|               |       |           |              |

## Deprioritized
| Ticker | Reason Removed | Date |
|--------|----------------|------|
|        |                |      |
```

## Ranking Rules

1. Rank by setup quality and catalyst clarity, not only recent price momentum.
2. Keep Priority A short (maximum 3-5 names) to maintain execution focus.
3. Move symbols between tiers whenever evidence changes.
4. Remove stale names after catalyst passes with no valid trigger.

## Quick Health Checks

- Does each Priority A ticker have both trigger and invalidation?
- Are you duplicating correlated names with the same risk driver?
- Is a no-trade list maintained to prevent revenge entries?
