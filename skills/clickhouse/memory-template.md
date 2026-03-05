# Memory Template — ClickHouse

Create `~/clickhouse/memory.md` with this structure:

```markdown
# ClickHouse Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending | done | declined

## Connection Profile
<!-- NOTE: Never store passwords here. Use env vars or clickhouse-client profiles -->
host: localhost
port: 9000
database: default
auth_method: none | password | certificate
cluster: no | yes (cluster_name)

## Use Case
<!-- Primary analytics use case -->
<!-- e.g., "Real-time event analytics for SaaS product" -->

## Data Scale
<!-- Order of magnitude -->
<!-- e.g., "~500M events/day, 90-day retention" -->

## Key Tables
<!-- Tables and their purposes -->
<!-- e.g., "events: user actions, 50B rows" -->

## Query Patterns
<!-- Common query types -->
<!-- e.g., "Hourly aggregations by user_id, date range filters" -->

## Pain Points
<!-- Issues they've mentioned -->
<!-- e.g., "Slow queries on high-cardinality columns" -->

## Notes
<!-- Internal observations -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning their setup | Gather context |
| `complete` | Have full picture | Optimize queries |
| `paused` | User said "not now" | Work with what you have |

## Key Principles

- **Connection profile is critical** — without it, can't help effectively
- **Data scale matters** — 1M rows vs 1T rows need different strategies
- **Learn from their queries** — save patterns that work well
- Update `last` on each use
