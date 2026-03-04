# Doppleganger

**OpenClaw skill: prevent duplicate subagent sessions.**

One task, one agent. Doppleganger ensures the same task isn’t run by multiple subagents at once—saving tokens and cutting lag. No more “multiple Spidermen pointing at each other.”

## What it does

- **Check** — Before you call `sessions_spawn`, run Doppleganger with the task string. If that task is already running, don’t spawn again.
- **Guard** — Same as check; use when you want a clear “guard before spawn” step in scripts or docs.
- Integrates with the orchestrator rule: the main agent runs a duplicate check (Doppleganger or subagent-tracker `check-duplicate`) before every spawn.

## Install

Copy or link this folder into your OpenClaw workspace skills directory:

```bash
# Example
ln -s /path/to/doppleganger ~/.openclaw/workspace/skills/doppleganger
```

Requires the **subagent-tracker** skill (same workspace) for `runs.json` and `sessions.json`.

## Quick start

```bash
# Check (human-readable)
python3 /Users/ghost/.openclaw/workspace/skills/doppleganger/scripts/doppleganger.py check "run funclip recognize_video https://youtube.com/foo /tmp/out"

# Check (JSON for orchestrator)
python3 /Users/ghost/.openclaw/workspace/skills/doppleganger/scripts/doppleganger.py check "your task here" --json

# Guard alias
python3 /Users/ghost/.openclaw/workspace/skills/doppleganger/scripts/doppleganger.py guard --task "your task" --json
```

## Exit codes

- `0` — No duplicate; safe to spawn (or check succeeded).
- `1` — Error (e.g. tracker not found).
- `2` — Duplicate detected; do not spawn.

## See also

- **subagent-tracker** — `check-duplicate` is the underlying implementation; Doppleganger is the named skill that calls it.
- Orchestrator rule: “Before calling sessions_spawn, run check-duplicate / Doppleganger with the task from the router.”
