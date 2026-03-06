---
name: source-library
description: >
  Searchable knowledge base that captures and cross-references everything users share.
  Auto-triggers when user shares ANY URL (article, tweet, thread, repo, video, paper).
  Saves structured summaries with key claims, quotes, analysis, tags, and decay tracking.
  Cross-references sources, maps connections, detects conflicts, and manages reading queue.
  Triggers on: shared URLs, "source library", "what have I read", "search sources",
  "find that article about", "remember when I shared", "conflicts", "connections".
  Do NOT use for general web browsing, bookmark management, or fetching pages without saving.
allowed-tools: "Bash(node:*)"
compatibility: >
  Requires Node.js 18+. Uses local markdown search for retrieval.
  No API keys needed. No external dependencies. Works on Linux/macOS.
metadata:
  author: DaDefiDon
  version: 2.0.0
  category: knowledge-management
  tags: [sources, research, knowledge-base, cross-reference]
---

# Source Library

A persistent, searchable knowledge base built from everything the user shares. Not a bookmark manager — a cross-referenced memory system with connection mapping, conflict detection, and confidence decay.

## Quick Start

1. `node scripts/source-library.js setup` — creates directories
2. Share any URL in chat — the agent auto-processes and saves it
3. Use `node scripts/source-library.js search "query"` to find past sources

## Auto-Trigger Behavior

When the user shares **any URL**, without being asked:

1. **Search first** — use local source search to find related existing sources. Surface specific connections.
2. **Analyze with context** — discuss the new source with existing knowledge layered in.
3. **Save with substance:**
   ```bash
   node scripts/source-library.js save --name "Title" --url "https://..." --author "Name" --type "article" --tags "topic1, topic2" --claims "Claim 1. Claim 2." --analysis "Why this matters" --context "How it came up"
   ```
4. Every entry must be useful months later without re-reading the original.

## Command Reference

All commands via `node scripts/source-library.js <command>`:

| Command | Description |
|---------|-------------|
| `setup` | Create directories, first-run welcome |
| `save --name "..." --url "..." [--author --type --tags --summary --claims --analysis --context --slug --related --decay --date --force]` | Save a source |
| `list [--type tweet] [--tag crypto] [--decay]` | List sources with optional filters |
| `search "query" [--limit 10]` | Search local source summaries with relevance scoring |
| `stats` | Library statistics (total, by type, by tag, disk usage) |
| `connections [--clusters\|--orphans]` | Map relationships between sources |
| `conflicts` | Detect contradictions via sentiment heuristics |
| `queue add "url" [--note "..."]` | Add URL to reading queue |
| `queue list` | Show queued items |
| `queue next` | Show oldest unprocessed item |
| `queue done "url-or-index"` | Remove from queue |
| `teach "topic" [--limit 20]` | Synthesize knowledge from related sources |
| `import file.json` | Bulk import from JSON (full objects or URL array) |

## Entry Format

Each source lives at `life/source/{slug}/summary.md`:

```markdown
# Title

**Source:** URL
**Author:** Name (@handle)
**Date:** YYYY-MM-DD
**Type:** tweet|thread|article|repo|video|paper
**Tags:** comma-separated
**Decay:** fast|normal|slow

## Key Claims
- Actual arguments, mechanics, data points
- Specific enough to be useful without re-reading original

## Notable Quotes
- Direct quotes worth remembering verbatim

## Analysis
What matters. Connections to other knowledge. Why it's significant.

## Context
Why it was shared. Decisions made based on this.

## Related Sources
- [[other-source-slug]]
```

## Quality Rules

1. **No vibes.** "Interesting macro take" is worthless. Capture specific claims, mechanics, data.
2. **Capture mechanics, not conclusions.** Store the reasoning, not just the takeaway.
3. **Include quotes.** Direct quotes are highest-fidelity knowledge.
4. **Tag generously.** Tags enable future discovery. Include topic, author, domain, entities.
5. **Record decisions.** If a source led to action, capture that in Context.
6. **Cross-reference.** A connected source is knowledge; an isolated source is a bookmark.

## Do NOT Use For

- General web browsing or page fetching without saving
- Bookmark management (no "save for later" without substance)
- Summarizing pages the user didn't ask to save
- Anything outside the user's knowledge base
