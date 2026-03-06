---
name: claude-code-pro
description: >
  Token-efficient Claude Code workflow. Other skills burn tokens polling tmux every 30s — 
  this one uses completion callbacks and only checks when notified. Observable tmux sessions,
  smart dispatch rules (know when NOT to spawn Claude Code), and structured JSON monitoring.
  Saves 80%+ supervision tokens vs polling-based approaches.
  Use when: multi-file coding tasks that need background execution.
  NOT for: simple single-file fixes (just read+edit directly — that's the point).
  Requires: tmux, claude CLI.
metadata:
  {
    "openclaw":
      {
        "emoji": "⚡",
        "os": ["darwin", "linux"],
        "requires": { "bins": ["tmux", "bash"], "anyBins": ["claude"] },
      },
  }
---

# Claude Code Pro ⚡

Production-grade Claude Code workflow that doesn't waste your tokens.

## The Problem with Other Skills

Most Claude Code tmux skills work like this:
```
Start task → Poll every 30s → Poll → Poll → Poll → Done
                 🔥 tokens      🔥       🔥       🔥
```

Each poll reads 100-200 lines of terminal output, feeds it to your agent, and burns tokens deciding "is it done yet?" A 20-minute task = 40 polls = thousands of wasted tokens.

## How This Skill Works

```
Start task (with callback) → Wait → 📩 Notification → Read result (50 lines)
                               😴 zero tokens          ⚡ one read
```

**The task itself tells you when it's done.** Your agent sleeps until notified. One lightweight check confirms the result. That's it.

### Token Savings Breakdown

| Approach | 20-min task | Tokens burned |
|----------|-------------|---------------|
| Poll every 30s | 40 reads × ~500 tokens | **~20,000** |
| Poll every 60s | 20 reads × ~500 tokens | **~10,000** |
| **This skill** | 1 notification + 1 read | **~500** |

**80-97% token savings** on supervision alone.

## Smart Dispatch: Know When NOT to Start

Before spawning Claude Code, ask:

| Situation | Action |
|-----------|--------|
| < 3 files involved | **Don't start CC.** Just read + edit directly. |
| Single bug fix | **Don't start CC.** Faster to fix inline. |
| Need extensive context exploration | ✅ Start CC |
| Multi-file refactor | ✅ Start CC |
| New feature (5+ files) | ✅ Start CC |

The fastest token savings come from not spawning a session at all.

## Quick Start

```bash
# Start a task — note the callback at the end
bash {baseDir}/scripts/start.sh --label auth-refactor --workdir ~/project --task "Refactor auth module to use JWT.

When completely finished, run: openclaw system event --text \"Done: JWT auth refactor complete\" --mode now"
```

That's the key line: `openclaw system event --text "Done: ..." --mode now`. The task notifies your agent on completion. No polling needed.

### Task from file (complex requirements)

```bash
bash {baseDir}/scripts/start.sh --label my-feature --workdir ~/project \
  --task-file /path/to/requirements.md --mode auto
```

Write detailed requirements once upfront → fewer mid-task corrections → fewer tokens.

## Monitor (Only When Needed)

```bash
# Lightweight check — 50 lines, minimal tokens
bash {baseDir}/scripts/monitor.sh --session my-task --lines 50

# JSON mode — structured, even fewer tokens for agent parsing
bash {baseDir}/scripts/monitor.sh --session my-task --json

# Send follow-up (use sparingly — write requirements upfront instead)
bash {baseDir}/scripts/send.sh --session my-task --text "Also add unit tests"

# Compact context when running long
bash {baseDir}/scripts/send.sh --session my-task --compact
```

## Manage Sessions

```bash
# List all active sessions
bash {baseDir}/scripts/list.sh          # human-readable
bash {baseDir}/scripts/list.sh --json   # structured

# Stop sessions
bash {baseDir}/scripts/stop.sh --session my-task
bash {baseDir}/scripts/stop.sh --all
```

## Attach (Human SSH Access)

```bash
tmux -L cc attach -t cc-<label>
```

## Agent Workflow

```
1. DECIDE — Is this a 3+ file task? No → just edit. Yes → continue.
2. START — start.sh with detailed task + completion callback
3. WAIT — Do other work. Zero tokens spent watching.
4. NOTIFIED — Receive "Done: ..." event
5. CHECK — monitor.sh --lines 50 to confirm result
6. CLEANUP — stop.sh to end session
```

**Fallback:** If no notification after 15 minutes, one lightweight poll with `--json`.

## Completion Callback Template

Always append to your task prompt:

```
When completely finished, run this command to notify:
openclaw system event --text "Done: [brief description]" --mode now
```

This is what makes the whole approach work. The task signals completion; your agent doesn't need to guess.

## Modes

| Mode | Flag | Behavior |
|------|------|----------|
| auto | `--mode auto` | Full permissions, runs freely (default) |

## Design Choices

- **Isolated tmux socket** (`-L cc`) — doesn't interfere with your tmux sessions
- **`cc-` prefix** on all sessions — easy to list/filter
- **Bracketed paste** for multi-line prompts — no escaping issues
- **JSON output** from list/monitor — agent-friendly, fewer tokens to parse

## Files

| Script | Purpose |
|--------|---------|
| `scripts/start.sh` | Launch CC in tmux with task |
| `scripts/monitor.sh` | Lightweight output capture |
| `scripts/send.sh` | Send prompts / compact / approve |
| `scripts/list.sh` | List active sessions |
| `scripts/stop.sh` | Kill sessions |
