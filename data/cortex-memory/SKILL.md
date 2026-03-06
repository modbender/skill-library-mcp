---
name: cortex-memory
description: Long-term structured memory with knowledge graph, entity tracking, temporal reasoning, and cross-session recall. Powered by the Cortex API.
metadata: {"openclaw": {"emoji": "🧠", "category": "memory", "homepage": "https://github.com/Ubundi/Cortex", "primaryEnv": "CORTEX_API_KEY", "requires": {"env": ["CORTEX_API_KEY", "CORTEX_BASE_URL"], "bins": ["curl", "jq"]}}}
---

# Cortex Memory

Cortex gives you a **structured long-term memory** that goes beyond what `memory_search` can do. It extracts facts, entities, and relationships from text, stores them in a knowledge graph, and retrieves them using hybrid search (BM25 + semantic + temporal + graph traversal).

Use Cortex when you need to:
- Recall information across past sessions
- Understand how concepts, people, or projects relate to each other
- Track what changed over time (superseded facts, belief drift)
- Find things that `memory_search` returns noisy or incomplete results for

**Do NOT use Cortex for** simple lookups that `memory_search` handles well (recent session context, keyword matches in today's log). Use native memory first; escalate to Cortex for deeper queries.

**If `@cortex/openclaw-plugin` is also installed:** The plugin automatically injects Cortex memories before every turn inside a `<cortex_memories>` tag. If you see `<cortex_memories>` in the current context, Cortex has already been queried for this turn — do NOT call recall again unless you need a different query (e.g., a follow-up entity lookup or a different query type).

## Setup

Requires `CORTEX_API_KEY` and `CORTEX_BASE_URL` environment variables. These are set in `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "cortex-memory": {
        "enabled": true,
        "apiKey": "sk-cortex-oc-YOUR_KEY",
        "env": {
          "CORTEX_BASE_URL": "https://q5p64iw9c9.execute-api.us-east-1.amazonaws.com/prod"
        }
      }
    }
  }
}
```

## Verify Connection

```bash
curl -s "$CORTEX_BASE_URL/health" -H "x-api-key: $CORTEX_API_KEY" | jq .
```

Expected: `{"status": "ok"}`

## Recall — Search Long-Term Memory

When you need to recall facts, entities, or relationships from past sessions:

```bash
curl -s -X POST "$CORTEX_BASE_URL/v1/retrieve" \
  -H "x-api-key: $CORTEX_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg query "QUERY_HERE" \
    --arg query_type "factual" \
    --argjson top_k 10 \
    '{query: $query, query_type: $query_type, top_k: $top_k}')" | jq '.results[] | {type, content, score, metadata}'
```

**Retrieval modes:**
- `full` (default) — all 5 retrieval channels + graph traversal + reranking. Best recall quality, but slower (~300-600ms depending on region). Use this for thorough queries where you need the best results.
- `fast` — BM25 + semantic only, no graph traversal or reranking (~80-150ms server-side). Use when you need a quick check and can tolerate less thorough results. Pass `"mode": "fast"` in the request body.

```bash
# Fast mode example — quick entity lookup
curl -s -X POST "$CORTEX_BASE_URL/v1/retrieve" \
  -H "x-api-key: $CORTEX_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg query "QUERY_HERE" \
    --arg query_type "factual" \
    --arg mode "fast" \
    --argjson top_k 5 \
    '{query: $query, query_type: $query_type, top_k: $top_k, mode: $mode}')" | jq '.results[] | {type, content, score}'
```

**Query types:**
- `factual` — search FACT and ENTITY nodes (use for: who, what, when, where questions)
- `emotional` — search EMOTION, INSIGHT, VALUE, BELIEF nodes (use for: how does the user feel about X?)
- `combined` — search all node types (default, use when unsure)

**When to use Cortex recall vs. `memory_search`:**

| Situation | Use `memory_search` | Use Cortex recall | Mode |
|---|---|---|---|
| Recent context from today | Yes | No | — |
| Simple keyword lookup | Yes | No | — |
| Cross-session facts | No — often noisy | **Yes** | `fast` usually sufficient |
| Entity relationships ("how does X relate to Y?") | No — can't traverse | **Yes** | `full` (needs graph traversal) |
| Temporal changes ("what changed about X?") | No — no SUPERSEDES tracking | **Yes** | `full` (needs temporal channel) |
| Scoped project queries | No — cross-project noise | **Yes** | `fast` usually sufficient |
| Entity lookup ("who is Sarah Chen?") | Partial — finds mentions | **Yes** — entity node + all connected facts | `fast` for quick check, `full` for complete picture |

## Remember — Store in Long-Term Memory

When the user asks you to remember something important, or when you encounter high-value information that should persist with full entity extraction:

```bash
curl -s -X POST "$CORTEX_BASE_URL/v1/ingest" \
  -H "x-api-key: $CORTEX_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg text "TEXT_TO_REMEMBER" \
    --arg session_id "openclaw:$(date +%Y-%m-%d)" \
    '{text: $text, session_id: $session_id}')" | jq '{nodes_created, edges_created, facts: [.facts[].core], entities: [.entities[].name]}'
```

The response shows what was extracted:
- `facts` — factual statements extracted from the text
- `entities` — named entities (people, companies, places, etc.) with aliases
- `nodes_created` / `edges_created` — graph nodes and relationship edges created

**When to remember:**
- User explicitly asks: "remember this", "store this in Cortex", "don't forget that..."
- Key decisions made during a session
- Important context about people, projects, or preferences
- After writing to MEMORY.md — also send the same content to Cortex for structured extraction

**Session ID convention:**
- General sessions: `openclaw:YYYY-MM-DD` (e.g., `openclaw:2026-02-17`)
- Project-scoped: `openclaw:project-name:topic` (e.g., `openclaw:project-frontend:memory-md`)
- Daily logs (used by the npm plugin's file sync): `openclaw:project-name:daily:YYYY-MM-DD`
- Preferences/standing facts: `openclaw:preferences`

The session ID is used for scoped retrieval — queries can filter to a specific project by matching the session ID prefix.

## Ingest Conversation — End of Session

At the end of a productive session, you can ingest the key conversation turns with proper speaker attribution:

```bash
curl -s -X POST "$CORTEX_BASE_URL/v1/ingest/conversation" \
  -H "x-api-key: $CORTEX_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg session_id "openclaw:$(date +%Y-%m-%d):session-topic" \
    --argjson messages '[
      {"role": "user", "content": "FIRST USER MESSAGE"},
      {"role": "assistant", "content": "FIRST ASSISTANT RESPONSE"},
      {"role": "user", "content": "SECOND USER MESSAGE"}
    ]' \
    '{messages: $messages, session_id: $session_id}')" | jq '{nodes_created, edges_created, facts: [.facts[].core]}'
```

**When to use this:**
- After a session with significant decisions or new information
- Do NOT ingest every conversation — only sessions with lasting value
- Summarize or select key turns rather than dumping the entire transcript
- Keep to 5-15 key messages, not the full history

## Bootstrap — First Run

On first install, ingest the user's existing MEMORY.md to seed the knowledge graph.

**For small MEMORY.md files** (under ~50 lines / ~4KB — most users):

```bash
MEMORY_CONTENT=$(cat ~/.openclaw/workspace/MEMORY.md 2>/dev/null || echo "")
if [ -n "$MEMORY_CONTENT" ]; then
  curl -s -X POST "$CORTEX_BASE_URL/v1/ingest" \
    -H "x-api-key: $CORTEX_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg text "$MEMORY_CONTENT" --arg session_id "openclaw:bootstrap" \
      '{text: $text, session_id: $session_id}')" | jq '{nodes_created, edges_created, facts: (.facts | length), entities: (.entities | length)}'
fi
```

**For large MEMORY.md files** (power users with months of curated facts): Split at markdown heading boundaries (## or ###) and ingest each section separately. Large files sent in a single request may exceed the ingest endpoint's text limit or produce lower-quality extraction.

```bash
# Split MEMORY.md at ## headings and ingest each section
MEMORY_FILE=~/.openclaw/workspace/MEMORY.md
if [ -f "$MEMORY_FILE" ]; then
  SECTION="" TOTAL_FACTS=0 TOTAL_ENTITIES=0
  while IFS= read -r line || [ -n "$line" ]; do
    if echo "$line" | grep -q '^## ' && [ -n "$SECTION" ]; then
      RESULT=$(curl -s -X POST "$CORTEX_BASE_URL/v1/ingest" \
        -H "x-api-key: $CORTEX_API_KEY" \
        -H "Content-Type: application/json" \
        -d "$(jq -n --arg text "$SECTION" --arg session_id "openclaw:bootstrap" \
          '{text: $text, session_id: $session_id}')")
      TOTAL_FACTS=$((TOTAL_FACTS + $(echo "$RESULT" | jq '.facts | length')))
      TOTAL_ENTITIES=$((TOTAL_ENTITIES + $(echo "$RESULT" | jq '.entities | length')))
      SECTION=""
    fi
    SECTION="$SECTION$line
"
  done < "$MEMORY_FILE"
  # Ingest final section
  if [ -n "$SECTION" ]; then
    RESULT=$(curl -s -X POST "$CORTEX_BASE_URL/v1/ingest" \
      -H "x-api-key: $CORTEX_API_KEY" \
      -H "Content-Type: application/json" \
      -d "$(jq -n --arg text "$SECTION" --arg session_id "openclaw:bootstrap" \
        '{text: $text, session_id: $session_id}')")
    TOTAL_FACTS=$((TOTAL_FACTS + $(echo "$RESULT" | jq '.facts | length')))
    TOTAL_ENTITIES=$((TOTAL_ENTITIES + $(echo "$RESULT" | jq '.entities | length')))
  fi
  echo "Bootstrap complete: $TOTAL_FACTS facts, $TOTAL_ENTITIES entities extracted."
fi
```

Run this **once** after installation. Tell the user how many facts and entities were extracted.

## Error Handling

- `401 Unauthorized` — invalid or missing API key. Ask user to check `CORTEX_API_KEY`.
- `422 Validation Error` — malformed request. Check the JSON payload.
- `500 Internal Server Error` — Cortex API issue. Retry once, then fall back to native `memory_search`.
- Network timeout — Cortex is unreachable. Use native memory only and inform the user.

If Cortex is unavailable, **always fall back to `memory_search`**. Never block the user because of a Cortex API issue.

## Examples

### "What company did I join?"
```bash
curl -s -X POST "$CORTEX_BASE_URL/v1/retrieve" \
  -H "x-api-key: $CORTEX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "What company did the user join?", "query_type": "factual", "top_k": 5}' | jq '.results[] | {type, content, score}'
```

### "Remember that I prefer PostgreSQL over MySQL"
```bash
curl -s -X POST "$CORTEX_BASE_URL/v1/ingest" \
  -H "x-api-key: $CORTEX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "User prefers PostgreSQL over MySQL for all database projects.", "session_id": "openclaw:preferences"}' | jq '{facts: [.facts[].core], entities: [.entities[].name]}'
```

### "How does the auth service relate to the API gateway?"
```bash
curl -s -X POST "$CORTEX_BASE_URL/v1/retrieve" \
  -H "x-api-key: $CORTEX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "How does the auth service relate to the API gateway?", "query_type": "factual", "top_k": 10}' | jq '.results[] | {type, content, score, metadata}'
```

## Security

- **NEVER** output the `CORTEX_API_KEY` value in responses, logs, or tool outputs.
- **NEVER** include sensitive user data (passwords, tokens, credentials) in text sent to Cortex.
- The Cortex API uses tenant-level database isolation — the user's data is not accessible to other users.
