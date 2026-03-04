# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agent Registry is a **lazy-loading system for Claude Code agents** that reduces context window token usage by 70-90%. Instead of loading all agents upfront (~117 tokens/agent), it maintains a lightweight JSON index (~20-25 tokens/agent) and loads agents on-demand via search.

The project ships as a **Claude Code Skill** (defined in `SKILL.md`) and is installed to `~/.claude/skills/agent-registry/`.

## Architecture

### Core Data Flow

```
registry.json (index) → search.js (BM25 ranking) → get.js (lazy load) → agent .md file
```

### Automatic Discovery (Hook)

```
User prompt → UserPromptSubmit hook → user_prompt_search.js (in-process BM25) → additionalContext → Claude loads agents
```

The `hooks/user_prompt_search.js` hook runs on Bun (Claude Code's runtime) automatically on every user prompt. It reads `registry.json` directly and runs the BM25 search in-process. If high-confidence matches are found (score >= 0.5), they're injected as context. This makes agent discovery transparent.

### Key Components

- **`references/registry.json`** — Lightweight index storing agent metadata (name, summary, keywords, token_estimate, content_hash). This is the only file loaded into context at conversation start.
- **`agents/`** — Migrated agent markdown files, organized by subdirectory categories. Entirely git-ignored (user-specific data).
- **`lib/`** — Shared JavaScript modules (run on Bun):
  - `registry.js` — Path utilities and registry I/O (read/write registry.json, resolve skill paths).
  - `parse.js` — Agent file parsing (extract frontmatter, summary, keywords, token estimates).
  - `search.js` — BM25 + keyword matching search engine. Custom BM25 implementation (no external dependencies).
  - `telemetry.js` — Fire-and-forget anonymous telemetry using fetch. Disabled by default; opt-in via `AGENT_REGISTRY_TELEMETRY=1`. Also respects `AGENT_REGISTRY_NO_TELEMETRY=1` and `DO_NOT_TRACK=1`.
- **`bin/`** — CLI entry points (run via `bun bin/X.js`):
  - `init.js` — Interactive migration wizard with @clack/prompts UI (paginated, category-grouped). Scans `~/.claude/agents/` and `.claude/agents/`, builds the index.
  - `search.js` — Search agents by intent using BM25.
  - `search-paged.js` — Paginated variant for large registries (300+ agents).
  - `get.js` — Load full agent content by name (exact match, then partial match).
  - `list.js` — List all indexed agents with metadata table.
  - `rebuild.js` — Rebuild `registry.json` from agents in the `agents/` directory.
  - `cli.js` — Thin CLI dispatcher (routes subcommands to the above scripts).
- **`hooks/`** — Hook scripts that integrate with Claude Code's event system:
  - `user_prompt_search.js` — `UserPromptSubmit` hook (Bun). Automatically searches the registry on each user prompt using an in-process BM25 engine. Injects matching agents (score >= 0.5) as `additionalContext`. Fails silently on errors.
- **`SKILL.md`** — Skill definition with YAML frontmatter consumed by Claude Code's skill system. Includes hook registration in the `hooks` frontmatter key.
- **`install.sh`** — Bash installer that copies files to `~/.claude/skills/agent-registry/`, creates directory structure, and only installs optional dependencies when `--install-deps` is passed.

### Search Algorithm

`lib/search.js` implements BM25 (Best Matching 25) from scratch with no external search libraries. Keywords from the registry index are matched against query terms with relevance scoring (0.0-1.0).

### Telemetry

CLI scripts call `telemetry.track()` from `lib/telemetry.js`, but network events are sent only if `AGENT_REGISTRY_TELEMETRY=1` is set. Payload remains anonymous (event type, result count, timing, OS, runtime version) and excludes search queries, agent names, and file paths.

## Commands

### Run CLI tools (from repo root)

```bash
bun bin/search.js "query terms"
bun bin/get.js <agent-name>
bun bin/list.js
bun bin/rebuild.js
bun bin/init.js                    # Interactive migration (non-destructive copy)
bun bin/init.js --move             # Destructive move (explicit opt-in)
```

### Run tests

```bash
bun test                  # 101 tests across 5 files (unit + CLI integration)
```

### Install

```bash
./install.sh                 # User-level install to ~/.claude/skills/agent-registry/
./install.sh --project       # Project-level install to .claude/skills/agent-registry/
./install.sh --install-deps  # Optional: install @clack/prompts
```

### Disable telemetry during development

```bash
AGENT_REGISTRY_TELEMETRY=1 bun bin/search.js "query"
```

## Development Notes

- **Bun runtime required.** Bun ships with Claude Code — no additional runtime installation needed.
- **External dependency:** `@clack/prompts` (for interactive checkbox UI in `bin/init.js`). All search/indexing uses only built-in APIs.
- `lib/` modules use CommonJS (require/module.exports). CLI scripts in `bin/` import from `../lib/`.
- `registry.json` and `agents/*` are git-ignored (user-specific data populated during migration).
- The `remotion-video/` directory is git-ignored and unrelated to the core skill (used for promotional video).
