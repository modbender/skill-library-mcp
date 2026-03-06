# @netcetera/morning

Daily journaling, reflection, and planning skill for OpenClaw.

## What it does

- Reviews yesterday — what was planned, what happened, what was avoided
- Pulls today's tasks and projects from Brain MCP
- Checks inbox for items to promote to today
- Aligns daily to-dos against annual goals
- Writes and maintains a daily journal file
- Logs entries throughout the day on demand
- Supports evening review and weekly review

## Install

```bash
openclaw skills install @netcetera/morning
```

## Trigger

Say `morning` to start your day.

## File structure expected

```
journal/
  YYYY/
    goals.md          # Annual goals
    MM/
      YYYY-MM-DD.md   # Daily journal entries
inbox.md              # Quick capture
```

## Brain MCP

This skill uses `mcp__claude_ai_Actions_Team__listActions` and `mcp__claude_ai_Actions_Team__listProjects` to pull tasks and projects from Brain at the start of each session.

Requires Brain MCP to be configured in your OpenClaw setup.
