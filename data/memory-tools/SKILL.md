---
name: memory-tools
description: Agent-controlled memory plugin for OpenClaw with confidence scoring, decay, and semantic search. The agent decides WHEN to store/retrieve memories — no auto-capture noise. v2 uses file-based storage with optional QMD search (no external APIs required).
homepage: https://github.com/Purple-Horizons/memory-tools
metadata:
  openclaw:
    emoji: 🧠
    kind: plugin
---

# Memory Tools v2

Agent-controlled persistent memory for OpenClaw.

## What's New in v2

- **File-based storage** — Memories stored as readable markdown files
- **No external APIs** — No OpenAI dependency, everything runs locally
- **QMD search (optional)** — BM25 + vector + reranking via local GGUF models
- **Auto-migration** — Seamlessly upgrades from v1 SQLite/LanceDB storage

## Why Memory-as-Tools?

Traditional memory systems auto-capture everything, flooding context with irrelevant information. Memory Tools follows the [AgeMem](https://arxiv.org/abs/2409.02634) approach: **the agent decides** when to store and retrieve memories.

## Features

- **6 Memory Tools**: `memory_store`, `memory_update`, `memory_forget`, `memory_search`, `memory_summarize`, `memory_list`
- **Confidence Scoring**: Track how certain you are (1.0 = explicit, 0.5 = inferred)
- **Importance Scoring**: Prioritize critical instructions over nice-to-know facts
- **Decay/Expiration**: Temporal memories automatically become stale
- **Human-readable storage**: Markdown files with YAML frontmatter
- **Conflict Resolution**: New info auto-supersedes old (no contradictions)

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

Without QMD, basic filtering works. With QMD, you get semantic search (BM25 + vector + reranking).

### Node Compatibility (QMD)

- QMD may not be compatible with the newest Node ABI immediately.
- If QMD fails (for example `NODE_MODULE_VERSION` mismatch), memory-tools falls back to basic mode.
- To force basic mode: `MEMORY_TOOLS_DISABLE_QMD=true`.
- For best QMD stability, use a Node LTS version supported by your installed QMD build.

## Security Model

- No API keys or external credentials are required.
- Data is stored locally in `~/.openclaw/memories` (or configured `memoriesPath`).
- The plugin can prepend standing-instruction context at `before_agent_start` when `autoInjectInstructions=true`.
- The plugin can auto-migrate legacy v1 data from `~/.openclaw/memory/tools/memory.db` when `autoMigrateLegacy=true`.
- Defaults are conservative: both `autoInjectInstructions` and `autoMigrateLegacy` are `false`.

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

Each memory file:

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
| fact | Static information | "User's dog is named Rex" |
| preference | Likes/dislikes | "User prefers dark mode" |
| event | Temporal things | "Dentist Tuesday 3pm" |
| relationship | People connections | "Sarah is user's wife" |
| instruction | Standing orders | "Always respond in Spanish" |
| decision | Choices made | "We decided to use PostgreSQL" |
| context | Situational info | "User is job hunting" |
| entity | Named things | "Project Apollo is their startup" |

## Tool Reference

### memory_store
```
memory_store({
  content: "User prefers bullet points",
  category: "preference",
  confidence: 0.9,
  importance: 0.7,
  tags: ["formatting", "communication"]
})
```

### memory_search
```
memory_search({
  query: "formatting preferences",
  category: "preference",
  limit: 10
})
```

### memory_update
```
memory_update({
  id: "abc123",
  content: "User now prefers numbered lists",
  confidence: 1.0
})
```

### memory_forget
```
memory_forget({
  query: "bullet points",
  reason: "User corrected preference"
})
```

### memory_summarize
```
memory_summarize({
  topic: "user's work projects",
  maxMemories: 20
})
```

### memory_list
```
memory_list({
  category: "instruction",
  sortBy: "importance",
  limit: 20
})
```

## CLI Commands

```bash
# Show memory statistics
openclaw memory-tools stats

# List memories
openclaw memory-tools list
openclaw memory-tools list --category fact

# Search memories (requires QMD)
openclaw memory-tools search "dark mode"

# Export all memories as JSON
openclaw memory-tools export

# Force re-index with QMD
openclaw memory-tools reindex

# Show storage path
openclaw memory-tools path
```

## Debugging

Memories are plain markdown files — just read them:

```bash
cat ~/.openclaw/memories/facts/*.md
ls ~/.openclaw/memories/
```

Export all memories:

```bash
openclaw memory-tools export > memories.json
```

## Migration from v1

v2 automatically detects v1 databases and migrates them:

1. On startup, v2 checks for `~/.openclaw/memory/tools/memory.db`
2. If found, exports all memories to markdown files
3. Original database preserved as backup
4. No manual action required

To enable auto-migration, set `autoMigrateLegacy: true` in plugin config.

## License

MIT — [Purple Horizons](https://github.com/Purple-Horizons)
