---
name: letheclaw
version: 1.0.0
description: Use letheClaw to store, search, and manage memories with criticality and provenance.
trigger: "memory|letheclaw|remember|recall|criticality|provenance"
tools: [network]
---

# letheClaw — Agent memory

You can use the letheClaw API to store and retrieve memories for the user or the current session. The API base URL is in the environment variable **LETHECLAW_API_URL**. 

**Environment patterns:**
- Docker Compose with letheClaw API container: `http://api:8080`
- Host machine from Docker Desktop (Windows/Mac): `http://host.docker.internal:51234`
- Local testing (same machine): `http://localhost:51234`

If LETHECLAW_API_URL is unset, try `http://host.docker.internal:51234` first (Docker Desktop default), then ask the user.

---

## ⚠️ PROTOCOL (NON-NEGOTIABLE)

### Retrieval Rule
When the user asks about **history, decisions, prior work, "what did we do", or any past context:**

1. **ALWAYS query letheClaw API FIRST:**
   ```bash
   curl -s "{LETHECLAW_API_URL}/memory/search?q=<query>&limit=5"
   ```

2. **Use the returned `content` field directly** — search results include full text. No need for `memory_get` or flat file access.

3. **NEVER use `memory_search` tool as the first step.** That tool searches flat markdown files, which are backup/reference only.

4. **Apply criticality filtering when appropriate:**
   - Security/config: add `&min_criticality=0.7`
   - General recall: add `&min_criticality=0.5`
   - Exploratory: no filter

5. **Use tag pre-filtering when query domain is clear** (e.g., `tags=moltbook` for Moltbook questions).

6. **letheClaw is the authoritative memory system.** Flat files may be stale or incomplete.

### Storage Rule
When the user says "log this", "remember that", or you observe something worth recording:

1. **POST to letheClaw API** (see "Store a memory" below)
2. **Assign appropriate criticality:** 0.3 (transient) → 0.5 (useful) → 0.7 (important) → 0.9 (critical)
3. **Tag precisely:** 2-5 specific tags (type + domain, e.g. `["episodic", "security", "moltbook"]`)
4. **Set source:** `operator_input` (user said it), `direct_observation` (you verified it), `inferred` (derived)

**No exceptions.** This is operator-mandated protocol.

---

## Store a memory

- **POST** `{LETHECLAW_API_URL}/memory`
- **Body (JSON):** `content` (required), optional: `source` (e.g. `operator_input`, `direct_observation`, `inferred`), `tags` (array), `operator`, `session_key`, `context`
- **Returns:** `memory_id` (UUID). Save it to update criticality or fetch provenance later.

## Search memories (semantic)

- **GET** `{LETHECLAW_API_URL}/memory/search?q={query}&limit=5`
- Optional: `min_criticality` (0–1) to filter by importance.
- Optional: `tags` (comma-separated) to pre-filter by tag before semantic search (e.g. `tags=moltbook,security`)
- **Returns:** `results` array with `id`, `content` (full text), `criticality`, `tags`, `source`, `created_at`, `access_count`

**Important:** Search results include **full content** — you do NOT need to call memory_get afterward. Use the returned content directly.

**Criticality filtering guidance:**
- Security/config queries: `min_criticality=0.7` (critical knowledge only)
- General recall: `min_criticality=0.5` (useful and above)
- Exploratory search: no filter (all results)

**Tag pre-filtering (performance optimization):**
When query intent is clear, pre-filter by tags to reduce search space:
```bash
# "Latest Moltbook posts"
curl "{LETHECLAW_API_URL}/memory/search?q=posts&tags=moltbook,episodic&limit=5"

# "Security findings"
curl "{LETHECLAW_API_URL}/memory/search?q=findings&tags=security,semantic&min_criticality=0.7&limit=3"
```

## Recent memories

- **GET** `{LETHECLAW_API_URL}/memory/recent`
- **Returns:** Recently stored memories (from cache or DB).

## Update criticality (manual)

- **POST** `{LETHECLAW_API_URL}/memory/{memory_id}/criticality`
- **Body (JSON):** `criticality` (0–1, required), optional `reason`
- Use when the user or you want to mark a memory as more or less important.

## Mark operator correction

- **POST** `{LETHECLAW_API_URL}/memory/{memory_id}/correction`
- No body. Call when the user corrects something about this memory; this boosts criticality and increments a correction counter so provenance shows how often it was corrected.

## Get provenance

- **GET** `{LETHECLAW_API_URL}/memory/{memory_id}/provenance`
- **Returns:** Full memory object plus `events` (history of criticality changes: manual_boost, operator_correction, etc.) and `correction_count`.

## Errors

- **400** — Invalid request or invalid memory ID format.
- **404** — Memory not found (wrong or deleted ID).
- **5xx** — Server/upstream error; suggest checking if letheClaw is running and reachable.

When the user says they want to remember something, search memory, see why a memory is important, or correct a memory, use the appropriate endpoint above.
