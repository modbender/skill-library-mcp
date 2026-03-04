---
name: memory-to-notion
description: >
  Summarize and archive conversation memories to Notion. Trigger when the user says
  "summarize memory", "archive conversation", "save memories", "sync memories to Notion",
  "write memories to Notion", "review and record what we discussed", or any variation asking
  to review, summarize, archive, or export conversation history / chat memories to Notion.
disable-model-invocation: true
user-invocable: true
---

# Memory to Notion

This skill retrieves the user's past conversation history, analyzes it for valuable and meaningful
content, decomposes conversations into **atomic memory entries**, and writes them as rows into
the **Memory Store** Notion Database.

## Database Discovery

This skill uses a **zero-config convention**: the database is always named **"Memory Store"**.

**Locate the database:**

```
POST /v1/search
{
  "query": "Memory Store"
}
```

From the results, find the item with `object: "data_source"` whose title is "Memory Store".
Extract both:
- `data_source_id` -- for querying (`POST /v1/data_sources/{id}/query`)
- `database_id` -- for creating pages (`POST /v1/pages` with `parent: {"database_id": "..."}`)

- **If found** -> use `data_source_id` for queries, `database_id` for page creation.
- **If not found** -> ask the user: "No 'Memory Store' database found in your Notion workspace.
  Which page should I create it under? Please provide a Notion page URL or page ID."
  Then create the database (see Database Creation below).

### Schema

| Property    | Type        | Description                                             |
|-------------|-------------|---------------------------------------------------------|
| Title       | Title       | One-line memory summary (searchable)                    |
| Category    | Select      | Fact / Decision / Preference / Context / Pattern / Skill|
| Content     | Rich Text   | Detailed memory content                                 |
| Source      | Select      | Claude.ai / ClaudeCode / Manual / OpenClaw / Other      |
| Status      | Select      | Active / Archived / Contradicted                        |
| Scope       | Select      | Global / Project                                        |
| Project     | Rich Text   | Project name (set when Scope=Project, leave empty for Global) |
| Expiry      | Select      | Never / 30d / 90d / 1y                                  |
| Source Date | Date        | When the original conversation happened                 |

### Database Creation

When the database does not exist, create it under the user-specified parent page.
Use the Notion create-database API with the schema above.

### Category Definitions

- **Fact**: Objective facts -- user's identity, background, tech stack, tools, environment, organization
- **Decision**: Architecture decisions, technology choices, approach selections
- **Preference**: User preferences -- coding style, tool configuration, interaction habits
- **Context**: Background information -- project context, domain knowledge, observations
- **Pattern**: Behavioral patterns -- workflows, recurring needs
- **Skill**: Skills and knowledge -- commands, APIs, techniques learned

## Platform Adaptation

This skill describes operations using generic Notion REST API format.
Each platform's AI should translate to its available tools using the **fixed mappings** below.
Do NOT guess -- follow these mappings exactly.

### Claude Code / Claude.ai (Notion MCP Tools)

| Operation | SKILL.md Describes | Use MCP Tool | Key Parameters |
|-----------|-------------------|--------------|----------------|
| Discover database | `POST /v1/search` | `notion-search` | `query: "Memory Store"`, `content_search_mode: "workspace_search"` |
| Get IDs | -- | `notion-fetch` | Fetch the database, extract `data_source_id` from `<data-source url="collection://...">` tag |
| Dedup query | `POST /v1/data_sources/{id}/query` | **Not available** | Fall back to `notion-search` with `data_source_url` (see Step 3 note) |
| Create page | `POST /v1/pages` | `notion-create-pages` | `parent: { "data_source_id": "..." }` |
| Update page status | `PATCH /v1/pages/{id}` | `notion-update-page` | `command: "update_properties"` |
| Create database | `POST /v1/databases` | `notion-create-database` | Uses SQL DDL syntax (see Database Creation) |
| Fetch page | `GET /v1/pages/{id}` | `notion-fetch` | `id: "<page_id>"` |

**Critical notes:**
- Discovery MUST use `content_search_mode: "workspace_search"` (default `ai_search` mode may not return databases)
- Structured query for dedup is **not available** in MCP. Use semantic search as fallback:
  `notion-search` with `data_source_url: "collection://<data_source_id>"` and keywords from the candidate memory.
  Then `notion-fetch` each result to compare full properties.
- `notion-create-database` uses SQL DDL syntax, not JSON. See Database Creation section for the DDL.

### OpenClaw / Direct API Access

Use Notion REST API exactly as described in the workflow steps. All operations including
structured query for dedup are fully supported.

## Workflow

### Step 1: Discover Database

Locate the "Memory Store" database. If not found, create it (see above).

### Step 2: Gather Conversation Content

Choose a strategy based on the current platform:

**Claude.ai** (has conversation history API):
- Use `recent_chats(n=20)` to fetch recent conversations
- Use `after`/`before` parameters to filter by time range
- Use `conversation_search` for keyword-based retrieval
- For comprehensive archival, paginate up to ~5 rounds

**Claude Code** (current session only):
- Extract valuable information from the current conversation context
- Triggered when the user says "summarize memory" or similar
- Review facts, decisions, preferences produced in this session
- Cannot access past sessions -- only processes current conversation

### Step 3: Check Existing Memories (Dedup & Conflict Detection)

Before writing, query the database to check for duplicates and conflicts.
For each candidate memory, search Title and Content:

```
POST /v1/data_sources/{data_source_id}/query
{
  "filter": {
    "or": [
      { "property": "Title", "title": { "contains": "<keyword from new memory>" } },
      { "property": "Content", "rich_text": { "contains": "<keyword from new memory>" } }
    ]
  },
  "page_size": 10
}
```

> **MCP platforms (Claude Code / Claude.ai):** Structured query is not available.
> Use `notion-search` with `data_source_url: "collection://<data_source_id>"` and keywords
> from the candidate memory as query. Then `notion-fetch` each result to compare properties.

The query returns full page properties. Check for:
1. **Duplicates**: Same fact already stored -> skip
2. **Updates**: Same topic but info changed -> update existing, mark old as Contradicted if needed
3. **Conflicts**: New info contradicts existing -> create new as Active, mark old as Contradicted

### Step 4: Decompose into Atomic Memories

Each conversation may yield 0-N memory entries. The key principle is **one fact per row**.

**Decomposition rules:**
- Each memory should be self-contained and independently meaningful
- Don't store entire conversation summaries -- extract individual facts, decisions, preferences
- Title should be a single declarative sentence (searchable)
- Content provides enough detail to be useful without the original conversation

**Examples of good decomposition:**

A conversation about "setting up a new Python project" might yield:
```
"User prefers uv over pip for Python dependency management"  -> Category: Preference
"Project OpenClaw uses FastAPI + PostgreSQL architecture"     -> Category: Decision
"User prefers Ruff for code formatting and linting"           -> Category: Preference
"User is a programmer"                                        -> Category: Fact
```

**What NOT to store:**
- Transient Q&A that can be easily re-searched ("What is Python's GIL")
- Pleasantries and small talk
- Failed attempts with no useful outcome
- Information the user explicitly asked to forget

### Step 5: Write to Memory Store

Create pages in the database. For each memory entry, set properties:

```json
{
  "Title": "One-line summary",
  "Category": "Fact|Decision|Preference|Context|Pattern|Skill",
  "Content": "Detailed memory content, sufficient for any AI platform to understand and use",
  "Source": "Claude.ai|ClaudeCode|OpenClaw|Manual|Other",
  "Status": "Active",
  "Scope": "Global|Project",
  "Project": "Project name (set when Scope=Project)",
  "Expiry": "Never|30d|90d|1y",
  "date:Source Date:start": "YYYY-MM-DD",
  "date:Source Date:is_datetime": 0
}
```

**Scope guidelines:**
- **Global**: Cross-project universal -- user preferences, general toolchain, personal habits, global decisions
- **Project**: Project-specific -- project architecture, dedicated config, project-scoped technical decisions
- When uncertain, default to Global
- Project field should match the user's project directory name or repository name (e.g., "OpenClaw")

**Expiry guidelines:**
- **Never**: Stable facts and preferences (name, tools, architecture)
- **1y**: May become outdated (tool versions, project status)
- **90d**: Limited shelf life (current tasks, temporary decisions)
- **30d**: Very transient (this week's todos, temporary workarounds)

### Step 6: Handle Conflicts

If Step 3 found conflicting memories:

1. Update the **old** memory's Status to "Contradicted":
   ```
   PATCH /v1/pages/{old_page_id}
   { "properties": { "Status": { "select": { "name": "Contradicted" } } } }
   ```
2. Create the **new** memory with Status "Active" (default)
3. Optionally note in new Content what it supersedes: "(Updated: previously recorded as XX)"

### Step 7: Report Results

After writing, provide the user with a summary:
- Conversations processed
- Memories created / updated / skipped
- List of new entries with Titles and Categories
- Conflicts detected and how resolved

**Example:**
```
Memory archival complete

Processed 8 conversations, generated 12 memories:
- New: 10
- Updated: 1 (user location updated from Beijing to Shenzhen)
- Skipped: 3 low-value conversations

New memories:
| Title | Category |
|-------|----------|
| User prefers uv for Python dependency management | Preference |
| Project OpenClaw uses FastAPI architecture | Decision |
```

## Important Notes

- **Atomic entries**: One fact per row. Never dump a whole conversation summary into one entry.
- **Language**: Title and Content should be written in the user's primary language (the language they most frequently use in conversations). This ensures memories are searchable and readable in the language the user naturally uses. Do NOT force English -- match the user's language.
- **Idempotent**: Always check for existing memories before writing. Running twice should not create duplicates.
- **Source accuracy**: Auto-set Source based on current platform (Claude.ai -> "Claude.ai", Claude Code -> "ClaudeCode", OpenClaw -> "OpenClaw").
- **Preserve details**: Keep code snippets, commands, config values, URLs verbatim in Content.
- **User control**: Don't store anything the user wouldn't want to see. When in doubt, ask.
- **Cross-platform ready**: Write Content so any AI platform can understand and use it.

## Example Interaction

**User**: summarize memory

**Claude**:
1. Searches for "Memory Store" database, obtains `data_source_id` and `database_id`
2. Reviews current session (Claude Code) or recent chats (Claude.ai)
3. Queries database for existing entries to avoid duplicates
4. Decomposes conversations into atomic memories
5. Writes entries to the database
6. Reports: "Processed 5 conversations, generated 8 new memories, updated 1, skipped 2."
