# Polymarket Workflow Patterns

## Data Gotchas

- Numeric columns are stored as text in SQLite snapshots; cast with `CAST(... AS REAL)`.
- `event_slug` and `event_title` may be null; do not rely on them for grouping.
- Exclude resolved markets with `CAST(hours_until_end AS REAL) > 0`.

## Slug-Based Dedup

```typescript
function eventKey(slug) {
  return slug
    .replace(/-\d{3,}(-\d{3,})+$/, "")
    .replace(/-\d+-\d+$/, "")
    .replace(/-\d+plus$/, "")
    .replace(/-game\d+$/, "")
    .replace(/-\d{4}-\d{2}-\d{2}$/, "")
}
```

## Dual-Layer Dedup (Slug + Question)

```typescript
function normQ(q) {
  return q.toLowerCase()
    .replace(/game\s*\d+/gi, "")
    .replace(/\b(map|round|set)\s*\d+/gi, "")
    .replace(/\d{1,2}\/\d{1,2}\/\d{2,4}/g, "")
    .replace(/\s+/g, " ")
    .trim()
}
```

## Thin-Book Detection

```sql
ROUND(CAST(volume_24h_usd AS REAL) / MAX(CAST(liquidity_usd AS REAL), 1), 1) AS vol_liq_ratio,
CASE
  WHEN CAST(volume_24h_usd AS REAL) / MAX(CAST(liquidity_usd AS REAL), 1) > 20 THEN 'THIN'
  ELSE 'ok'
END AS book_depth
```

Use a `> 20x` volume-to-liquidity ratio as a conservative slippage warning.

## KV Snapshot Diff Pattern

- Store periodic slug snapshots under time-bucketed keys.
- Keep `scanner:latest` for quick state access.
- Use `kv.list("scanner:")` and parse `.value` strings to diff new/dropped slugs.
