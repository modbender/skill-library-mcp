# Retrieval Operations

The Second Brain has five tables with both semantic search and traditional filtering.

**Tables**: `thoughts` (inbox/audit), `people` (relationships), `projects` (work), `ideas` (insights), `admin` (tasks)

**Auth headers** for all requests:
```
-H "apikey: $SUPABASE_SERVICE_ROLE_KEY"
-H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

## 1. Cross-Table Semantic Search (search_all)

Search across all tables by meaning. One query, all knowledge.

```bash
# Embed the query
QUERY_EMBEDDING=$(curl -s -X POST "https://openrouter.ai/api/v1/embeddings" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "openai/text-embedding-3-small", "input": "career changes"}' \
  | jq -c '.data[0].embedding')

# Search all tables
curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/search_all" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query_embedding\": $QUERY_EMBEDDING, \"match_threshold\": 0.5, \"match_count\": 20}"
```

**Returns**: `table_name`, `record_id`, `label`, `detail`, `similarity`, `created_at`

**Example output**:
```json
{
  "table_name": "people",
  "record_id": "uuid...",
  "label": "Sarah",
  "detail": "Thinking about leaving her job",
  "similarity": 0.87,
  "created_at": "2026-02-10T14:30:00Z"
}
```

Use this for "show me everything about X" queries.

## 2. Per-Table Semantic Search

Each table has its own match function for focused search.

### match_thoughts

Search the inbox/audit log:

```bash
QUERY_EMBEDDING=$(curl -s -X POST "https://openrouter.ai/api/v1/embeddings" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "openai/text-embedding-3-small", "input": "website redesign tasks"}' \
  | jq -c '.data[0].embedding')

curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/match_thoughts" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query_embedding\": $QUERY_EMBEDDING, \"match_threshold\": 0.5, \"match_count\": 10, \"filter\": {}}"
```

**Filter by metadata** (optional):
```json
{"filter": {"type": "task"}}
{"filter": {"topics": ["ai"]}}
{"filter": {"people": ["Sarah"]}}
```

### match_people

"What do I know about Sarah?" or "career mentors I've talked to":

```bash
QUERY_EMBEDDING=$(curl -s -X POST "https://openrouter.ai/api/v1/embeddings" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "openai/text-embedding-3-small", "input": "career mentors"}' \
  | jq -c '.data[0].embedding')

curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/match_people" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query_embedding\": $QUERY_EMBEDDING, \"match_threshold\": 0.5, \"match_count\": 10}"
```

### match_projects

"Anything about the website redesign?" or "active projects related to AI":

```bash
QUERY_EMBEDDING=$(curl -s -X POST "https://openrouter.ai/api/v1/embeddings" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "openai/text-embedding-3-small", "input": "website redesign"}' \
  | jq -c '.data[0].embedding')

curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/match_projects" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query_embedding\": $QUERY_EMBEDDING, \"match_threshold\": 0.5, \"match_count\": 10}"
```

### match_ideas

"Ideas about AI coaching" or "thoughts on creative workflow":

```bash
QUERY_EMBEDDING=$(curl -s -X POST "https://openrouter.ai/api/v1/embeddings" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "openai/text-embedding-3-small", "input": "AI coaching ideas"}' \
  | jq -c '.data[0].embedding')

curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/match_ideas" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query_embedding\": $QUERY_EMBEDDING, \"match_threshold\": 0.5, \"match_count\": 10}"
```

### match_admin

"Tasks related to the presentation" or "follow-ups on the proposal":

```bash
QUERY_EMBEDDING=$(curl -s -X POST "https://openrouter.ai/api/v1/embeddings" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "openai/text-embedding-3-small", "input": "presentation follow-ups"}' \
  | jq -c '.data[0].embedding')

curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/match_admin" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query_embedding\": $QUERY_EMBEDDING, \"match_threshold\": 0.5, \"match_count\": 10}"
```

### Tuning threshold

| Threshold | Behavior |
|-----------|----------|
| 0.7+ | High precision — only very close matches |
| 0.5 | Balanced — good default for most queries |
| 0.3 | Wide net — catches loose associations |

Lower the threshold if searches return no results.

## 3. People Queries

### List all people

```bash
curl -s "$SUPABASE_URL/rest/v1/people?select=name,context,follow_ups,tags&order=updated_at.desc" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

### Get specific person

```bash
curl -s "$SUPABASE_URL/rest/v1/people?name=eq.Sarah&select=*" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

### People with follow-ups

```bash
curl -s "$SUPABASE_URL/rest/v1/people?select=name,context,follow_ups&follow_ups=not.is.null&order=updated_at.desc" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

### People by tag

```bash
curl -s "$SUPABASE_URL/rest/v1/people?select=name,context,tags&tags=cs.{mentor}&order=updated_at.desc" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

## 4. Project Queries

### Active projects

```bash
curl -s "$SUPABASE_URL/rest/v1/projects?status=eq.active&select=name,next_action,notes&order=updated_at.desc" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

### Blocked projects

```bash
curl -s "$SUPABASE_URL/rest/v1/projects?status=eq.blocked&select=name,next_action,notes&order=updated_at.desc" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

### All non-done projects

```bash
curl -s "$SUPABASE_URL/rest/v1/projects?status=neq.done&select=name,status,next_action,notes&order=updated_at.desc" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

### Projects with next actions

Good for daily digest:

```bash
curl -s "$SUPABASE_URL/rest/v1/projects?status=eq.active&next_action=not.is.null&select=name,next_action&order=updated_at.desc" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

## 5. Ideas Queries

### Recent ideas

```bash
curl -s "$SUPABASE_URL/rest/v1/ideas?select=title,summary,topics&order=created_at.desc&limit=10" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

### Filter by topic

```bash
curl -s "$SUPABASE_URL/rest/v1/ideas?select=title,summary,topics&topics=cs.{ai}&order=created_at.desc" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

### Semantic search for related ideas

Use `match_ideas` (see section 2 above).

## 6. Admin (Task) Queries

### Pending tasks

```bash
curl -s "$SUPABASE_URL/rest/v1/admin?status=eq.pending&select=name,due_date,notes&order=due_date.asc" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

### Overdue tasks

```bash
curl -s "$SUPABASE_URL/rest/v1/admin?status=neq.done&due_date=lt.2026-02-16&select=name,due_date,notes&order=due_date.asc" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

### Tasks due this week

```bash
curl -s "$SUPABASE_URL/rest/v1/admin?due_date=gte.2026-02-16&due_date=lte.2026-02-22&select=name,due_date,status,notes&order=due_date.asc" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

### All open tasks sorted by due date

```bash
curl -s "$SUPABASE_URL/rest/v1/admin?status=neq.done&select=name,due_date,status,notes&order=due_date.asc.nullslast" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

## 7. Inbox Log (Thoughts) Queries

### Recent captures

```bash
curl -s "$SUPABASE_URL/rest/v1/thoughts?select=content,metadata,created_at&order=created_at.desc&limit=10" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

### Unrouted thoughts

Thoughts that haven't been filed into people/projects/ideas/admin yet:

```bash
curl -s "$SUPABASE_URL/rest/v1/thoughts?select=content,metadata,created_at&metadata->>routed_to=is.null&order=created_at.desc" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

### Filter by type

```bash
curl -s "$SUPABASE_URL/rest/v1/thoughts?select=content,metadata,created_at&metadata->>type=eq.task&order=created_at.desc&limit=10" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

### Filter by topic

```bash
curl -s "$SUPABASE_URL/rest/v1/thoughts?select=content,metadata,created_at&metadata->topics=cs.[\"ai\"]&order=created_at.desc&limit=10" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

### Filter by person

```bash
curl -s "$SUPABASE_URL/rest/v1/thoughts?select=content,metadata,created_at&metadata->people=cs.[\"Sarah\"]&order=created_at.desc" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

### Semantic search with filter

Use `match_thoughts` with the `filter` parameter (see section 2 above).

## 8. Daily Digest Query Pattern

Build a daily digest by querying multiple tables in sequence:

**1. Active projects with next actions**:
```bash
curl -s "$SUPABASE_URL/rest/v1/projects?status=eq.active&next_action=not.is.null&select=name,next_action&order=updated_at.desc"
```

**2. Overdue or due-today admin tasks**:
```bash
TODAY=$(date +%Y-%m-%d)
curl -s "$SUPABASE_URL/rest/v1/admin?status=neq.done&due_date=lte.$TODAY&select=name,due_date,notes&order=due_date.asc"
```

**3. People with follow-ups**:
```bash
curl -s "$SUPABASE_URL/rest/v1/people?follow_ups=not.is.null&select=name,context,follow_ups&order=updated_at.desc&limit=5"
```

**4. Unrouted thoughts**:
```bash
curl -s "$SUPABASE_URL/rest/v1/thoughts?metadata->>routed_to=is.null&select=content,metadata,created_at&order=created_at.desc&limit=10"
```

Combine these into a single briefing.

## 9. Stats

### Count per table

Use `HEAD` with `Prefer: count=exact`:

```bash
# Thoughts count
curl -s "$SUPABASE_URL/rest/v1/thoughts?select=*" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Prefer: count=exact" \
  -I 2>&1 | grep -i content-range

# People count
curl -s "$SUPABASE_URL/rest/v1/people?select=*" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Prefer: count=exact" \
  -I 2>&1 | grep -i content-range

# Projects count
curl -s "$SUPABASE_URL/rest/v1/projects?select=*" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Prefer: count=exact" \
  -I 2>&1 | grep -i content-range

# Ideas count
curl -s "$SUPABASE_URL/rest/v1/ideas?select=*" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Prefer: count=exact" \
  -I 2>&1 | grep -i content-range

# Admin count
curl -s "$SUPABASE_URL/rest/v1/admin?select=*" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Prefer: count=exact" \
  -I 2>&1 | grep -i content-range
```

The `content-range` header returns `0-0/TOTAL`.

### Project status breakdown

```bash
curl -s "$SUPABASE_URL/rest/v1/projects?select=status" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  | jq -r '.[].status' | sort | uniq -c
```

### Task status breakdown

```bash
curl -s "$SUPABASE_URL/rest/v1/admin?select=status" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  | jq -r '.[].status' | sort | uniq -c
```

### Most mentioned people

```bash
curl -s "$SUPABASE_URL/rest/v1/thoughts?select=metadata" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  | jq -r '.[].metadata.people[]?' | sort | uniq -c | sort -rn
```

## 10. Supabase REST Filter Reference

| Operator | Syntax | Meaning |
|----------|--------|---------|
| `eq` | `field=eq.value` | Equals |
| `neq` | `field=neq.value` | Not equals |
| `gt` | `field=gt.value` | Greater than |
| `gte` | `field=gte.value` | Greater than or equal |
| `lt` | `field=lt.value` | Less than |
| `lte` | `field=lte.value` | Less than or equal |
| `cs` | `field=cs.value` | Contains (arrays) |
| `is` | `field=is.null` | Is null |
| `not.is` | `field=not.is.null` | Is not null |
| `->>` | `metadata->>key=eq.value` | JSONB text access |
| `->` | `metadata->key=cs.value` | JSONB sub-object/array |

**Combining filters**: Use `&` to stack filters:
```
?status=eq.active&due_date=gte.2026-02-16&order=due_date.asc
```

**Ordering**:
- `order=field.asc` — ascending
- `order=field.desc` — descending
- `order=field.asc.nullslast` — nulls at the end

---

Built by Limited Edition Jonathan • natebjones.com
