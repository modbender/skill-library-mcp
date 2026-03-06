---
name: index1
description: AI memory system for coding agents — code index + cognitive facts, persistent across sessions.
version: 2.0.3
license: Apache-2.0
author: gladego
tags: [mcp, memory, semantic-search, bm25, rag, cognitive, coding-agent]
---

# index1

AI memory system for coding agents with BM25 + vector hybrid search. Provides 6 MCP tools for intelligent code/doc search and cognitive fact recording.

## What it does

- **Dual memory**: corpus (code index) + cognition (episodic facts)
- **Hybrid search**: BM25 full-text + vector semantic search with RRF fusion
- **Structure-aware chunking**: Markdown, Python, Rust, JavaScript, plain text
- **MCP Server**: 6 tools (`recall`, `learn`, `read`, `status`, `reindex`, `config`)
- **CJK optimized**: Chinese/Japanese/Korean query detection with dynamic weight tuning
- **Built-in ONNX embedding**: Vector search works out of the box, no Ollama required
- **Graceful degradation**: Works without any embedding service (BM25-only mode)

## Install

```bash
# Recommended
pipx install index1

# Or via pip
pip install index1

# Or via npm (auto-installs Python package)
npx index1@latest
```

One-click plugin setup:

```bash
index1 setup                 # Auto-configure hooks + MCP for Claude Code
```

Verify:

```bash
index1 --version
index1 doctor        # Check environment
```

## Setup MCP

Create `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "index1": {
      "type": "stdio",
      "command": "index1",
      "args": ["serve"]
    }
  }
}
```

> If `index1` is not in PATH, use the full path from `which index1`.

## Add Search Rules

Add to your project's `.claude/CLAUDE.md`:

```markdown
## Search Strategy

This project has index1 MCP Server configured (recall + 5 other tools). When searching code:

1. Known identifiers (function/class/file names) -> Grep/Glob directly (4ms)
2. Exploratory questions ("how does XX work") -> recall first, then Grep for details
3. CJK query for English code -> must use recall (Grep can't cross languages)
4. High-frequency keywords (50+ expected matches) -> prefer recall (saves 90%+ context)
```

**Impact**:

```
Without rules: Grep "search" -> 881 lines -> 35,895 tokens
With rules:    recall        -> 5 summaries -> 460 tokens (97% savings)
```

## Index Your Project

```bash
index1 index ./src ./docs    # Index source and docs
index1 status                # Check index stats
index1 search "your query"   # Test search
```

## Optional: Multilingual Enhancement

index1 v2 has built-in ONNX embedding (bge-small-en-v1.5). For better multilingual support:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull nomic-embed-text           # Standard, 270MB
# or
ollama pull bge-m3                     # Best for CJK, 1.2GB

index1 config embed_backend ollama
index1 doctor                          # Verify setup
```

Without Ollama, ONNX embedding provides vector search out of the box.

## Web UI

```bash
index1 web                   # Start Web UI on port 6888
index1 web --port 8080       # Custom port
```

## MCP Tools Reference

| Tool | Description |
|------|-------------|
| `recall` | Unified search — code + cognitive facts, BM25 + vector hybrid |
| `learn` | Record insights, decisions, lessons learned (auto-classify + dedup) |
| `read` | Read file content + index metadata |
| `status` | Index and cognition statistics |
| `reindex` | Rebuild index for a path or collection |
| `config` | View or modify configuration |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Tools not showing | Check `.mcp.json` format and `index1` path |
| AI doesn't use recall | Add search rules to CLAUDE.md |
| `command not found` | Use full path from `which index1` |
| Chinese search returns 0 | Install Ollama + `bge-m3` model |
| No vector search | Built-in ONNX should work; run `index1 doctor` |
