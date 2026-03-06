# Source Library

A persistent, searchable knowledge base for OpenClaw agents. Every link you share gets analyzed, cross-referenced, and filed — building a personal research library that gets smarter over time.

## What It Does

- **Auto-captures URLs** — Share any link in chat and your agent saves it with structured metadata, key claims, and analysis
- **Cross-references everything** — Maps connections between sources, detects contradictions, clusters by topic
- **Local relevance search** — Searches your `life/source/*/summary.md` files by title, tags, key claims, and analysis with relevance scores. Zero API keys needed.
- **Confidence decay** — Tracks freshness so you know which sources are stale
- **Reading queue** — Save URLs to process later

## Install

```bash
clawhub install source-library
```

Then in chat, tell your agent to run setup:
```
Run: node scripts/source-library.js setup
```

That's it. Share a URL and your agent handles the rest.

## Requirements

- Node.js 18+
- OpenClaw workspace
- No API keys, no external dependencies

## Commands

All via `node scripts/source-library.js <command>`:

- `setup` — First-run directory creation
- `save` — Save a source with metadata, claims, analysis
- `list` — Browse your library with filters
- `search "query"` — Local relevance search across saved source summaries
- `stats` — Library stats
- `connections` — Map how sources relate to each other
- `conflicts` — Detect contradictions between sources
- `queue add|list|next|done` — Manage reading list
- `teach "topic"` — Synthesize knowledge across sources
- `import file.json` — Bulk import

## How It Works

Sources are stored as markdown files at `life/source/{slug}/summary.md` in your workspace. The built-in `search` command scans and ranks these local files directly — no separate database, no vector store to maintain, no API keys to configure.

Each source captures: title, URL, author, date, type, tags, key claims, notable quotes, analysis, and context. The agent fills these in automatically when you share a link.

The real value is in the cross-referencing. As your library grows, every new source gets connected to what you already know. "This echoes what Dalio said about capital wars" is more useful than a bookmark.

## Example

Here's what a saved source looks like with real content:

```markdown
# Ryan Carson - Code Factory: Agent Auto-Write + Review Setup

**Source:** https://x.com/ryancarson/status/2023452909883609111
**Author:** Ryan Carson (@ryancarson)
**Date:** 2026-02-16
**Type:** thread
**Tags:** ai-workflow, coding-agents, ci-cd, code-review

## Key Claims
- Risk-tier contracts (JSON defining high/low risk paths) remove ambiguity in agent PRs
- Current-head SHA matching is non-negotiable — stale review evidence leads to merging bad code
- Automated remediation loops (agent reads findings → patches → pushes) cut loop time significantly

## Analysis
Production-grade CI/CD for fully autonomous agent coding. The repo enforces quality
through risk tiers and deterministic review loops, not human reviewers.

## Context
Shared during workflow optimization session. Relevant pattern for future dev pipelines.
```

## Author

Built by [@DaDefiDon](https://x.com/DaDefiDon)

## License

ISC
