---
name: clawng-term-memory
description: Make your OpenClaw agent portable and persistent. Version-controls SOUL.md, MEMORY.md, and all core knowledge files using git with automatic GitHub push — so your agent's identity, memory, and operating rules are backed up and can be restored on any machine by cloning the repo. Use whenever core knowledge files are modified to commit and push changes. Also use when asked to show history, diff a file, or revert a change. Watch your assistant evolve over time through its git history.
---

# clawng-term-memory

Make your OpenClaw agent **portable and persistent**. Every change to your agent's soul, memory, and operating rules is committed to git and pushed to a private GitHub repo — so you can restore your exact agent setup on any machine, just by cloning the repo.

Watch your assistant evolve over time through its git history: see when it learned something new, what decisions changed, and who it was a week ago. It's version control for a mind.

## Setup

1. Initialize a git repo in your workspace (if not already done):
```bash
cd ~/.openclaw/workspace
git init
git config user.name "YourAgent"
git config user.email "agent@example.com"
```

2. Create a private GitHub repo, then add it as a remote using SSH (recommended) or HTTPS:

**SSH (recommended — no token exposure):**
```bash
git remote add origin git@github.com:<user>/<repo>.git
```

**HTTPS with credential store (no token in URL):**
```bash
git remote add origin https://github.com/<user>/<repo>.git
git config credential.helper store
# Git will prompt for credentials on first push and store them securely
```

3. Push initial commit:
```bash
git branch -M main && git push -u origin main
```

4. Set workspace path if non-standard (optional):
```bash
export CLAWNG_WORKSPACE=/your/custom/workspace/path
```
The script defaults to `$HOME/.openclaw/workspace` if not set.

## Multi-agent / multi-machine support

Each machine has its own branch (`agent/<hostname>`) with its own `MEMORY.md`. A daily AI synthesis job reads all agents' memories and writes one authoritative `SHARED_MEMORY.md` to `main` — fully automatic, no human required.

```
agent/vps-1 → MEMORY.md ──┐
agent/vps-2 → MEMORY.md ──┤ Claude synthesizes → SHARED_MEMORY.md → main
agent/vps-3 → MEMORY.md ──┘
```

- `commit.sh` — pushes to `agent/<hostname>` automatically (branch created on first commit)
- `merge.sh` — collects all agents' MEMORY.md files for the synthesis agent
- AI synthesis agent — deduplicates and merges into `SHARED_MEMORY.md` on `main` nightly
- All agents read `SHARED_MEMORY.md` from `main` to stay in sync

Scales to 10+ machines with no conflicts.

## Tracked files
- `SOUL.md`, `MEMORY.md`, `USER.md`, `TOOLS.md`, `IDENTITY.md`, `AGENTS.md`, `HEARTBEAT.md`
- `memory/*.md` (daily notes)
- `skills/` (installed skills)

## Commit + push changes

Run after modifying any core file:

```bash
bash /path/to/workspace/skills/clawng-term-memory/scripts/commit.sh "short description of what changed"
```

Examples:
- `"MEMORY.md: added new client context"`
- `"SOUL.md: updated operating rules"`
- `"memory/2026-02-21.md: daily notes"`
- `"HEARTBEAT.md: adjusted check frequency"`

## Daily AI synthesis (run once per day)

`merge.sh` collects all agent `MEMORY.md` files. An AI agent then synthesizes them into `SHARED_MEMORY.md` on `main` — deduplicating, resolving conflicts intelligently, and keeping all unique information.

Set up as an OpenClaw cron job (runs at 02:00 local time by default).

## View history

```bash
cd /path/to/workspace && git log --oneline --graph memory/ MEMORY.md SOUL.md
```

## Diff a file

```bash
cd /path/to/workspace && git diff HEAD~1 MEMORY.md
```

## Revert a file to previous version

```bash
cd /path/to/workspace && git checkout HEAD~1 -- MEMORY.md
bash skills/clawng-term-memory/scripts/commit.sh "revert MEMORY.md to previous version"
```

## Auto-commit rule

**Always run the commit script after modifying a core knowledge file.** Write → commit → push. Every time, no exceptions.
