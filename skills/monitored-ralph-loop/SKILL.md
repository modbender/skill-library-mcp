---
name: ralph-loop
description: Generate copy-paste bash scripts for Ralph Wiggum/AI agent loops (Codex, Claude Code, OpenCode, Goose). Use when asked for a "Ralph loop", "Ralph Wiggum loop", or an AI loop to plan/build code via PROMPT.md + AGENTS.md, SPECS, and IMPLEMENTATION_PLAN.md, including PLANNING vs BUILDING modes, backpressure, sandboxing, and completion conditions.
---

# Ralph Loop (Event-Driven)

Enhanced Ralph pattern with **event-driven notifications** — Codex/Claude calls OpenClaw when it needs attention instead of polling.

## Key Concepts

### Clean Sessions
Each iteration spawns a **fresh agent session** with clean context. This is intentional:
- Avoids context window limits
- Each `codex exec` is a new process with no memory of previous runs
- Memory persists via files: `IMPLEMENTATION_PLAN.md`, `AGENTS.md`, git history

### File-Based Notification Fallback
If OpenClaw is rate-limited when Codex sends a wake notification:
1. The notification is written to `.ralph/pending-notification.txt`
2. Wake is attempted (may fail)
3. When OpenClaw recovers, it checks for pending notifications
4. Work is never lost — it's all in git/files

## File Structure

```
project/
├── PROMPT.md                      # Loaded each iteration (mode-specific)
├── AGENTS.md                      # Project context, test commands, learnings
├── IMPLEMENTATION_PLAN.md         # Task list with status
├── specs/                         # Requirements specs
│   ├── overview.md
│   └── <feature>.md
└── .ralph/
    ├── ralph.log                  # Execution log
    ├── pending-notification.txt   # Current pending notification (if any)
    └── last-notification.txt      # Previous notification (for reference)
```

## Notification Format

`.ralph/pending-notification.txt`:
```json
{
  "timestamp": "2026-02-07T02:30:00+01:00",
  "project": "/home/user/my-project",
  "message": "DONE: All tasks complete.",
  "iteration": 15,
  "max_iterations": 20,
  "cli": "codex",
  "status": "pending"
}
```

Status values:
- `pending` — Wake failed or not attempted
- `delivered` — Wake succeeded

---

## OpenClaw Recovery Procedure

When coming back online after rate limit or downtime, **check for pending notifications**:

```bash
# Find all pending notifications across projects
find ~/projects -name "pending-notification.txt" -path "*/.ralph/*" 2>/dev/null

# Or check a specific project
cat /path/to/project/.ralph/pending-notification.txt
```

### Recovery Actions by Message Prefix

| Prefix | Action |
|--------|--------|
| `DONE:` | Report completion to user, summarize what was built |
| `PLANNING_COMPLETE:` | Inform user, ask if ready for BUILDING mode |
| `PROGRESS:` | Log it, update user if significant |
| `DECISION:` | Present options to user, wait for answer, inject into AGENTS.md |
| `ERROR:` | Check logs (`.ralph/ralph.log`), analyze, help or escalate |
| `BLOCKED:` | Escalate to user immediately with full context |
| `QUESTION:` | Present to user, get clarification, inject into AGENTS.md |

### Injecting Responses

To answer a decision/question for the next iteration:
```bash
echo "## Human Decisions
- [$(date '+%Y-%m-%d %H:%M')] Q: <question>? A: <answer>" >> AGENTS.md
```

The next Codex session will read AGENTS.md and see the answer.

### Clearing Notifications

After processing a notification, clear it:
```bash
mv .ralph/pending-notification.txt .ralph/last-notification.txt
```

---

## Workflow

### 1. Collect Requirements

Ask for (if not provided):
- **Goal/JTBD**: What outcome is needed?
- **CLI**: `codex`, `claude`, `opencode`, `goose`
- **Mode**: `PLANNING`, `BUILDING`, or `BOTH`
- **Tech stack**: Language, framework, database
- **Test command**: How to verify correctness
- **Max iterations**: Default 20

### 2. Generate Specs

Break the goal into **topics of concern** → `specs/*.md`:

```markdown
# specs/overview.md
## Goal
<one-sentence JTBD>

## Tech Stack
- Language: Python 3.11
- Framework: FastAPI
- Database: SQLite
- Frontend: HTMX + Tailwind

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

### 3. Generate AGENTS.md

```markdown
# AGENTS.md

## Project
<brief description>

## Commands
- **Install**: `pip install -e .`
- **Test**: `pytest`
- **Lint**: `ruff check .`
- **Run**: `python -m app`

## Backpressure
Run after each implementation:
1. `ruff check . --fix`
2. `pytest`

## Human Decisions
<!-- Decisions made by humans are recorded here -->

## Learnings
<!-- Agent appends operational notes here -->
```

### 4. Generate PROMPT.md (Mode-Specific)

#### PLANNING Mode

```markdown
# Ralph PLANNING Loop

## Goal
<JTBD>

## Context
- Read: specs/*.md
- Read: Current codebase structure
- Update: IMPLEMENTATION_PLAN.md

## Rules
1. Do NOT implement code
2. Do NOT commit
3. Analyze gaps between specs and current state
4. Create/update IMPLEMENTATION_PLAN.md with prioritized tasks
5. Each task should be small (< 1 hour of work)
6. If requirements are unclear, list questions

## Notifications
When you need input or finish planning:
```bash
openclaw gateway wake --text "PLANNING: <your message>" --mode now
```

Use prefixes:
- `DECISION:` — Need human input on a choice
- `QUESTION:` — Requirements unclear
- `DONE:` — Planning complete

## Completion
When plan is complete and ready for building, add to IMPLEMENTATION_PLAN.md:
```
STATUS: PLANNING_COMPLETE
```
Then notify:
```bash
openclaw gateway wake --text "DONE: Planning complete. X tasks identified." --mode now
```
```

#### BUILDING Mode

```markdown
# Ralph BUILDING Loop

## Goal
<JTBD>

## Context
- Read: specs/*.md, IMPLEMENTATION_PLAN.md, AGENTS.md
- Implement: One task per iteration
- Test: Run backpressure commands from AGENTS.md

## Rules
1. Pick the highest priority incomplete task from IMPLEMENTATION_PLAN.md
2. Investigate relevant code before changing
3. Implement the task
4. Run backpressure commands (lint, test)
5. If tests pass: commit with clear message, mark task done
6. If tests fail: try to fix (max 3 attempts), then notify
7. Update AGENTS.md with any operational learnings
8. Update IMPLEMENTATION_PLAN.md with progress

## Notifications
Call OpenClaw when needed:
```bash
openclaw gateway wake --text "<PREFIX>: <message>" --mode now
```

Prefixes:
- `DECISION:` — Need human input (e.g., "SQLite vs PostgreSQL?")
- `ERROR:` — Tests failing after 3 attempts
- `BLOCKED:` — Missing dependency, credentials, or unclear spec
- `PROGRESS:` — Major milestone complete (optional)
- `DONE:` — All tasks complete

## Completion
When all tasks are done:
1. Add to IMPLEMENTATION_PLAN.md: `STATUS: COMPLETE`
2. Notify:
```bash
openclaw gateway wake --text "DONE: All tasks complete. Summary: <what was built>" --mode now
```
```

### 5. Run the Loop

Use the provided `scripts/ralph.sh`:

```bash
# Default: 20 iterations with Codex
./scripts/ralph.sh 20

# With Claude Code
RALPH_CLI=claude ./scripts/ralph.sh 10

# With tests
RALPH_TEST="pytest" ./scripts/ralph.sh
```

---

## Parallel Execution

For independent tasks, use git worktrees:

```bash
# Create worktrees for parallel work
git worktree add /tmp/task-auth main
git worktree add /tmp/task-upload main

# Spawn parallel sessions (each is clean/fresh)
exec pty:true background:true workdir:/tmp/task-auth command:"codex exec --full-auto 'Implement user authentication...'"
exec pty:true background:true workdir:/tmp/task-upload command:"codex exec --full-auto 'Implement image upload...'"
```

Track sessions:

| Session ID | Worktree | Task | Status |
|------------|----------|------|--------|
| abc123 | /tmp/task-auth | Auth module | running |
| def456 | /tmp/task-upload | Image upload | running |

Each Codex notifies independently. Check `.ralph/pending-notification.txt` in each worktree.

---

## CLI-Specific Notes

### Codex
- Requires git repository
- **Each `codex exec` is a fresh session** — no memory between calls
- `--full-auto`: Auto-approve in workspace (sandboxed)
- `--yolo`: No sandbox, no approvals (dangerous but fast)
- Default model: gpt-5.2-codex

### Claude Code
- `--dangerously-skip-permissions`: Auto-approve (use in sandbox)
- No git requirement
- Each invocation is fresh

### OpenCode
- `opencode run "$(cat PROMPT.md)"`

### Goose
- `goose run "$(cat PROMPT.md)"`

---

## Safety

⚠️ **Auto-approve flags are dangerous.** Always:
1. Run in a dedicated directory/branch
2. Use a sandbox (Docker/VM) for untrusted projects
3. Have `git reset --hard` ready as escape hatch
4. Review commits before pushing

---

## Quick Start

```bash
# 1. Create project directory
mkdir my-project && cd my-project && git init

# 2. Copy templates from skill
cp /path/to/ralph-loop/templates/* .
mv PROMPT-PLANNING.md PROMPT.md

# 3. Create specs
mkdir specs
cat > specs/overview.md << 'EOF'
## Goal
Build a web app that...

## Tech Stack
- Python 3.11 + FastAPI
- SQLite
- HTMX + Tailwind

## Features
1. Feature one
2. Feature two
EOF

# 4. Edit PROMPT.md with your goal

# 5. Run the loop
./ralph.sh 20
```

---

## Example: Antique Catalogue

```markdown
# specs/overview.md
## Goal
Web app for cataloguing antique items with metadata, images, and categories.

## Tech Stack
- Python 3.11 + FastAPI
- SQLite + SQLAlchemy
- HTMX + Tailwind CSS
- Local file storage for images

## Features
1. CRUD for items (name, description, age, purchase info, dimensions)
2. Image upload (multiple per item)
3. Tags and categories
4. Search and filter
5. Multiple view modes (grid, list, detail)
```

The agent will:
1. (PLANNING) Break this into 10-15 tasks
2. (BUILDING) Implement each task, one per iteration
3. Commit after each successful implementation
4. Notify on completion or if blocked
