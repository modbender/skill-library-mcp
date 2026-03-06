---
name: claude-tmux-runner
description: "Claude Code parallel task manager with tmux backend. For running
  multiple Claude Code tasks concurrently, monitoring progress, and managing
  background jobs. Activate when user mentions: Claude Code, background task,
  parallel, tmux."
---


# Claude Code tmux Runner

## Overview

Run multiple Claude Code tasks in parallel using tmux sessions. Non-blocking, background execution with status monitoring.

## Usage

### Start a Task

```bash
~/.openclaw/scripts/claude-tmux.sh start "Your task description" [task-name]
```

Examples:
```bash
~/.openclaw/scripts/claude-tmux.sh start "Write a Python auth module" auth
~/.openclaw/scripts/claude-tmux.sh start "Build a React component" ui
~/.openclaw/scripts/claude-tmux.sh start "Create a Go microservice" api
```

### List All Tasks

```bash
~/.openclaw/scripts/claude-tmux.sh list
```

### Check Task Status

```bash
~/.openclaw/scripts/claude-tmux.sh status <task-id>
```

### View Generated Files

```bash
~/.openclaw/scripts/claude-tmux.sh files
```

### Stop Tasks

```bash
~/.openclaw/scripts/claude-tmux.sh stop <task-id>
~/.openclaw/scripts/claude-tmux.sh stop-all
```

## Workflow

1. User says "use Claude Code xxx" → Optimize prompt → Show for approval
2. User confirms → Start background task → Return immediately
3. User can continue chatting → Non-blocking
4. User asks "how is Claude doing" → Check status → Return progress

## Industrial Code Standards

Generated code must include:

1. Complete error handling (try-catch, boundary checks)
2. Type annotations (TypeScript, Python type hints)
3. Documentation (JSDoc, docstring)
4. Unit tests (pytest, jest)
5. Performance considerations (time/space complexity)
6. Security best practices (input validation)
7. Maintainability (clear naming, modular)

## File Locations

- Script: `~/.openclaw/scripts/claude-tmux.sh`
- Logs: `~/.openclaw/logs/claude/`
- Files: `~/.openclaw/workspace/`
- State: `~/.openclaw/state/claude/`
