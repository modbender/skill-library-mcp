# Elasticsearch Logs Examples

Search and analyze application logs using Elasticsearch Query DSL and ES|QL.

## Available Tools

### 1. list-log-indices-from-elasticsearch

List all available log indices.

**Parameters:**

- `format` (optional, string): Output format - `table` or `json` (default: table)
- `health` (optional, string): Filter by health - `green`, `yellow`, or `red`
- `status` (optional, string): Filter by status - `open` or `close`

### 2. search-logs-from-elasticsearch

Full-text search using Elasticsearch Query DSL.

**Parameters:**

- `index` (required, string): Index pattern (e.g., `logs-*`, `filebeat-*`)
- `body` (required, string): Complete ES Query DSL as JSON string

### 3. query-logs-from-elasticsearch

Query logs using ES|QL (Elasticsearch Query Language).

**Parameters:**

- `query` (required, string): ES|QL query string
- `format` (optional, string): Response format - `json`, `csv`, `tsv`, `txt` (default: json)
- `columnar` (optional, string): Columnar format - `true` or `false` (default: false)

## Example 1: List Log Indices

```bash
# List all indices
npx mcporter call ops-mcp-server list-log-indices-from-elasticsearch

# Filter by health status
npx mcporter call ops-mcp-server list-log-indices-from-elasticsearch health="green" format="table"

# Get open indices in JSON
npx mcporter call ops-mcp-server list-log-indices-from-elasticsearch status="open" format="json"
```

## Example 2: Simple Text Search (Query DSL)

```bash
# Simple search
npx mcporter call ops-mcp-server search-logs-from-elasticsearch \
  index="logs-*" body='{"query":{"match":{"message":"error"}}}'

# Search with time filter
npx mcporter call ops-mcp-server search-logs-from-elasticsearch \
  index="logs-app-*" body='{"query":{"bool":{"must":[{"match":{"message":"timeout"}}],"filter":[{"range":{"@timestamp":{"gte":"now-1h"}}}]}}}'
```

## Example 3: ES|QL Queries (Recommended)

ES|QL is the new query language (ES 8.11+) - simpler and more powerful.

```bash
# Basic ES|QL query
npx mcporter call ops-mcp-server query-logs-from-elasticsearch \
  query="FROM logs-* | WHERE @timestamp > NOW() - 1 hour | LIMIT 10"

# Aggregation query
npx mcporter call ops-mcp-server query-logs-from-elasticsearch \
  query="FROM logs-* | WHERE level == 'error' | STATS count() BY message | SORT count DESC | LIMIT 10"

# With format option
npx mcporter call ops-mcp-server query-logs-from-elasticsearch \
  query="FROM logs-* | WHERE service == 'api-gateway' AND level IN ('error', 'fatal')" format="json"
```

## ES|QL Syntax Reference

### Basic Structure

```sql
FROM <index_pattern>
| WHERE <condition>
| STATS <aggregation>
| SORT <field> [ASC|DESC]
| LIMIT <number>
```

### Common Operators

```sql
-- Comparison
WHERE level == "error"
WHERE response_time > 1000
WHERE status_code >= 500

-- Logical
WHERE level == "error" AND service == "api"
WHERE status_code == 404 OR status_code == 500

-- IN operator
WHERE level IN ("error", "fatal", "critical")

-- Pattern matching
WHERE message LIKE "%timeout%"
```

### Aggregations

```sql
-- Count
STATS count()
STATS count() BY level

-- Statistics
STATS avg(response_time), max(response_time), min(response_time)

-- Grouping
STATS count() BY service, level

-- Bucket by time
STATS count() BY bucket(@timestamp, 1 hour)
```

## Example 4: Advanced Query DSL Searches

```bash
# Multi-field search
npx mcporter call ops-mcp-server search-logs-from-elasticsearch \
  index="logs-*" body='{"query":{"multi_match":{"query":"database connection","fields":["message","error"]}}}'

# Aggregation query
npx mcporter call ops-mcp-server search-logs-from-elasticsearch \
  index="logs-*" body='{"size":0,"query":{"match_all":{}},"aggs":{"by_level":{"terms":{"field":"level.keyword"}}}}'
```

### Query DSL Structure

```json
{
  "query": {
    "bool": {
      "must": [
        {"match": {"level": "error"}}
      ],
      "filter": [
        {"range": {"@timestamp": {"gte": "now-1h"}}}
      ],
      "should": [
        {"match": {"service": "api-gateway"}}
      ],
      "must_not": [
        {"match": {"message": "ignore"}}
      ]
    }
  },
  "size": 10,
  "sort": [{"@timestamp": "desc"}],
  "aggs": {
    "by_service": {
      "terms": {"field": "service.keyword"}
    }
  }
}
```

## Example 5: Common Query Patterns

```bash
# Last 30 minutes
npx mcporter call ops-mcp-server query-logs-from-elasticsearch \
  query="FROM logs-* | WHERE @timestamp > NOW() - 30 minutes"

# Count by service
npx mcporter call ops-mcp-server query-logs-from-elasticsearch \
  query="FROM logs-* | STATS count() BY service | SORT count DESC"

# Error count by hour
npx mcporter call ops-mcp-server query-logs-from-elasticsearch \
  query="FROM logs-* | WHERE level == 'error' | STATS count() BY bucket(@timestamp, 1 hour)"

# Top error messages
npx mcporter call ops-mcp-server query-logs-from-elasticsearch \
  query="FROM logs-* | WHERE level == 'error' | STATS count() BY message | SORT count DESC | LIMIT 10"

# Structured field search
npx mcporter call ops-mcp-server query-logs-from-elasticsearch \
  query="FROM logs-* | WHERE http.status_code >= 500 AND http.status_code < 600"

# Trace correlation
npx mcporter call ops-mcp-server query-logs-from-elasticsearch \
  query="FROM logs-* | WHERE trace_id == 'abc123def456' | SORT @timestamp ASC | KEEP @timestamp, service, message, span_id"
```

## Expected Output

### List Indices Response

```
health status index                       docs.count docs.deleted store.size
green  open   logs-app-2024.01.15         1234567    0            5.2gb
yellow open   logs-auth-2024.01.15        456789     0            1.8gb
green  open   logs-system-2024.01.15      789012     0            3.1gb
```

### ES|QL Query Response

```json
{
  "columns": [
    {"name": "@timestamp", "type": "date"},
    {"name": "level", "type": "keyword"},
    {"name": "message", "type": "text"}
  ],
  "values": [
    ["2024-01-15T10:30:00Z", "error", "Database connection timeout"],
    ["2024-01-15T10:29:55Z", "error", "Failed to authenticate user"]
  ]
}
```

## Troubleshooting

### Index Not Found

**Problem:** Error about index not found

**Solutions:**

1. List indices first: `list-log-indices-from-elasticsearch`
2. Check index pattern (use wildcards: `logs-*`)
3. Verify index name spelling

### Query Syntax Error

**Problem:** Invalid query syntax

**Solutions:**

1. For ES|QL: Check SQL-like syntax (use `==` not `=`)
2. For Query DSL: Validate JSON structure
3. Start with simple query and add complexity

### No Results

**Problem:** Query returns no results

**Solutions:**

1. Verify time range includes data
2. Try broader search terms
3. Check field names are correct
4. Remove filters one by one to isolate issue

### Query Too Slow

**Problem:** Query takes too long

**Solutions:**

1. Add time range filter
2. Limit result size (`LIMIT 10`)
3. Use more specific index pattern
4. Add field filters early in query

## Best Practices

### 1. Use ES|QL for New Queries

ES|QL is simpler and more readable than Query DSL.

### 2. Always Include Time Filters

```bash
# Good - limited time range
npx mcporter call ops-mcp-server query-logs-from-elasticsearch \
  query="FROM logs-* | WHERE @timestamp > NOW() - 1 hour"
```

### 3. Use LIMIT to Control Results

```bash
# Good - limited results
npx mcporter call ops-mcp-server query-logs-from-elasticsearch \
  query="FROM logs-* | WHERE level == 'error' | LIMIT 100"
```

### 4. Use Specific Index Patterns

```bash
# Good - specific pattern
npx mcporter call ops-mcp-server query-logs-from-elasticsearch \
  query="FROM logs-app-2024.01.* | LIMIT 10"
```

### 5. Leverage Structured Fields

```bash
# Good - uses indexed field
npx mcporter call ops-mcp-server query-logs-from-elasticsearch \
  query="FROM logs-* | WHERE http.status_code == 500"
```

## Common Query Patterns

### Find Errors

```bash
npx mcporter call ops-mcp-server query-logs-from-elasticsearch \
  query="FROM logs-* | WHERE @timestamp > NOW() - 1 hour | WHERE level IN ('error', 'fatal', 'critical') | SORT @timestamp DESC | LIMIT 50"
```

### Top Error Messages

```bash
npx mcporter call ops-mcp-server query-logs-from-elasticsearch \
  query="FROM logs-* | WHERE @timestamp > NOW() - 24 hours | WHERE level == 'error' | STATS count() BY message | SORT count DESC | LIMIT 10"
```

### Service Health

```bash
npx mcporter call ops-mcp-server query-logs-from-elasticsearch \
  query="FROM logs-* | WHERE @timestamp > NOW() - 1 hour | STATS total = count(), errors = count(level == 'error') BY service"
```

### Request Timeline

```bash
npx mcporter call ops-mcp-server query-logs-from-elasticsearch \
  query="FROM logs-* | WHERE trace_id == 'abc123def456' | SORT @timestamp ASC | KEEP @timestamp, service, message, duration"
```

## Reference

- **Tools**: `list-log-indices-from-elasticsearch`, `search-logs-from-elasticsearch`, `query-logs-from-elasticsearch`
- **ES|QL Documentation**: <https://www.elastic.co/guide/en/elasticsearch/reference/current/esql.html>
- **Query DSL**: <https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html>
- **Time Math**: <https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#date-math>
