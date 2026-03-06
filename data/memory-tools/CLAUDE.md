# CLAUDE.md

Project context for Claude Code.

## Project

**memory-tools v2** - Agent-controlled memory plugin for OpenClaw/ClawHub.

- **Repo**: `Purple-Horizons/memory-tools`
- **ClawHub slug**: `memory-tools`
- **Owner**: gianni-dalerta

## Architecture (v2)

- **File-based storage** - Memories stored as markdown files with YAML frontmatter
- **QMD search** - Optional BM25 + vector + reranking via local GGUF models
- **No external APIs** - No OpenAI dependency, everything runs locally
- **Auto-migration** - Seamlessly upgrades from v1 SQLite/LanceDB storage

### Storage Structure
```
~/.openclaw/memories/
├── facts/
│   └── abc123.md
├── preferences/
│   └── def456.md
├── instructions/
│   └── ghi789.md
└── .deleted/
    └── old-memory.md
```

### Memory File Format
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

## Key Decisions

- **v2 rewrote storage layer**: Switched from SQLite + LanceDB + OpenAI to file-based + QMD
- **QMD is optional**: Works without QMD (basic file listing), better search with QMD installed
- **Auto-migration**: v2 detects v1 databases and automatically exports to markdown files
- **Backward compatible API**: Tools interface unchanged, existing integrations work

## QMD Integration

QMD provides hybrid search (BM25 + vector + reranking) using local GGUF models:
- `npm install -g @tobilu/qmd` to install
- Models download on first use (~2GB total)
- Without QMD: basic category/tag filtering only
- With QMD: semantic search across all memories

## Publishing to ClawHub

```bash
clawhub publish . --slug memory-tools --version X.Y.Z --changelog "description"
```

Always use `--slug memory-tools` to update the correct skill.

## Build & Test

```bash
npm run build    # TypeScript compile
npm test         # Run vitest (uses MEMORY_TOOLS_DISABLE_QMD=true in CI)
```

## Environment Variables

- `MEMORY_TOOLS_DISABLE_QMD=true` - Disable QMD for testing
