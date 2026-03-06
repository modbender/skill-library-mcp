# Ghostclaw

> "I see the flow between functions. I sense the weight of dependencies. I know when a module is uneasy."

Ghostclaw is an OpenClaw skill that provides an **architectural code review assistant** focused on system-level flow, cohesion, and tech stack best practices.

## Quick Start

```bash
# Install the skill
./scripts/install.sh

# Run a review on a codebase
./scripts/ghostclaw.sh review /path/to/your/repo

# Set up background monitoring (cron)
export GHOSTCLAW_REPOS=/path/to/repos.txt  # list of git repos
0 9 * * * /path/to/ghostclaw/scripts/watcher.sh
```

## What Ghostclaw Does

- Analyzes codebase structure (file sizes, module boundaries)
- Detects "architectural ghosts" — code smells that hurt maintainability
- Assigns a "vibe score" (0-100) representing architectural health
- Suggests refactoring directions aligned with your tech stack
- Can run as a sub-agent via `openclaw sessions_spawn --agentId ghostclaw`
- Can run as a watcher that opens PRs for improvements

## Modes

- **Review mode**: `ghostclaw.sh review <repo_path>` — one-shot analysis
- **Watcher mode**: `ghostclaw.sh watcher` — monitors multiple repos (configured via `repos.txt`)
- **Sub-agent**: Spawned by OpenClaw when `ghostclaw` codename is invoked

## Configuration

- `scripts/repos.txt` — List of repositories for watcher (one URL per line)
- `GH_TOKEN` — GitHub token for PR automation (optional)
- `NOTIFY_CHANNEL` — Telegram channel ID for alerts (optional)

## Files

```
ghostclaw/
├── SKILL.md — Skill documentation for OpenClaw
├── scripts/
│   ├── ghostclaw.sh — Main CLI entry point
│   ├── analyze.py — Core analysis engine
│   ├── watcher.sh — Cron watcher
│   └── install.sh — Installation script
├── references/
│   └── stack-patterns.md — Tech-stack heuristics
└── assets/ (reserved for future templates)
```

## Currently Supported Stacks

- Node.js / React / TypeScript
- Python (Django, FastAPI)
- Go (basic detection)

Analysis is currently based on file size metrics; future versions will add coupling (import analysis) and naming coherence.

## License

MIT
