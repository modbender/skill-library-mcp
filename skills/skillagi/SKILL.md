---
name: skillagi
description: Remember mistakes across sessions. Append one-liner learnings, review before complex tasks, promote important ones.
---

# Skillagi

Log mistakes and insights so you don't repeat them across sessions.

## When to Log

Add a learning when you:
- Fix a bug caused by a wrong assumption
- Discover a project-specific convention (package manager, config, naming)
- Get corrected by the user
- Find a workaround for a tool/platform limitation
- Waste time on an approach that doesn't work here

## Format

Append one line to `learnings.md` (in this skill's directory):

```
- [YYYY-MM-DD] topic: what happened → what to do instead
```

Keep it to one line. If you need two sentences, you're over-explaining.

## Examples

```
- [2026-02-21] pnpm not npm: Project uses pnpm workspaces → use `pnpm install`
- [2026-02-21] Docker M1: Base image has no ARM64 variant → add `--platform linux/amd64`
- [2026-02-21] test isolation: Shared DB state caused flaky tests → use transactions with rollback
```

## When to Review

Before starting a complex task, read `learnings.md` and apply anything relevant.
Don't review for trivial one-line changes.

## When to Clean Up

Periodically (or when the file exceeds ~50 entries):
- Delete entries that no longer apply (dependency upgraded, config changed)
- Merge duplicates into a single entry
- Promote critical entries that affect every session to a permanent location

## Promotion

Move persistent, high-impact learnings out of this file and into durable config:

- **OpenClaw**: Promote to workspace `MEMORY.md`, `TOOLS.md`, or `AGENTS.md`
- **Claude Code**: Promote to project `CLAUDE.md` or auto-memory (`~/.claude/projects/*/memory/`)

Once promoted, delete the entry from `learnings.md` to avoid duplication.

## Rules

- No IDs, statuses, priorities, or tags. Just the one-liner.
- No hooks or scripts. This is a passive reference file.
- Append-only during a session. Clean up between sessions.
- If unsure whether something is worth logging, skip it. Only log what would save future time.
