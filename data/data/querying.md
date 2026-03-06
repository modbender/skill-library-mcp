# Querying & Extraction

## SQL Generation

When user describes data needs in natural language:
1. Identify tables/sources involved
2. Determine join conditions
3. Build query incrementally — SELECT, FROM, WHERE, GROUP BY
4. Explain query logic before execution if complex

### Common Traps
- **Cartesian joins** — always verify join conditions exist between all tables
- **NULL in WHERE** — `= NULL` never matches, use `IS NULL`
- **Aggregates without GROUP BY** — every non-aggregated column needs GROUP BY
- **DISTINCT overuse** — usually masks a join problem
- **String comparisons** — case sensitivity varies by database

### Query Optimization
- Check if indexes exist on WHERE/JOIN columns
- Avoid `SELECT *` — specify needed columns
- Push filters early — WHERE before JOIN when possible
- Use EXPLAIN/EXPLAIN ANALYZE to verify plan

## Multi-Source Extraction

### APIs
- Handle pagination automatically (offset, cursor, page tokens)
- Respect rate limits — implement backoff
- Cache responses when appropriate
- Validate response schema before processing

### Files
- Detect encoding (UTF-8, Latin-1, etc.)
- Handle various delimiters (comma, tab, pipe, semicolon)
- Parse dates explicitly — don't rely on auto-detection
- Handle quoted fields and escaped characters

### Databases
- Use connection pooling for multiple queries
- Close connections after use
- Use parameterized queries — never string interpolation
- Handle timeouts gracefully

## Schema Discovery

When exploring new data source:
```
1. List available tables/collections
2. For each table: columns, types, sample values
3. Identify primary keys and relationships
4. Note row counts and data freshness
5. Document in a data dictionary
```

## Data Type Inference

| Observed Pattern | Likely Type | Verify With |
|------------------|-------------|-------------|
| 2024-01-15 | DATE | Check for time component |
| 2024-01-15T10:30:00Z | TIMESTAMP | Check timezone handling |
| 123.45 | DECIMAL/FLOAT | Check precision needs |
| true/false, 1/0 | BOOLEAN | Check for nulls |
| UUID pattern | UUID/STRING | Check if indexed |
| JSON object | JSONB/TEXT | Check if queried |
