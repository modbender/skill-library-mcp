# MemoClaw API Reference

HTTP endpoint documentation for direct API access. Most agents should use the CLI instead (see SKILL.md).

### Store a memory

```
POST /v1/store
```

Request:
```json
{
  "content": "User prefers dark mode and minimal notifications",
  "metadata": {"tags": ["preferences", "ui"]},
  "importance": 0.8,
  "namespace": "project-alpha",
  "memory_type": "preference",
  "expires_at": "2026-06-01T00:00:00Z",
  "immutable": false
}
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "stored": true,
  "tokens_used": 15
}
```

Fields:
- `content` (required): The memory text, max 8192 characters
- `metadata.tags`: Array of strings for filtering, max 10 tags
- `importance`: Float 0-1, affects ranking in recall (default: 0.5)
- `namespace`: Isolate memories per project/context (default: "default")
- `memory_type`: `"correction"|"preference"|"decision"|"project"|"observation"|"general"` — each type has different decay half-lives (correction: 180d, preference: 180d, decision: 90d, project: 30d, observation: 14d, general: 60d)
- `session_id`: Session identifier for multi-agent scoping
- `agent_id`: Agent identifier for multi-agent scoping
- `expires_at`: ISO 8601 date string — memory auto-expires after this time (must be in the future)
- `pinned`: Boolean — pinned memories are exempt from decay (default: false)
- `immutable`: Boolean — immutable memories cannot be updated or deleted (default: false)

### Store batch

```
POST /v1/store/batch
```

Request:
```json
{
  "memories": [
    {"content": "User uses VSCode with vim bindings", "metadata": {"tags": ["tools"]}},
    {"content": "User prefers TypeScript over JavaScript", "importance": 0.9}
  ]
}
```

Response:
```json
{
  "ids": ["uuid1", "uuid2"],
  "stored": true,
  "count": 2,
  "tokens_used": 28
}
```

Max 100 memories per batch.

### Recall memories

Semantic search across your memories.

```
POST /v1/recall
```

Request:
```json
{
  "query": "what are the user's editor preferences?",
  "limit": 5,
  "min_similarity": 0.7,
  "namespace": "project-alpha",
  "filters": {
    "tags": ["preferences"],
    "after": "2025-01-01",
    "memory_type": "preference"
  }
}
```

Response:
```json
{
  "memories": [
    {
      "id": "uuid",
      "content": "User uses VSCode with vim bindings",
      "metadata": {"tags": ["tools"]},
      "importance": 0.8,
      "similarity": 0.89,
      "created_at": "2025-01-15T10:30:00Z"
    }
  ],
  "query_tokens": 8
}
```

Fields:
- `query` (required): Natural language query
- `limit`: Max results (default: 10)
- `min_similarity`: Threshold 0-1 (default: 0.5)
- `namespace`: Filter by namespace
- `filters.tags`: Match any of these tags
- `filters.after`: Only memories after this date
- `filters.memory_type`: Filter by type (`correction`, `preference`, `decision`, `project`, `observation`, `general`)
- `include_relations`: Boolean — include related memories in results

### List memories

```
GET /v1/memories?limit=20&offset=0&namespace=project-alpha
```

Response:
```json
{
  "memories": [...],
  "total": 45,
  "limit": 20,
  "offset": 0
}
```

### Update memory

```
PATCH /v1/memories/{id}
```

Update one or more fields on an existing memory. If `content` changes, embedding and full-text search vector are regenerated.

Request:
```json
{
  "content": "User prefers 2-space indentation (not tabs)",
  "importance": 0.95,
  "expires_at": "2026-06-01T00:00:00Z"
}
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "User prefers 2-space indentation (not tabs)",
  "importance": 0.95,
  "expires_at": "2026-06-01T00:00:00Z",
  "updated_at": "2026-02-11T15:30:00Z"
}
```

Fields (all optional, at least one required):
- `content`: New memory text, max 8192 characters (triggers re-embedding)
- `metadata`: Replace metadata entirely (same validation as store)
- `importance`: Float 0-1
- `memory_type`: `"correction"|"preference"|"decision"|"project"|"observation"|"general"`
- `namespace`: Move to a different namespace
- `expires_at`: ISO 8601 date (must be future) or `null` to clear expiration
- `pinned`: Boolean — pinned memories are exempt from decay
- `immutable`: Boolean — lock memory from further updates or deletion

### Get single memory

```
GET /v1/memories/{id}
```

Returns full memory with metadata, relations, and current importance.

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "User prefers dark mode",
  "metadata": {"tags": ["preferences", "ui"]},
  "importance": 0.8,
  "memory_type": "preference",
  "namespace": "default",
  "pinned": false,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

CLI: `memoclaw get <uuid>`

### Delete memory

```
DELETE /v1/memories/{id}
```

Response:
```json
{
  "deleted": true,
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Bulk delete

```
POST /v1/memories/bulk-delete
```

Delete multiple memories at once. Free.

Request:
```json
{
  "ids": ["uuid1", "uuid2", "uuid3"]
}
```

Response:
```json
{
  "deleted": 3
}
```

CLI: `memoclaw purge --namespace old-project` (deletes all in namespace)

### Batch update

```
PATCH /v1/memories/batch
```

Update multiple memories in one request. Charged $0.005 per request (not per memory) if any content changes trigger re-embedding.

Request:
```json
{
  "updates": [
    {"id": "uuid1", "importance": 0.9, "pinned": true},
    {"id": "uuid2", "content": "Updated fact", "importance": 0.8}
  ]
}
```

Response:
```json
{
  "updated": 2,
  "memories": [...]
}
```

### Ingest

```
POST /v1/ingest
```

Dump a conversation or raw text, get extracted facts, dedup, and auto-relations.

Request:
```json
{
  "messages": [{"role": "user", "content": "I prefer dark mode"}],
  "text": "or raw text instead of messages",
  "namespace": "default",
  "session_id": "session-123",
  "agent_id": "agent-1",
  "auto_relate": true
}
```

Response:
```json
{
  "memory_ids": ["uuid1", "uuid2"],
  "facts_extracted": 3,
  "facts_stored": 2,
  "facts_deduplicated": 1,
  "relations_created": 1,
  "tokens_used": 150
}
```

Fields:
- `messages`: Array of `{role, content}` conversation messages (optional if `text` provided)
- `text`: Raw text to extract facts from (optional if `messages` provided)
- `namespace`: Namespace for stored memories (default: "default")
- `session_id`: Session identifier for multi-agent scoping
- `agent_id`: Agent identifier for multi-agent scoping
- `auto_relate`: Automatically create relations between extracted facts (default: false)

### Extract facts

```
POST /v1/memories/extract
```

Extract facts from conversation messages via LLM.

Request:
```json
{
  "messages": [
    {"role": "user", "content": "My timezone is PST and I use vim"},
    {"role": "assistant", "content": "Got it!"}
  ],
  "namespace": "default",
  "session_id": "session-123",
  "agent_id": "agent-1"
}
```

Response:
```json
{
  "memory_ids": ["uuid1", "uuid2"],
  "facts_extracted": 2,
  "facts_stored": 2,
  "facts_deduplicated": 0,
  "tokens_used": 120
}
```

### Consolidate

```
POST /v1/memories/consolidate
```

Find and merge duplicate/similar memories.

Request:
```json
{
  "namespace": "default",
  "min_similarity": 0.85,
  "mode": "rule",
  "dry_run": false
}
```

Response:
```json
{
  "clusters_found": 3,
  "memories_merged": 5,
  "memories_created": 3,
  "clusters": [
    {"memory_ids": ["uuid1", "uuid2"], "similarity": 0.92, "merged_into": "uuid3"}
  ]
}
```

Fields:
- `namespace`: Limit consolidation to a namespace
- `min_similarity`: Minimum similarity threshold to consider merging (default: 0.85)
- `mode`: `"rule"` (fast, pattern-based) or `"llm"` (smarter, uses LLM to merge)
- `dry_run`: Preview clusters without merging (default: false)

### Suggested

```
GET /v1/suggested?limit=5&namespace=default&category=stale
```

Get memories you should review: stale important, fresh unreviewed, hot, decaying.

Query params:
- `limit`: Max results (default: 10)
- `namespace`: Filter by namespace
- `session_id`: Filter by session
- `agent_id`: Filter by agent
- `category`: `"stale"|"fresh"|"hot"|"decaying"`

Response:
```json
{
  "suggested": [...],
  "categories": {"stale": 3, "fresh": 2, "hot": 5, "decaying": 1},
  "total": 11
}
```

### Memory relations

Create, list, and delete relationships between memories.

**Create relationship:**
```
POST /v1/memories/:id/relations
```
```json
{
  "target_id": "uuid-of-related-memory",
  "relation_type": "related_to",
  "metadata": {}
}
```

Relation types: `"related_to"|"derived_from"|"contradicts"|"supersedes"|"supports"`

**List relationships:**
```
GET /v1/memories/:id/relations
```

**Delete relationship:**
```
DELETE /v1/memories/:id/relations/:relationId
```

### Assemble context

```
POST /v1/context
```

Build a ready-to-use context block from your memories for LLM prompts.

Request:
```json
{
  "query": "user preferences and project context",
  "namespace": "default",
  "max_memories": 5,
  "max_tokens": 2000,
  "format": "text",
  "include_metadata": false,
  "summarize": false
}
```

Response:
```json
{
  "context": "The user prefers dark mode...",
  "memories_used": 5,
  "tokens": 450
}
```

Fields:
- `query` (required): Natural language description of what context you need
- `namespace`: Filter by namespace
- `max_memories`: Max memories to include (default: 10, max: 100)
- `max_tokens`: Target token limit for output (default: 4000, range: 100-16000)
- `format`: `"text"` (plain) or `"structured"` (JSON with metadata)
- `include_metadata`: Include tags, importance, type in output (default: false)
- `summarize`: Use LLM to merge similar memories in output (default: false)

CLI: `memoclaw context "user preferences and project context" --max-memories 5`

### Search (full-text)

```
POST /v1/search
```

Keyword search using BM25 ranking. Free alternative to semantic recall when you know the exact terms.

Request:
```json
{
  "query": "PostgreSQL migration",
  "limit": 10,
  "namespace": "project-alpha",
  "memory_type": "decision",
  "tags": ["architecture"]
}
```

Response:
```json
{
  "memories": [...],
  "total": 3
}
```

CLI: `memoclaw search "PostgreSQL migration" --namespace project-alpha`

### Memory history

```
GET /v1/memories/{id}/history
```

Returns full change history for a memory (every update tracked).

Response:
```json
{
  "history": [
    {
      "id": "uuid",
      "memory_id": "uuid",
      "changes": {"importance": 0.95, "content": "updated text"},
      "created_at": "2026-02-11T15:30:00Z"
    }
  ]
}
```

### Memory graph

```
GET /v1/memories/{id}/graph?depth=2&limit=50
```

Traverse the knowledge graph of related memories up to N hops.

Query params:
- `depth`: Max hops (default: 2, max: 5)
- `limit`: Max memories returned (default: 50, max: 200)
- `relation_types`: Comma-separated filter (`related_to,supersedes,contradicts,supports,derived_from`)

### Export memories

```
GET /v1/export?format=json&namespace=default
```

Export memories in `json`, `csv`, or `markdown` format.

Query params:
- `format`: `json`, `csv`, or `markdown` (default: json)
- `namespace`, `memory_type`, `tags`, `before`, `after`: Filters

CLI: `memoclaw export --format markdown --namespace default`

### List namespaces

```
GET /v1/namespaces
```

Returns all namespaces with memory counts.

Response:
```json
{
  "namespaces": [
    {"name": "default", "count": 42, "last_memory_at": "2026-02-16T10:00:00Z"},
    {"name": "project-alpha", "count": 15, "last_memory_at": "2026-02-15T08:00:00Z"}
  ],
  "total": 2
}
```

CLI: `memoclaw namespaces`

### Core memories

```
GET /v1/core-memories?limit=10&namespace=default
```

Returns the most important, frequently accessed, and pinned memories — the "core" of your memory store. Free endpoint.

Response:
```json
{
  "memories": [
    {
      "id": "uuid",
      "content": "User's name is Ana",
      "importance": 0.95,
      "pinned": true,
      "access_count": 42,
      "memory_type": "preference",
      "namespace": "default"
    }
  ],
  "total": 5
}
```

CLI: `memoclaw list --sort importance --limit 10` (approximate equivalent)

### Usage stats

```
GET /v1/stats
```

Aggregate statistics: total memories, pinned count, never-accessed count, average importance, breakdowns by type and namespace.

CLI: `memoclaw stats`

### Count memories

```
GET /v1/memories/count?namespace=default
```

Quick count of memories, optionally filtered by namespace.

Response:
```json
{
  "count": 42
}
```

CLI: `memoclaw count` or `memoclaw count --namespace project-alpha`

### Import memories

```
POST /v1/import
```

Import memories from a JSON export (produced by `memoclaw export --format json`). Free.

Request: JSON array of memory objects (same format as export output).

Response:
```json
{
  "imported": 15,
  "skipped": 2
}
```

CLI: `memoclaw import memories.json`

### Migrate markdown files

```
POST /v1/migrate
```

Import `.md` files. The API extracts facts, creates memories, and deduplicates.

CLI: `memoclaw migrate ./memory/`

