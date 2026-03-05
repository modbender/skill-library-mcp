---
name: nate-jones-second-brain
description: Set up and operate a personal knowledge system using Supabase (pgvector) and OpenRouter. Five structured tables — thoughts (inbox log), people, projects, ideas, admin — with AI-powered classification, confidence-based routing, and semantic search across all categories. Captures thoughts from any source, classifies them via LLM, routes them to the right table (the Sorter), rejects low-confidence classifications (the Bouncer), and logs everything (the Receipt). Two opinionated primitives — Supabase for persistent context architecture, OpenRouter as the AI gateway — that unlock unlimited applications on top. The foundation layer for a personal knowledge system. By Limited Edition Jonathan • natebjones.com
metadata: {"openclaw": {"requires": {"env": ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "OPENROUTER_API_KEY"]}, "homepage": "https://natebjones.com"}}
---

# Nate Jones Second Brain

When intelligence is abundant, context becomes the scarce resource. This skill is context architecture — a persistent, searchable knowledge layer that turns your agent into a personal knowledge manager.

Two opinionated primitives:

- **Supabase** — your database, and so much more. PostgreSQL + pgvector. Stores thoughts, people, projects, ideas, and tasks as structured data with vector embeddings. REST API built in. Your data, your infrastructure. Models come and go; your context persists. And once you have a Supabase project, you've unlocked the foundation for everything else you'll want to build — the Second Brain is just the beginning.
- **OpenRouter** — your AI gateway. One API key, every model. Embeddings and LLM calls for classification and routing. Swap models by changing a string. Future-proof by design.

Everything else — how you capture thoughts, how you retrieve them, what you build on top — is application layer. The skill covers the foundation.

> If the tables don't exist yet, see `{baseDir}/references/setup.md`

## Building Blocks

These are the operational concepts behind the system. Understanding them helps you operate correctly.

| Block | What It Does | Implementation |
|-------|-------------|----------------|
| **Drop Box** | One frictionless capture point | Everything goes to `thoughts` first |
| **Sorter** | AI classification + routing | LLM classifies type, then routes to structured table |
| **Form** | Consistent data contracts | Each table has a defined schema |
| **Filing Cabinet** | Source of truth per category | `people`, `projects`, `ideas`, `admin` tables |
| **Bouncer** | Confidence threshold | confidence < 0.6 = don't route, stay in inbox |
| **Receipt** | Audit trail | `thoughts` row logs what came in, where it went |
| **Tap on the Shoulder** | Proactive surfacing | Daily digest queries (application layer) |
| **Fix Button** | Agent-mediated corrections | Move records between tables on user request |

Full conceptual framework: `{baseDir}/references/concepts.md`

## Five Tables

| Table | Role | Key Fields |
|-------|------|------------|
| `thoughts` | Inbox Log / audit trail | content, embedding, metadata (type, topics, people, confidence, routed_to) |
| `people` | Relationship tracking | name (unique), context, follow_ups, tags, embedding |
| `projects` | Work tracking | name, status, next_action, notes, tags, embedding |
| `ideas` | Insight capture | title, summary, elaboration, topics, embedding |
| `admin` | Task management | name, due_date, status, notes, embedding |

Every table has semantic search via its own `match_*` function. Cross-table search via `search_all`.

## Routing Rules

When a thought is classified:

| Type | Route | Action |
|------|-------|--------|
| `person_note` | `people` | Upsert: create person or append to existing context |
| `task` | `admin` | Insert new task (status=pending) |
| `idea` | `ideas` | Insert new idea |
| `observation` | none | Stays in thoughts only |
| `reference` | none | Stays in thoughts only |

If confidence < 0.6, don't route. Leave in thoughts, tell user.

## Quick Start

### Capture a thought (full pipeline)

```bash
# 1. Embed
EMBEDDING=$(curl -s -X POST "https://openrouter.ai/api/v1/embeddings" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "openai/text-embedding-3-small", "input": "Sarah mentioned she is thinking about leaving her job to start consulting"}' \
  | jq -c '.data[0].embedding')

# 2. Classify (run in parallel with step 1)
METADATA=$(curl -s -X POST "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "openai/gpt-4o-mini", "response_format": {"type": "json_object"}, "messages": [{"role": "system", "content": "Extract metadata from the captured thought. Return JSON with: type (observation/task/idea/reference/person_note), topics (1-3 tags), people (array), action_items (array), dates_mentioned (array), confidence (0-1), suggested_route (people/projects/ideas/admin/null), extracted_fields (structured data for destination table)."}, {"role": "user", "content": "Sarah mentioned she is thinking about leaving her job to start consulting"}]}' \
  | jq -r '.choices[0].message.content')

# 3. Store in thoughts (the Receipt)
curl -s -X POST "$SUPABASE_URL/rest/v1/thoughts" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "[{\"content\": \"Sarah mentioned she is thinking about leaving her job to start consulting\", \"embedding\": $EMBEDDING, \"metadata\": $METADATA}]"

# 4. Route based on classification (if confidence >= 0.6)
```

Full pipeline with routing logic: `{baseDir}/references/ingest.md`

### Semantic search (single table)

```bash
QUERY_EMBEDDING=$(curl -s -X POST "https://openrouter.ai/api/v1/embeddings" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "openai/text-embedding-3-small", "input": "career changes"}' \
  | jq -c '.data[0].embedding')

curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/match_thoughts" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query_embedding\": $QUERY_EMBEDDING, \"match_threshold\": 0.5, \"match_count\": 10, \"filter\": {}}"
```

### Cross-table search

```bash
curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/search_all" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query_embedding\": $QUERY_EMBEDDING, \"match_threshold\": 0.5, \"match_count\": 20}"
```

Returns `table_name`, `record_id`, `label`, `detail`, `similarity`, `created_at` from all tables.

### List active projects

```bash
curl -s "$SUPABASE_URL/rest/v1/projects?status=eq.active&select=name,next_action,notes&order=updated_at.desc" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

### List pending tasks

```bash
curl -s "$SUPABASE_URL/rest/v1/admin?status=eq.pending&select=name,due_date,notes&order=due_date.asc" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY"
```

## Ingest Pipeline

When content arrives from any source:

1. **Embed** the text via OpenRouter (1536-dim vector)
2. **Classify** via OpenRouter LLM (type, topics, people, confidence, suggested route)
3. **Log** in `thoughts` (the Receipt — always, regardless of routing)
4. **Bounce check** — if confidence < 0.6, stop here
5. **Route** to structured table based on type (the Sorter)
6. **Confirm** to the user what was captured and where it was filed

Full pipeline details: `{baseDir}/references/ingest.md`

## Metadata Schema

Every thought gets classified with:

| Field | Type | Values |
|-------|------|--------|
| `type` | string | `observation`, `task`, `idea`, `reference`, `person_note` |
| `topics` | string[] | 1-3 short topic tags (always at least one) |
| `people` | string[] | People mentioned (empty if none) |
| `action_items` | string[] | Implied to-dos (empty if none) |
| `dates_mentioned` | string[] | Dates in YYYY-MM-DD format (empty if none) |
| `source` | string | Where it came from: `slack`, `signal`, `cli`, `manual`, etc. |
| `confidence` | float | LLM classification confidence (0-1). The Bouncer uses this. |
| `routed_to` | string | Which table the thought was filed into (null if unrouted) |
| `routed_id` | string | UUID of the record in the destination table (null if unrouted) |

## References

- **Conceptual framework:** `{baseDir}/references/concepts.md`
- **First-time setup:** `{baseDir}/references/setup.md`
- **Database schema (SQL):** `{baseDir}/references/schema.md`
- **Ingest pipeline details:** `{baseDir}/references/ingest.md`
- **Retrieval operations:** `{baseDir}/references/retrieval.md`
- **OpenRouter API patterns:** `{baseDir}/references/openrouter.md`

## Env Vars

| Variable | Service |
|----------|---------|
| `SUPABASE_URL` | Supabase project REST base URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase auth (full access) |
| `OPENROUTER_API_KEY` | OpenRouter API key |

## Security Notes

**Why service_role key?** Supabase provides two keys: `anon` (public, respects RLS) and `service_role` (full access, bypasses RLS). This skill uses `service_role` because:

- This is a **single-user personal knowledge base**, not a multi-tenant app
- Your agent IS the trusted server-side component
- The RLS policy restricts access to `service_role` only — the most restrictive option
- Using the `anon` key would require loosening RLS to allow anonymous access to your thoughts, which is worse

**Data sent to OpenRouter:** All captured text (thoughts, names, action items) is sent to OpenRouter for embedding and classification. This is inherent to the design — you need AI to understand meaning. Don't capture highly sensitive information unless you accept OpenRouter's data handling policies.

**Key handling:** Store `SUPABASE_SERVICE_ROLE_KEY` and `OPENROUTER_API_KEY` securely. Never commit them to public repos. Rotate periodically. In OpenClaw, store them in `openclaw.json` under `skills.entries` or as environment variables.

---

Built by Limited Edition Jonathan • natebjones.com
