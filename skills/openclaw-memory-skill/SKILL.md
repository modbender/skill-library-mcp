# OpenClaw Memory — Agent Skill

**MongoDB-backed long-term memory with Voyage AI semantic search**

## When to Use

Use OpenClaw Memory when:
- ✅ You need to recall prior conversations, decisions, or preferences
- ✅ Building context across multiple sessions
- ✅ Tracking facts, insights, or learnings over time
- ✅ Searching for relevant information semantically (not just keywords)
- ✅ Remembering user preferences, project details, or domain knowledge

**NOT for:**
- ❌ Immediate/short-term context (use conversation history instead)
- ❌ Temporary scratch notes (use files in workspace)
- ❌ Large document storage (use file system or database)

## Available Tools

### `memory_search`

**Semantically search long-term memory.** Use this to recall prior decisions, preferences, context, or facts.

```typescript
memory_search({
  query: "What did we decide about the database schema?",
  maxResults: 6  // optional, default: 6
})
```

**Returns:** Array of memories with similarity scores, text, tags, and metadata.

**When to use:**
- Before answering questions about past work
- When user asks "remember when..." or "what did we say about..."
- To check for existing context before making new decisions
- When solving similar problems to past ones

**Example output:**
```json
{
  "results": [
    {
      "id": "507f1f77bcf86cd799439011",
      "text": "Decided to use MongoDB for vector storage with Atlas Search",
      "score": 0.89,
      "tags": ["decision", "database"],
      "createdAt": "2026-02-20T14:30:00Z"
    }
  ]
}
```

---

### `memory_remember`

**Store a fact, decision, preference, or important context** in long-term memory.

```typescript
memory_remember({
  text: "User prefers TypeScript over JavaScript for new projects",
  tags: ["preference", "programming"],  // optional
  ttl: 2592000  // optional, 30 days default
})
```

**Returns:** Stored memory ID and confirmation.

**When to use:**
- After important decisions are made
- When user states a preference ("I prefer X over Y")
- Key facts or insights discovered during work
- Context that should persist across sessions
- User explicitly asks you to remember something

**Best practices:**
- Be specific and concise (1-2 sentences ideal)
- Include relevant tags for categorization
- Don't store temporary/ephemeral information
- Use structured format when possible (e.g., "Key: value")

---

### `memory_get`

**Read a specific memory file from the workspace.** Use memory_search for semantic recall; use this for targeted file reads.

```typescript
memory_get({
  path: "MEMORY.md",
  from: 1,      // optional, starting line
  lines: 50     // optional, number of lines
})
```

**Returns:** File contents (text).

**When to use:**
- After memory_search to get full context
- Reading structured memory files (MEMORY.md, memory/YYYY-MM-DD.md)
- Targeted line-range reads for efficiency

---

### `memory_forget`

**Delete a specific memory by ID.** Use `memory_search` first to find the memory ID.

```typescript
memory_forget({
  memoryId: "507f1f77bcf86cd799439011"
})
```

**Returns:** Confirmation or error.

**When to use:**
- User explicitly asks to delete/forget something
- Correcting incorrect memories
- Removing outdated information
- Never use proactively without user request

---

### `memory_list`

**Browse stored memories** by recency or tag.

```typescript
memory_list({
  tags: "decision,database",  // optional, comma-separated
  limit: 10,                  // optional, default: 10
  sort: "desc"                // optional, "desc" or "asc"
})
```

**Returns:** Array of memories with metadata (no similarity scores).

**When to use:**
- Browsing recent memories
- Filtering by specific tags
- Audit/review of stored memories
- When user asks "what have you remembered?"

---

### `memory_status`

**Check memory system health and stats.**

```typescript
memory_status()
```

**Returns:** Daemon status, MongoDB connection, Voyage AI status, total memories, uptime.

**When to use:**
- Debugging memory system issues
- User asks about memory capacity or health
- Before relying on memory for critical tasks
- Rarely needed in normal operation

---

## Configuration

Memory tools connect to a daemon at `http://localhost:7654` by default. Configuration is set in `~/.openclaw/openclaw.json`:

```json5
{
  plugins: {
    entries: {
      "openclaw-memory": {
        enabled: true,
        config: {
          daemonUrl: "http://localhost:7654",
          agentId: "openclaw",
          maxResults: 6,
          minScore: 0.5,
          defaultTtl: 2592000  // 30 days
        }
      }
    }
  }
}
```

## Automatic Memory Capture

OpenClaw Memory includes **lifecycle hooks** that capture memories automatically:

### `auto-remember` Hook
Fires after every agent response. Extracts facts, decisions, and preferences using pattern matching:
- "I prefer..." → stored as preference
- "We decided..." → stored as decision
- "Remember that..." → stored as fact
- "Key: value" patterns (structured data)

**Limits:** Max 5 extractions per message, min 10 chars, deduplicates.

### `session-to-memory` Hook
Fires when starting a new session. Summarizes the ending session and stores it as a searchable memory.

### `memory-bootstrap` Hook
Fires on agent startup. Queries for relevant memories (preferences, recent decisions, pinned items) and injects them into context.

### `memory-enriched-tools` Hook
Fires before tool results are saved. Appends related memories as context annotations to Read/Grep/Glob/Bash outputs.

**To disable hooks:** Set `hooksEnabled: false` in plugin config.

---

## Workflow Examples

### Example 1: Recall Prior Decision

**User asks:** "What did we decide about the API authentication?"

**Agent response:**
1. Call `memory_search({ query: "API authentication decision" })`
2. Review results
3. Answer based on stored memory
4. If no results, say "I don't have any memory of that decision"

### Example 2: Store Preference

**User says:** "I prefer Material UI over Tailwind for all React projects"

**Agent response:**
1. Acknowledge the preference
2. Call `memory_remember({ text: "User prefers Material UI over Tailwind for React projects", tags: ["preference", "ui"] })`
3. Confirm it's stored: "Got it, I'll remember that preference"

### Example 3: Check Before Recommending

**User asks:** "What CSS framework should we use?"

**Agent response:**
1. Call `memory_search({ query: "CSS framework preference" })`
2. If match found: "You previously preferred Material UI over Tailwind"
3. If no match: Provide recommendation based on context

### Example 4: Session Continuity

**New session starts:**

1. `memory-bootstrap` hook auto-runs
2. Loads recent preferences, decisions, project context
3. Agent has continuity without user repeating everything

---

## Tips & Best Practices

**Do:**
- ✅ Use `memory_search` before answering questions about past work
- ✅ Store concise, specific facts (1-2 sentences)
- ✅ Tag memories for easy filtering (`preference`, `decision`, `fact`, `project-name`)
- ✅ Trust semantic search (it understands meaning, not just keywords)
- ✅ Let hooks handle routine memory capture (preferences, decisions)

**Don't:**
- ❌ Store temporary/ephemeral information
- ❌ Duplicate conversation history (that's already stored)
- ❌ Store sensitive credentials (use secure storage instead)
- ❌ Forget without user permission (use `memory_forget` sparingly)
- ❌ Overwhelm with too many manual `memory_remember` calls (hooks handle most)

**Search Tips:**
- Use natural language: "database preference" > "db pref"
- Be specific when possible: "TypeScript vs JavaScript decision" > "language"
- Results are ranked by semantic similarity (0-1 score)
- Default `minScore: 0.5` filters low-relevance results

**TTL Guidelines:**
- 7 days: Temporary project context
- 30 days (default): Most facts, decisions, preferences
- 90 days: Important long-term context
- 365 days: Critical knowledge that should persist long-term

---

## Troubleshooting

**"Memory daemon not reachable"**
- Check daemon is running: `curl http://localhost:7654/health`
- Start daemon: `cd openclaw-memory && pnpm dev:daemon`
- Or use Docker: `docker compose up -d`

**"No memories found"**
- Verify memories exist: `memory_list({ limit: 5 })`
- Check agentId matches (`openclaw` by default)
- Try broader search queries
- Lower `minScore` threshold in config

**"Memory search returns irrelevant results"**
- Be more specific in query
- Increase `minScore` threshold (default: 0.5)
- Check tags to filter results
- Verify Voyage AI embeddings are working (not mock mode)

**"Tools not available"**
- Verify plugin is enabled in `openclaw.json`
- Restart OpenClaw gateway
- Check plugin installation: `openclaw plugins list`

---

## Advanced Features

### Web Dashboard

Full installation includes a web dashboard at `http://localhost:3002`:
- Memory browser with semantic search
- Graph visualizer (relationship mapping)
- Conflict resolution (contradiction detection)
- Timeline and analytics

### Reflection Pipeline

9-stage processing pipeline for:
- Duplicate detection (0.92 similarity threshold)
- Contradiction detection (heuristic + LLM)
- Confidence scoring
- Graph relationship extraction
- Entity extraction
- Temporal decay

**Trigger reflection:**
```bash
curl -X POST http://localhost:7654/reflect \
  -H "Content-Type: application/json" \
  -d '{"agentId":"openclaw"}'
```

### Graph Relationships

Memories can be connected via edges:
- `SUPPORTS` — reinforces/supports another memory
- `CONTRADICTS` — conflicts with another memory
- `DERIVES_FROM` — built upon another memory
- `CO_OCCURS` — frequently appears together
- `PRECEDES` — temporal sequence
- `MENTIONS_ENTITY` — references an entity

Access via web dashboard at `/graph`.

---

## Requirements

- MongoDB 8.0+ (local or Atlas)
- Node.js 18+
- OpenClaw CLI
- Optional: Voyage AI API key (mock mode available)

## Installation

```bash
# Install plugin
openclaw plugins install openclaw-memory

# Start daemon
cd openclaw-memory
pnpm install && pnpm dev:daemon

# Or use Docker
docker compose up -d
```

---

## Summary

OpenClaw Memory gives agents **persistent, searchable memory** across sessions:

1. **Search semantically** with `memory_search`
2. **Store facts** with `memory_remember`
3. **Automatic capture** via lifecycle hooks
4. **MongoDB-backed** with Voyage AI embeddings
5. **Web dashboard** for visualization and management

**Use it to build agents that remember, learn, and improve over time.** 🧠

---

**Version:** 0.2.1  
**Author:** Michael Lynn  
**License:** MIT  
**Repository:** https://github.com/mrlynn/openclaw-mongodb-memory
