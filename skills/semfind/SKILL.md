---
name: semfind
description: Semantic search over local text files using embeddings. Use when grep/ripgrep fails to find relevant results because the exact wording is unknown, or when searching by meaning rather than pattern — e.g., searching logs for "deployment issue" when the actual text says "container build failed". Install with `pip install semfind`. Ideal for searching memory files, project docs, logs, and notes by meaning.
---

# semfind

Semantic grep for the terminal. Searches files by meaning using local embeddings (BAAI/bge-small-en-v1.5 + FAISS). No API keys needed.

## When to reach for semfind

1. `grep` or `ripgrep` returned no results or irrelevant results
2. You don't know the exact wording of what you're looking for
3. You want to search by concept/meaning rather than exact text

Do NOT use semfind when grep works — grep is instant and has zero overhead.

## Install

```bash
pip install semfind
```

First run downloads a ~65MB model (~10-30s). Subsequent runs use the cached model.

## Usage

```bash
# Basic search
semfind "deployment issue" logs.md

# Search multiple files, top 3 results
semfind "permission error" memory/*.md -k 3

# With context lines
semfind "database migration" notes.md -n 2

# Force re-index after file changes
semfind "query" file.md --reindex

# Minimum similarity threshold
semfind "auth bug" *.md -m 0.5
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `-k, --top-k` | Number of results | 5 |
| `-n, --context` | Context lines before/after | 0 |
| `-m, --max-distance` | Minimum similarity score | none |
| `--reindex` | Force re-embed | false |
| `--no-cache` | Skip embedding cache | false |

## Output format

Grep-like with similarity scores:

```
file.md:9: [2026-01-15] Fixed docker build with missing env vars  (0.796)
file.md:3: [2026-01-17] Agent couldn't write to /var/log          (0.689)
```

Higher scores (closer to 1.0) mean stronger semantic match.

## Resource usage

- ~250MB RAM while running, freed immediately on exit
- ~65MB model cached in `/tmp/fastembed_cache/`
- ~2s first query (model load), ~14ms cached queries
- Embedding cache in `~/.cache/semfind/`, auto-invalidates on file changes

## Workflow pattern

```bash
# Step 1: Try grep first
grep "deployment" memory/*.md

# Step 2: If grep fails, use semfind
semfind "something went wrong with the deployment" memory/*.md -k 5
```
