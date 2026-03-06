# Classic Patterns — Updated for ES 9.x

**Note:** This reference covers read-only query patterns. Mapping design is included
for understanding existing index structure, not for creating/modifying indices.

## Mapping Design (Read-Only Context)

Understanding field types helps construct appropriate queries and aggregations.

### Common Field Types
- `text` — full-text search (tokenized, analyzed). Use for search queries.
- `keyword` — exact match, aggregations, sorting. Use for filters and aggregations.
- `semantic_text` — AI semantic search via inference endpoint (ES 8.11+)
- `dense_vector` — vector embedding field for kNN search (manually managed vectors)
- `integer`, `float`, `double` — numeric fields for range queries and stats
- `boolean`, `date`, `ip` — typed fields for exact and range matching

### Multi-field Pattern
Indices often use text + keyword subfields:
```json
"title": {
  "type": "text",           // for search
  "fields": {
    "raw": { "type": "keyword" }  // for sort/agg
  }
}
```
Query on `title`, sort/aggregate on `title.raw`.

### Text Search Example
```json
GET /products/_search
{
  "query": {
    "match": {
      "description": "organic healthy vegetables"
    }
  }
}
```
Tokenized, analyzed, relevance scoring. Finds documents containing any/all terms.

### Keyword Search Example
```json
GET /products/_search
{
  "query": {
    "term": {
      "category.keyword": "vegetables"
    }
  }
}
```
Exact match, case-sensitive, no analysis. Must match the entire value.

### Inspecting Existing Mappings
```bash
GET /my-index/_mapping
```
Always check mapping before querying to understand available fields and their types.

## Boolean Query (must, filter, should, must_not)

```json
{
  "query": {
    "bool": {
      "must": [
        { "match": { "title": "broccoli" } }      ← scores (relevance)
      ],
      "filter": [
        { "term": { "on_sale": true } },           ← cached, no score
        { "range": { "price": { "lte": 20 } } }   ← cached, no score
      ]
    }
  }
}
```

**Query context vs Filter context:**
- `must` / `should` → query context (scoring), expensive
- `filter` / `must_not` → filter context (cached, yes/no, no scoring)

Use `filter` for exact conditions to improve performance.

## Analyzers

```bash
# Test before indexing
POST _analyze
{
  "analyzer": "english",
  "text": "Fresh running vegetables"
}
```

| Analyzer | Behavior | Use for |
|---|---|---|
| `standard` | lowercase, removes punctuation | General text |
| `keyword` | exact string | Codes, emails, IDs |
| `english` | stems words (running→run) | English prose |
| custom | configurable | Special requirements |

## Aggregations

```json
POST my-index/_search
{
  "size": 0,
  "aggs": {
    "by_category": {
      "terms": {
        "field": "category",   ← must be keyword type
        "size": 20             ← default is 10, increase if needed
      },
      "aggs": {
        "avg_price": { "avg": { "field": "price" } }
      }
    },
    "price_stats": { "stats": { "field": "price" } }
  }
}
```

- `terms` agg requires `keyword` field — text fields fail or give garbage
- Default `size: 10` — always set explicitly
- Cardinality is approximate (HyperLogLog) — exact requires full scan

### Nested Aggregation Example
```json
POST /products/_search
{
  "size": 0,
  "aggs": {
    "variants": {
      "nested": {
        "path": "variants"
      },
      "aggs": {
        "by_color": {
          "terms": { "field": "variants.color" }
        }
      }
    }
  }
}
```
Required when aggregating on `nested` type fields. The `nested` aggregation creates a separate context for the nested documents.

## Pagination

```json
// ✅ Standard — up to 10,000 hits
{ "from": 0, "size": 20 }

// ✅ Deep pagination — search_after
POST my-index/_search
{
  "size": 20,
  "sort": [{ "updated_at": "desc" }, { "_id": "asc" }],
  "search_after": ["2026-02-08T10:00:00Z", "10"]   ← from last result
}

// ✅ Bulk export — Point in Time (consistent snapshot)
POST my-index/_pit?keep_alive=5m
→ { "id": "pit-id..." }

POST _search
{
  "size": 1000,
  "pit": { "id": "pit-id...", "keep_alive": "5m" },
  "sort": [{ "_shard_doc": "asc" }]
}
```

**Point in Time (PIT):** Creates a lightweight view of the index state at the time of creation.
Subsequent searches using the same PIT ID see a consistent snapshot, even if documents
are added/modified during pagination. Essential for reliable bulk exports.

```
```

- `from + size` limit: **10,000 hits** — fails beyond that
- `search_after` → for user-facing deep pagination
- PIT + `search_after` → for bulk export, consistent snapshot
- Scroll API → deprecated for user pagination, still ok for one-time exports

## Sharding

- **Optimal shard size: 10–50 GB per shard**
  - Recommended by Elastic based on search performance benchmarks
  - Smaller shards = more overhead, slower coordination
  - Larger shards = slower recovery, less parallelism
  - Reference: [Elastic's sizing guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/size-your-shards.html)
- Number of shards is fixed at creation — plan ahead
- Single-node local dev: `number_of_replicas: 0`
- Over-sharding kills performance — start with 1 shard for small indices

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| `cluster_block_exception` | Disk > 85%, cluster read-only | Free disk, reset with `PUT _cluster/settings {"persistent":{"cluster.blocks.read_only_allow_delete": null}}` |
| `version_conflict_engine_exception` | Concurrent update | Use `retry_on_conflict: 3` or optimistic locking with `if_seq_no` |
| `circuit_breaker_exception` | Query uses too much memory | Reduce agg scope, add filters first |
| `index_not_found_exception` | Index doesn't exist | Create index or check name |
| `illegal_argument_exception: mapper [x] cannot be changed` | Changing field type after indexing | Reindex to new index |
| Mapping explosion | Dynamic mapping creating too many fields | Set `dynamic: "strict"` and explicit mappings |

## Performance Tips

- `_source: false` + `stored_fields` if you don't need full document
- `"profile": true` in query to see slow clauses
- Avoid leading wildcards `*term` — forces full scan, use `reverse` field instead
- Filter before scoring: `bool.filter` is cached, `bool.must` is not
- Disable `refresh_interval` during heavy indexing, re-enable after
