---
name: deep-current
description: Persistent research thread manager with a CLI for tracking topics, notes, sources, and findings. Pair with a nightly cron job to build a personal research digest over time. The shipped code is a local Python CLI for thread management — research is performed by the agent using its standard web_search and web_fetch tools.
---

# Deep Current

A research thread manager for agents. Track topics you care about, accumulate notes and sources over time, and pair with a scheduled cron job to produce regular research digests.

## Architecture

This skill ships **one component**: a Python CLI (`scripts/deep-current.py`) that manages research threads as local JSON data. It handles:
- Creating, listing, and updating research threads
- Storing notes, sources, and findings per thread
- Thread lifecycle (active/paused/resolved) and decay

**What this skill does NOT ship:** web search, link following, or report generation. Those capabilities come from the agent's built-in tools (`web_search`, `web_fetch`). The cron job prompt instructs the agent to use those tools to research threads, then write findings to a report file.

In short: the CLI manages *what* to research. The agent's existing tools do the *how*.

## How It Works

1. **Threads** — Long-running research topics stored in `deep-current/currents.json`
2. **Nightly job** — A cron job tells the agent which threads to research (agent uses its own `web_search`/`web_fetch` tools)
3. **Reports** — Each night's findings are written to `deep-current-reports/YYYY-MM-DD.md` (one file per run)
4. **Thread CLI** — Manage threads between sessions (add, note, source, finding, status)

## Setup

### 1. Create data directory

```bash
mkdir -p deep-current
```

### 2. Initialize currents.json

```json
{
  "threads": []
}
```

### 3. Schedule the cron job

Create an isolated cron job that runs nightly. The agent will use its own `web_search` and `web_fetch` tools to research each thread, then use the CLI to record findings. Example prompt:

```
You are running a Deep Current research session.

1. Run `python3 scripts/deep-current.py list` to see all active threads.
2. Run `python3 scripts/deep-current.py covered` to see topics and URLs already covered in recent reports. AVOID repeating these.
3. Pick TWO threads based on current relevance — check recent context to decide.
4. For each thread, use web_search and web_fetch to research the topic. Follow interesting links and cross-reference claims. Find NEW angles, developments, or sources not already covered.
5. Update each thread with notes/sources/findings using the deep-current.py CLI.

## Output Format
Create a new file in deep-current-reports/ named YYYY-MM-DD.md:

# Deep Current — [tonight's date]
## [catchy title for thread 1]
[findings with inline source links]
## [catchy title for thread 2]
[findings with inline source links]

Keep it dense and interesting. No fluff. Link to sources. Flag anything actionable.
```

Recommended: run at 1-3am, use a capable model, 30min timeout.

## Thread CLI

Manage research threads with `scripts/deep-current.py`:

| Command | Purpose |
|---------|---------|
| `list` | Show all threads with status |
| `show <id>` | Full thread details |
| `add <title>` | Create new thread |
| `note <id> <text>` | Add dated research note |
| `source <id> <url> [desc]` | Add source/reference |
| `finding <id> <text>` | Record key finding |
| `status <id> <active\|paused\|resolved>` | Change thread status |
| `digest` | Summary of all active threads |
| `decay` | Prune stale threads (>90 days inactive + no recent notes) |
| `covered [days]` | Show topics & URLs from recent reports (default 14 days) to avoid duplication |

Thread IDs are auto-generated slugs from the title. Prefix matching works for short IDs.

## Report Format

Each run creates a standalone file in `deep-current-reports/YYYY-MM-DD.md`. Each report contains:
- Date header
- 2+ research threads with catchy titles
- Dense findings with inline source links
- Actionable flags for anything the user should act on

One file per run — easy to browse, search, or archive.

## Research Quality Guidelines

When running a research session (nightly or manual), the agent should:
- Use `web_search` to find sources, `web_fetch` to read them
- Cross-reference claims across multiple sources
- Cite sources inline with markdown links
- Flag actionable items explicitly
- Write for a smart reader — dense, no filler
- Use catchy thread titles (this is morning reading, make it engaging)
- Distinguish speculation from sourced facts
