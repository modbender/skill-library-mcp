<p align="center">
  <img src="header.png" alt="memory-tools" width="100%">
</p>

# OpenClaw Memory Tools v2

Agent-controlled memory plugin for OpenClaw with confidence scoring, decay, and semantic search.

## What's New in v2

- **File-based storage** - Memories stored as readable markdown files
- **No external APIs** - No OpenAI dependency, everything runs locally
- **QMD search (optional)** - BM25 + vector + reranking via local GGUF models
- **Auto-migration** - Seamlessly upgrades from v1 SQLite/LanceDB storage

## Why Memory-as-Tools?

Traditional AI memory systems auto-capture everything, flooding context with irrelevant information. **Memory-as-Tools** follows the [AgeMem](https://arxiv.org/abs/2409.02634) approach: the agent decides **when** to store and retrieve memories.

```
Traditional: Agent -> always retrieves -> context flooded
Memory-as-Tools: Agent -> decides IF/WHAT to remember -> uses tools explicitly
```

## Features

- **6 Memory Tools**: `memory_store`, `memory_update`, `memory_forget`, `memory_search`, `memory_summarize`, `memory_list`
- **Confidence Scoring**: Track how certain you are about each memory (1.0 = explicit, 0.5 = inferred)
- **Importance Scoring**: Prioritize critical instructions over nice-to-know facts
- **Decay/Expiration**: Temporal memories (events) automatically become stale
- **Human-readable storage**: Markdown files with YAML frontmatter
- **Semantic Search**: Optional QMD-powered hybrid search (BM25 + vector + reranking)
- **Zero External Dependencies**: Everything runs locally, no API keys needed
- **Standing Instructions**: Auto-inject category="instruction" memories at conversation start

## Installation

### Step 1: Install from ClawHub

```bash
clawhub install memory-tools
```

### Step 2: Build the plugin

```bash
cd skills/memory-tools
npm install
npm run build
```

### Step 3: Activate the plugin

```bash
openclaw plugins install --link .
openclaw plugins enable memory-tools
```

### Step 4: Restart the gateway

```bash
openclaw gateway restart
```

### Optional: Install QMD for better search

```bash
npm install -g @tobilu/qmd
```

Without QMD, basic category/tag filtering works. With QMD, you get semantic search (BM25 + vector + reranking using local GGUF models).

### Node Compatibility (QMD)

- `memory-tools` works without QMD on modern Node versions.
- QMD dependencies (notably `better-sqlite3`) may lag behind the latest Node ABI.
- If QMD fails on startup (for example `NODE_MODULE_VERSION` mismatch on Node v25), the plugin now falls back to basic mode.
- To force basic mode explicitly, set `MEMORY_TOOLS_DISABLE_QMD=true`.
- Recommended for full QMD stability: use a Node LTS version supported by your installed QMD build.

## Configuration

Add to `~/.openclaw/openclaw.json`:

```json
{
  "plugins": {
    "slots": {
      "memory": "memory-tools"
    },
    "entries": {
      "memory-tools": {
        "enabled": true,
        "config": {
          "memoriesPath": "~/.openclaw/memories",
          "autoInjectInstructions": false,
          "autoMigrateLegacy": false
        }
      }
    }
  },
  "tools": {
    "alsoAllow": ["group:plugins"]
  }
}
```

### Security Model

- No API keys or external credentials are required by this plugin.
- Data is stored locally in `~/.openclaw/memories` (or your configured `memoriesPath`).
- The plugin can prepend standing-instruction context at `before_agent_start` only when `autoInjectInstructions=true`.
- The plugin can auto-migrate legacy v1 data from `~/.openclaw/memory/tools/memory.db` only when `autoMigrateLegacy=true`.
- Defaults are conservative: both `autoInjectInstructions` and `autoMigrateLegacy` are `false`.

### Verify Installation

```bash
# Restart gateway
openclaw gateway stop && openclaw gateway run

# Check plugin loaded
openclaw plugins list

# Test CLI
openclaw memory-tools stats
```

## Storage Format

Memories are stored as markdown files in `~/.openclaw/memories/`:

```
~/.openclaw/memories/
├── facts/
│   └── abc123-def4-5678-90ab-cdef12345678.md
├── preferences/
│   └── def456-7890-abcd-ef12-345678901234.md
├── instructions/
│   └── ghi789-0abc-def1-2345-678901234567.md
└── .deleted/
    └── old-memory.md
```

Each memory file contains YAML frontmatter with metadata:

```markdown
---
id: abc123-def4-5678-90ab-cdef12345678
category: preference
confidence: 0.9
importance: 0.7
created_at: 2024-01-15T10:30:00Z
tags: [ui, settings]
---

User prefers dark mode in all applications.
```

## Memory Categories

| Category | Use For | Example |
|----------|---------|---------|
| `fact` | Static information | "User's dog is named Rex" |
| `preference` | Likes/dislikes | "User prefers dark mode" |
| `event` | Temporal things | "Dentist appointment Tuesday 3pm" |
| `relationship` | People connections | "User's sister is Sarah" |
| `context` | Current work | "Working on React project" |
| `instruction` | Standing orders | "Always respond in Spanish" |
| `decision` | Choices made | "We decided to use PostgreSQL" |
| `entity` | Contact info | "User's email is x@y.com" |

## Tool Reference

### memory_store

Store a new memory.

```typescript
memory_store({
  content: "User prefers bullet points",
  category: "preference",
  confidence: 0.9,      // How sure (0-1)
  importance: 0.7,      // How critical (0-1)
  decayDays: null,      // null = permanent
  tags: ["formatting"]
})
```

### memory_update

Update an existing memory.

```typescript
memory_update({
  id: "abc-123",
  content: "User prefers numbered lists",  // Optional
  confidence: 0.95                          // Optional
})
```

### memory_forget

Delete a memory.

```typescript
memory_forget({
  id: "abc-123",           // If known
  query: "bullet points",  // Or search
  reason: "User corrected"
})
```

### memory_search

Semantic search (uses QMD if installed, otherwise basic filtering).

```typescript
memory_search({
  query: "formatting preferences",
  category: "preference",      // Optional filter
  minConfidence: 0.7,          // Optional filter
  limit: 10
})
```

### memory_summarize

Get topic summary.

```typescript
memory_summarize({
  topic: "user's work",
  maxMemories: 20
})
```

### memory_list

Browse all memories.

```typescript
memory_list({
  category: "instruction",
  sortBy: "importance",
  limit: 20
})
```

## CLI Commands

```bash
# Show statistics
openclaw memory-tools stats

# List memories
openclaw memory-tools list --category preference

# Search memories (uses QMD if installed)
openclaw memory-tools search "dark mode"

# Export all memories as JSON
openclaw memory-tools export

# Force re-index with QMD
openclaw memory-tools reindex

# Show storage path
openclaw memory-tools path
```

## Debugging

Memories are plain markdown files - just read them:

```bash
cat ~/.openclaw/memories/facts/*.md
ls ~/.openclaw/memories/
```

Export all memories:

```bash
openclaw memory-tools export > memories.json
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    OpenClaw Agent                       │
│                                                         │
│  Agent decides: "This is worth remembering"             │
│         ↓                                               │
│  Calls: memory_store(...)                               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   Memory Tools                          │
├─────────────────────────────────────────────────────────┤
│  store │ update │ forget │ search │ summarize │ list   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                 Storage Layer                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Markdown Files (YAML frontmatter)       │  │
│  │           ~/.openclaw/memories/{category}/*.md    │  │
│  └──────────────────────────────────────────────────┘  │
│                          ↓                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │        QMD Search (optional)                      │  │
│  │        BM25 + Vector + Reranking                  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Migration from v1

v2 automatically detects v1 databases and migrates them:

1. On startup, v2 checks for `~/.openclaw/memory/tools/memory.db`
2. If found, exports all memories to markdown files
3. Original database preserved as backup
4. No manual action required

To enable auto-migration, set `"autoMigrateLegacy": true` in plugin config.

## Development

```bash
# Install dependencies
npm install

# Run tests
npm test

# Run tests with coverage
npm test:coverage

# Type check
npm run typecheck

# Build
npm run build
```

### Environment Variables

- `MEMORY_TOOLS_DISABLE_QMD=true` - Disable QMD for testing

No environment variables are required for credentials.

## Comparison with Other Memory Systems

| Feature | [memU](https://github.com/NevaMind-AI/memU) | [claude-mem](https://github.com/thedotmack/claude-mem) | **memory-tools** |
|---------|------|------------|--------------|
| **Architecture** | 3-tier hierarchical (Resource -> Item -> Category) | Hook-based observer with lifecycle events | Tool-based agent control |
| **Storage Trigger** | Automatic extraction during background processing | Lifecycle hooks (SessionStart, PostToolUse, etc.) | Agent explicitly decides when to store |
| **Storage Backend** | Custom hierarchical | Custom | Markdown files + optional QMD |
| **External APIs** | Varies | Varies | None required |
| **Conflict Handling** | None - relies on proactive pattern detection | None - auto-capture model | Auto-supersede + explicit forget |
| **Context Injection** | Proactive - predicts and pre-loads context | Progressive disclosure (3-layer filtering) | On-demand via memory_search |
| **Token Efficiency** | Compression via fact extraction | ~10x savings via progressive disclosure | Semantic search with configurable limits |
| **Auditability** | Background processing | Hook-based capture | Human-readable markdown files |
| **User Corrections** | Accumulates conflicting facts | Accumulates conflicting facts | Replaces old with new automatically |
| **Best For** | 24/7 agents with predictable patterns | Automatic session continuity | Personal assistants with ongoing relationships |

### Design Philosophy

Different memory systems optimize for different things:

- **Automatic systems** (memU, claude-mem) minimize agent cognitive load by extracting memories in the background. Trade-off: less control over what's captured, conflicts accumulate.

- **Agent-controlled systems** (memory-tools) put the agent in charge of what matters. Trade-off: requires active management, but memories are deliberate choices.

For agents that maintain ongoing relationships with users - where someone might say "no, my favorite color is purple, not blue" - explicit conflict handling prevents contradictory memories from accumulating. Every memory has a clear provenance: the agent decided it was worth remembering, and corrections replace rather than compete with old information.

The file-based storage means you can always `ls ~/.openclaw/memories/` and read exactly what your agent knows. Each memory is a plain markdown file you can edit, delete, or backup.

## References

- [AgeMem Paper](https://arxiv.org/abs/2409.02634) - Memory operations as first-class tools
- [QMD](https://github.com/tobilu/qmd) - Local hybrid search with GGUF models
- [memU](https://github.com/NevaMind-AI/memU) - Hierarchical memory with proactive context
- [claude-mem](https://github.com/thedotmack/claude-mem) - Hook-based automatic memory
- [Mem0](https://github.com/mem0ai/mem0) - AI memory layer
- [OpenClaw](https://github.com/openclaw/openclaw) - Personal AI assistant

## License

MIT - [Purple Horizons](https://github.com/Purple-Horizons)
