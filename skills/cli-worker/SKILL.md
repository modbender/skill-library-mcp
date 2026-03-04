---
name: cli-worker
description: Delegates coding tasks to Kimi CLI agents in isolated git worktrees. Use when the user wants to delegate work to Kimi, run a headless task, or run an isolated coding task in parallel. Requires Kimi CLI installed and authenticated (kimi /login).
---

# CLI Worker Skill (Kimi CLI)

## When to use

- User asks to **delegate** a coding task to Kimi or a CLI worker
- Isolated coding task that should run in its own worktree (no git conflicts)
- Parallel work: run multiple tasks without blocking the main agent
- Headless task: run Kimi CLI non-interactively from OpenClaw

## Delegation: prefer CLI over sessions_spawn

**For a single coding task**, use the CLI so the task actually runs:

- **Do:** `cli-worker execute "Your task prompt"` (and optionally `--constraint` / `--success`). This runs Kimi CLI in a worktree and returns output.
- **Avoid:** Using `sessions_spawn` to delegate to a "sub-agent" for the same kind of task. Spawn is known to sometimes create a session that never processes (0 messages). Use `sessions_spawn` only when you need an ongoing sub-agent conversation with multiple back-and-forth or `sessions_send`.

After any spawn, verify within ~30s: `sessions_list` with `kinds: ["subagent"]` and/or `sessions_history` on the child session; if messages stay 0, treat as failed and retry with `cli-worker execute` instead.

## Prerequisites

> **You must install and authenticate the CLI yourself before using this skill. This skill does not store or use any credentials.**

- **Kimi CLI** installed (`uv tool install kimi-cli` or install script from code.kimi.com)
- **Authenticated**: run `kimi` then `/login` in the REPL (user must complete OAuth; cannot be automated)

Verify with: `cli-worker verify`

## How to invoke

```bash
# Run a single task (creates worktree if in a git repo)
cli-worker execute "Your task prompt"

# With context
cli-worker execute "Create hello.py" --constraint "Python 3.11" --success "Tests pass"

# To get full plain-text output for the agent (not only the final answer)
cli-worker execute "Your task" --output-format text

# Check task status (after Kimi writes report)
cli-worker status <taskId>

# List / remove worktrees
cli-worker worktree list
cli-worker worktree remove <taskId>

# Cleanup old worktrees
cli-worker cleanup --older-than 24
```

## Merge and cleanup

After a task completes, decide whether to keep or discard the work:

- **To keep the work:** From the **main repo** (e.g., on `main`), run:
  ```bash
  git merge openclaw/<taskId>
  cli-worker worktree remove <taskId>
  ```
- **To discard:** Run `cli-worker worktree remove <taskId>` directly, or rely on `cli-worker cleanup --older-than N`.

## Install

- **CLI (required for execute/verify):** Must be on PATH where the agent runs. From the repo: `npm install && npm run build && npm link`. (From npm: `npm install -g @sqncr/openclaw-cli-agent-skill`.) If the agent gets "command not found", run `npm link` from the repo and restart the gateway.
- **Skill discovery:** From the repo run `npm run install-skill` to symlink into `~/.openclaw/skills/cli-worker`. Restart gateway or new session after that.

## OpenClaw integration

- Symlink or copy `skills/cli-worker/` to `~/.openclaw/skills/cli-worker/` so agents can discover it
- Optional config: `~/.openclaw/openclaw.json` with `worktree.basePath` for worktree location
