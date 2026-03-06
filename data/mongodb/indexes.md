# Index Strategies

## Index Design Philosophy

- Design indexes for your queries, not your schema
- Every query pattern needs an index—no index = collection scan
- Start with slowest queries and work backwards
- Measure with explain(), don't guess

## Compound Index Order (ESR Rule)

- **E**quality fields first—exact match conditions
- **S**ort fields next—for ORDER BY without extra sort step
- **R**ange fields last—$gt, $lt, $in (multiple values)
- Order matters: `{status: 1, createdAt: -1}` different from `{createdAt: -1, status: 1}`

## Covered Queries

- Query uses only indexed fields = no document fetch—maximum speed
- Include fields from query AND projection in index
- Check explain for `IXSCAN` + `totalDocsExamined: 0`
- Worth it for frequent, simple queries

## Multikey Index Behavior

- Array field = multikey index—one entry per array element
- Index size explodes with large arrays—1000 element array = 1000 index entries
- Only ONE array field per compound index allowed
- Can still be useful—just understand the cost

## Partial Indexes

- Index only documents matching a filter: `{partialFilterExpression: {status: "active"}}`
- Smaller index = faster queries AND less storage
- Query MUST include filter condition to use partial index
- Great for "hot" subset of data—index only active users, recent orders

## TTL Indexes

- Auto-delete documents after time: `{expireAfterSeconds: 86400}`
- Only on date field—expires based on that date
- Background thread runs ~every 60 seconds—not instant deletion
- Doesn't work on capped collections

## Text Indexes

- Only ONE text index per collection—plan carefully
- Requires `$text` in query—regular find can't use it
- Stemming and stop words are language-specific
- For complex text search, use Atlas Search instead

## Index Intersection

- MongoDB CAN use multiple indexes on one query—but rarely efficient
- Don't rely on it—single compound index almost always better
- If explain shows `AND_SORTED` or `AND_HASH`, consider compound index
- Exception: covered queries with different projections

## Monitoring and Maintenance

- `db.collection.getIndexes()`—see all indexes
- `db.collection.aggregate([{$indexStats: {}}])`—usage statistics
- Drop unused indexes—they still cost writes and storage
- `background: true` when creating on production—but still impacts performance
