# clawctl

Coordination layer for [OpenClaw](https://github.com/openclaw/openclaw) agent fleets. Task board, inter-agent messaging, activity feed, and a live web dashboard — all backed by a single SQLite database.

```
$ clawctl board

═══ CLAWCTL ═══  agent: chat

── ○ pending (2) ──
  #4 Summarize weekly spending from transaction exports
  #6 Find showtimes for new releases this weekend [movie]

── ▶ in_progress (2) ──
  #1 Research best noise-cancelling headphones under $300 [research]
  #5 Write a Python script to rename photos by EXIF date [coding]

── ✗ blocked (1) ──
  #3 File notes from the headphone research [notes]

── ✓ done (1) ──
  #2 Check portfolio risk exposure for earnings week [trading]
```

## Why this exists

Multiple agents working in parallel need a shared source of truth. Without one, you get duplicate work, missed handoffs, and no audit trail.

clawctl is the answer for OpenClaw fleets:

- **Zero infrastructure.** Local SQLite in WAL mode. No cloud, no signup, no build step.
- **SSH-queryable.** `ssh your-vps clawctl board` works out of the box.
- **Race-safe.** Atomic claims and completions via single-UPDATE patterns with WHERE guards. No read-then-write races.
- **Auditable.** Every mutation hits an append-only activity log with optional JSON metadata for linking PRs, issues, test results.
- **OpenClaw-native.** Install as a skill, drop into any agent's workflow.

## Install

```bash
# As an OpenClaw skill (coming soon)
# openclaw skills install clawctl

# Standalone
git clone https://github.com/lludlow/clawctl.git
cd clawctl
pip install .

# For development
pip install -e .
```

**Requirements:** Python >= 3.9, Click, Flask

## Quick start

```bash
# Initialize
clawctl init

# Register the fleet
clawctl register chat --role "everyday triage & delegation"
clawctl register research --role "deep reasoning & web search"
clawctl register coding --role "sandboxed code execution"
clawctl register notes --role "knowledge graph & note-taking"
clawctl register trading --role "read-only market analysis"
clawctl register family --role "mention-gated secure responder"
clawctl register movie --role "watchlists & recommendations"

# Chat agent delegates work to specialists
CLAW_AGENT=chat clawctl add "Research best noise-cancelling headphones under $300" --for research
CLAW_AGENT=chat clawctl add "Write a Python script to rename photos by EXIF date" --for coding -p 1
CLAW_AGENT=chat clawctl add "File notes from the headphone research" --for notes

# Research agent picks up its task
CLAW_AGENT=research clawctl claim 1
CLAW_AGENT=research clawctl start 1
CLAW_AGENT=research clawctl done 1 -m "Top 3 picks with comparison table" \
  --meta '{"note":"~/notes/headphone-research.md"}'

# Research hands off to notes for filing
CLAW_AGENT=research clawctl msg notes "Research complete, ready to file" --task 3

# Monitor
clawctl board
clawctl fleet
clawctl feed --last 10
```

## Agent integration

The typical agent loop:

```bash
# On startup — check messages, find work
CLAW_AGENT=coding clawctl checkin
CLAW_AGENT=coding clawctl inbox --unread
CLAW_AGENT=coding clawctl next

# Do the work, then close out
CLAW_AGENT=coding clawctl done <id> -m "Script written and tested" \
  --meta '{"script":"~/scripts/rename-photos.py","tests":"passed"}'
```

Add a heartbeat to each agent's cron:

```
*/10 * * * * CLAW_AGENT=chat clawctl checkin
*/10 * * * * CLAW_AGENT=research clawctl checkin
*/10 * * * * CLAW_AGENT=coding clawctl checkin
```

Add to each agent's system prompt or AGENTS.md:

```
Before starting work: clawctl inbox --unread && clawctl list --mine
After completing work: clawctl done <id> -m "what I did"
Only claim tasks assigned to you or matching your role.
```

> If `CLAW_AGENT` is not set, clawctl falls back to `$USER` and prints a one-time warning on identity-sensitive commands.

## Commands

### Tasks

| Command | Description |
|---------|-------------|
| `add SUBJECT` | Create a task. Options: `-d` description, `-p 0\|1\|2` priority, `--for AGENT` pre-assign, `--parent ID` subtask |
| `list` | List active tasks. Options: `--mine`, `--status STATUS`, `--owner AGENT`, `--all` (include done/cancelled) |
| `next` | Show the highest-priority actionable task for the current agent |
| `claim ID` | Claim a task. Options: `--force` to override, `--meta JSON` |
| `start ID` | Begin work (transitions to in_progress). Options: `--meta JSON` |
| `done ID` | Complete a task. Options: `-m` note, `--force`, `--meta JSON` |
| `review ID` | Mark task as ready for review. Options: `--meta JSON` |
| `cancel ID` | Cancel a task. Options: `--meta JSON` |
| `block ID --by OTHER` | Mark task as blocked. Options: `--meta JSON` |
| `board` | Kanban board view grouped by status |

### Messages

| Command | Description |
|---------|-------------|
| `msg AGENT BODY` | Send a message. Options: `--task ID`, `--type TYPE` |
| `broadcast BODY` | Message all agents (type: alert) |
| `inbox` | Read messages. Options: `--unread` |

### Fleet

| Command | Description |
|---------|-------------|
| `register NAME` | Register an agent. Options: `--role TEXT` |
| `checkin` | Heartbeat — update presence, check for unread |
| `fleet` | Show all agents with status and current task |
| `whoami` | Show identity, role, and DB path |

### Monitoring

| Command | Description |
|---------|-------------|
| `feed` | Activity log. Options: `--last N`, `--agent NAME`, `--meta` |
| `summary` | Fleet overview with counts and recent events |

### Dashboard

| Command | Description |
|---------|-------------|
| `dashboard` | Start the web UI. Options: `--port INT` (default: 3737), `--verbose` |
| `dashboard --stop` | Stop the running dashboard |

## Task statuses

```
pending ─→ claimed ─→ in_progress ─→ done
                    ↘ blocked ↗     ↘ cancelled
                    ↘ review  ↗
```

`list` excludes done/cancelled by default and sorts by status priority (in_progress > claimed > blocked > review > pending), oldest first. `--all` flips to newest-first for history browsing.

## Activity metadata

Mutating commands (`claim`, `start`, `done`, `block`) accept `--meta` with a JSON string stored in the activity log. Use it to link back to external artifacts:

```bash
clawctl claim 1 --meta '{"source":"whatsapp","channel":"general"}'
clawctl done 1 -m "Top 3 picks with pros/cons" --meta '{"note":"~/notes/headphone-research.md"}'

# Review what happened overnight
clawctl feed --last 50 --agent research --meta
```

## Web dashboard

A live web UI served by Flask with token authentication and SSE for real-time updates.

```bash
clawctl dashboard
# Opens at http://localhost:3737/?token=<TOKEN>
```

Features:
- Live board with SSE push updates (no polling)
- Task detail view with messages and metadata grid
- Complete and delete actions from the UI
- Terminal/hacker aesthetic with optional CRT effects
- Keyboard accessible (Esc to close, Tab trapping in modals)
- Works on narrow viewports
- Token persisted at `~/.openclaw/.clawctl-token` across restarts

The dashboard is read-mostly — it shares the same SQLite database the CLI writes to. The CLI is the primary interface; the dashboard is for monitoring.

## Architecture

```
┌─────────────────────────────┐
│  clawctl CLI (Python/Click) │ ← Every agent calls this
├─────────────────────────────┤
│  db.py — all SQL lives here │ ← Shared by CLI + Flask
├─────────────────────────────┤
│  SQLite (WAL mode)          │ ← ~/.openclaw/clawctl.db
├─────────────────────────────┤
│  5 tables + indexes:        │
│  tasks          task_deps   │ ← Board + blocking graph
│  messages       agents      │ ← Comms + fleet registry
│  activity                   │ ← Append-only audit log
├─────────────────────────────┤
│  Flask dashboard (optional) │ ← dashboard/server.py
└─────────────────────────────┘
```

**Key design decisions:**

- **All SQL in `db.py`.** The CLI and Flask server import it. No queries in `cli.py` or `server.py`.
- **Race safety.** `claim_task()` and `complete_task()` use atomic single-UPDATE with WHERE guards and rowcount checks. No read-then-write.
- **Normalized blocking.** Dependencies live in the `task_deps` join table with a UNIQUE constraint. Not JSON columns.
- **Parameterized queries.** Every query uses `?` placeholders. No string interpolation.
- **Idempotent completions.** `done` on an already-done task is a safe no-op.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLAW_AGENT` | `$USER` (with warning) | Agent identity for all commands |
| `CLAW_DB` | `~/.openclaw/clawctl.db` | Database file path |

## License

MIT
