# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

`clawctl` — coordination layer for OpenClaw agent fleets. Task board, messaging, activity feed via CLI. Python package with Click, backed by SQLite (WAL mode).

## Development Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
```

The `clawctl` entrypoint is registered via `pyproject.toml` `[project.scripts]`. After install, use `.venv/bin/clawctl` or activate the venv.

## Testing

No test framework yet. Manual verification against a temp database:

```bash
CLAW_DB=/tmp/test.db .venv/bin/clawctl init
CLAW_DB=/tmp/test.db .venv/bin/clawctl add "Test task" -p 1
CLAW_DB=/tmp/test.db CLAW_AGENT=agent1 .venv/bin/clawctl claim 1
CLAW_DB=/tmp/test.db .venv/bin/clawctl board
rm -f /tmp/test.db
```

Always use `CLAW_DB=/tmp/test.db` to avoid touching the real database at `~/.openclaw/clawctl.db`.

## Architecture

Two separate layers share `clawctl.db` — the CLI writes directly to SQLite, Flask is a read-mostly viewer:

- **`clawctl/db.py`** — All SQL lives here. Every query uses `?` parameterized placeholders. Mutating functions return `(ok: bool, payload)` tuples. The `get_db()` context manager handles commit/rollback/close. This module is imported by both the CLI and the Flask server.
- **`clawctl/cli.py`** — Click commands. Each subcommand is a thin wrapper that calls `db.*` functions and formats output. The `print_columnar()` helper handles aligned table output with Unicode-aware width calculation.
- **`clawctl/schema.sql`** — Loaded by `db.init_db()` via `Path(__file__).parent`. Uses `CREATE TABLE IF NOT EXISTS` so re-running init is safe.
- **`dashboard/server.py`** — Flask app that imports `clawctl.db`. Read-only except for claim/complete endpoints. Persistent auth token saved to `~/.openclaw/.clawctl-token`. Not part of the installable package.
- **`dashboard/index.html`** — Single-file vanilla JS web UI. Tailwind via CDN. SSE for live updates.

## Key Design Decisions

**Race safety**: `claim_task()` and `complete_task()` use atomic single-UPDATE patterns with `WHERE` guards and `rowcount` checks — no read-then-write races. This matters because multiple agents hit the same DB concurrently.

**Blocking is normalized**: Task dependencies live in the `task_deps` join table (not JSON columns). The `UNIQUE(task_id, blocked_by)` constraint prevents duplicate deps.

**`list` excludes done/cancelled by default** and sorts active work by status priority. `--all` flips to newest-first for history browsing.

**`CLAW_AGENT` fallback**: Falls back to `$USER` silently in `db.py` but `cli.py` warns once via `_warn_agent_fallback()` on identity-sensitive commands.

**Activity metadata**: Mutating commands accept `--meta` (JSON string) stored in `activity.meta`. Shown in feed with `--meta` flag.

## Environment Variables

- `CLAW_DB` — Database path (default: `~/.openclaw/clawctl.db`)
- `CLAW_AGENT` — Agent identity (default: `$USER`)

## Conventions

- SQL goes in `db.py`, never in `cli.py` or `server.py`
- All new SQL must use `?` parameterized queries — no string interpolation
- `db.py` functions accept a `conn` parameter (from `get_db()` context manager), not a path
- CLI functions call `sys.exit(1)` on conflicts/not-found, exit 0 on success including idempotent no-ops
