# Deep Current

A research thread manager for AI agents. Track topics over time, accumulate notes and sources, and pair with scheduled jobs to produce regular research digests.

Your agent picks the threads. Your agent does the searching. This tool keeps the state.

## What It Does

**Ships:** A zero-dependency Python CLI (`scripts/deep-current.py`) that manages research threads as local JSON.

**Doesn't ship:** Web search, link following, or report generation. Those come from your agent's own tools.

The CLI handles *what* to research. Your agent handles *how*.

## Quick Start

```bash
# Create a thread
python3 scripts/deep-current.py add "Carnivore Diet Research"

# Add notes, sources, findings as you go
python3 scripts/deep-current.py note carnivore "New study on protein satiety in women"
python3 scripts/deep-current.py source carnivore "https://example.com/study" "2024 protein satiety meta-analysis"
python3 scripts/deep-current.py finding carnivore "High-protein diets show 25% better satiety scores"

# See what you're tracking
python3 scripts/deep-current.py list
python3 scripts/deep-current.py show carnivore
python3 scripts/deep-current.py digest
```

## CLI Reference

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
| `decay` | Prune stale threads (>90 days inactive) |

Thread IDs are auto-generated slugs. Prefix matching works (`carn` matches `carnivore-diet-research`).

## Agent Integration

### OpenClaw

Install from [ClawHub](https://clawhub.com):

```bash
clawhub install deep-current
```

Schedule a nightly cron job that tells your agent to pick threads, research them with `web_search`/`web_fetch`, and write findings to `deep-current-reports/YYYY-MM-DD.md`. See [SKILL.md](SKILL.md) for the full cron prompt template.

### Other Agent Frameworks

The CLI is framework-agnostic. Any agent that can:

1. Run shell commands (to call the CLI)
2. Search the web (to do the actual research)
3. Write files (to output reports)

...can use Deep Current. Point your agent at the CLI, give it a prompt like "pick a thread, research it, write findings," and you're set.

### Manual / Script Use

It's just Python with no dependencies. Use it as a personal research tracker without any agent at all:

```bash
python3 scripts/deep-current.py add "Topic I'm curious about"
python3 scripts/deep-current.py note topic "Found an interesting paper on..."
python3 scripts/deep-current.py digest
```

## Data

Everything lives in `deep-current/currents.json` — a single JSON file. Back it up, version it, move it between machines. Reports go to `deep-current-reports/` as individual dated markdown files.

## License

MIT

---

Built by [@meimakes](https://x.com/meimakes) · Available on [ClawHub](https://clawhub.com)
