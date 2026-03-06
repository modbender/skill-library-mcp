---
name: claude-code-cli
version: "0.1.0"
description: "Delegate coding tasks to Claude Code CLI via background process. Use when: building features, reviewing PRs, refactoring codebases, or iterative coding that needs file exploration. Supports interactive PTY mode for confirmations/permissions and headless pipe mode for automation. NOT for: simple one-liner fixes (just edit), reading code (use read tool), or any work in ~/.openclaw/ workspace."
author: "AtelyPham"
license: "MIT"
homepage: "https://github.com/AtelyPham/openclaw-claude-code-skill"
metadata: {"openclaw":{"emoji":"✻","requires":{"bins":["claude"]},"install":[{"id":"node","kind":"node","package":"@anthropic-ai/claude-code","bins":["claude"],"label":"Install Claude Code (npm)"}]}}
---

# Claude Code Skill

Delegate coding tasks to the **Claude Code CLI** via background process with PTY or headless pipe mode.

## PTY Mode Required (Interactive)

Claude Code is an **interactive terminal application** that needs a pseudo-terminal (PTY). Without PTY, output breaks or the agent hangs.

**Always use `pty:true`** for interactive mode:

```bash
# ✅ Correct - with PTY
exec pty:true command:"claude 'Your prompt'"

# ❌ Wrong - no PTY, agent may break
exec command:"claude 'Your prompt'"
```

---

## Two Modes

### 1. Interactive PTY Mode

For tasks where Claude Code may ask confirmations, need input, or show permission prompts.

```bash
# Foreground (waits for completion)
exec pty:true workdir:~/project command:"claude 'Add dark mode toggle'"

# Background (returns sessionId)
exec pty:true workdir:~/project background:true command:"claude 'Build REST API for todos'"
```

### 2. Headless Pipe Mode

For automation, scripting, CI-like usage. Uses `-p` flag for non-interactive.

```bash
# Simple one-shot
exec command:"claude -p 'Explain what src/main.ts does' --output-format json"

# With structured output validation
exec command:"claude -p 'List all exported functions in src/' --output-format json --json-schema '{\"type\":\"object\",\"properties\":{\"functions\":{\"type\":\"array\",\"items\":{\"type\":\"string\"}}}}'"

# Budget-capped automation
exec command:"claude -p 'Refactor auth module' --max-budget-usd 5.00 --output-format json"

# Real-time streaming output (JSON chunks as they arrive)
exec command:"claude -p 'Build a helper function' --output-format stream-json"
```

---

## Exec & Process Tool Reference

### Exec Tool Parameters

| Parameter    | Type    | Description                                                                 |
| ------------ | ------- | --------------------------------------------------------------------------- |
| `command`    | string  | The shell command to run                                                    |
| `pty`        | boolean | **Required for interactive mode!** Allocates a pseudo-terminal              |
| `workdir`    | string  | Working directory (agent sees only this folder's context)                   |
| `background` | boolean | Run in background, returns sessionId for monitoring                         |
| `timeout`    | number  | Timeout in seconds (default: 1800+ for real tasks)                          |
| `elevated`   | boolean | Run on host instead of sandbox (if allowed)                                 |

### Process Tool Actions (for background sessions)

| Action      | Description                                          |
| ----------- | ---------------------------------------------------- |
| `list`      | List all running/recent sessions                     |
| `poll`      | Check if session is still running                    |
| `log`       | Get session output (with optional offset/limit)      |
| `write`     | Send raw data to stdin                               |
| `submit`    | Send data + newline (like typing and pressing Enter) |
| `send-keys` | Send key tokens or hex bytes                         |
| `paste`     | Paste text (with optional bracketed mode)            |
| `kill`      | Terminate the session                                |

---

## Key CLI Flags

| Flag | Purpose |
|------|---------|
| `-p` | Non-interactive pipe mode (headless) |
| `--output-format json` | Structured JSON output (headless only) |
| `--output-format stream-json` | Real-time streaming output (headless only) |
| `--resume [SESSION_ID]` | Resume by ID, or open interactive picker with optional search term |
| `--continue` | Continue the latest session |
| `--fork-session` | Create new session ID when resuming (use with `--resume` or `--continue`) |
| `--from-pr [value]` | Resume session linked to a PR by number/URL |
| `--allowedTools 'Bash,Read,Edit,Write,Glob,Grep'` | Restrict available tools |
| `--permission-mode acceptEdits` | Auto-accept edits, prevents prompt stalls |
| `--permission-mode plan` | Read-only exploration mode (no writes) |
| `--dangerously-skip-permissions` | Full auto, no guardrails (⚠️ DANGER) |
| `--max-budget-usd N` | Spend cap for automation safety |
| `--json-schema '<schema>'` | Structured output validation (with `-p`) |
| `--append-system-prompt '...'` | Add to base prompt (doesn't replace) |
| `--system-prompt '...'` | Replace entire system prompt |
| `--agents '<json>'` | Inline dynamic subagent definitions |
| `--model <model>` | Override model (sonnet, haiku, opus) |
| `--add-dir <path>` | Add extra directory to context |

### Permission Modes

| Mode | Behavior |
|------|----------|
| `default` | Ask per operation |
| `acceptEdits` | Auto-accept file edits (recommended for background tasks) |
| `plan` | Read-only exploration, no writes |
| `dontAsk` | Auto-deny unless pre-approved |
| `bypassPermissions` | Skip all permission prompts (⚠️ same effect as `--dangerously-skip-permissions`) |

### System Prompt Modes

| Flag | Behavior |
|------|----------|
| `--append-system-prompt '...'` | Adds to the default system prompt — Claude Code keeps its built-in instructions |
| `--system-prompt '...'` | Replaces the entire system prompt — Claude Code loses all default behavior |

Use `--append-system-prompt` to add context or constraints. Use `--system-prompt` only when you need full control over the prompt (rare).

### Granular Tool Restrictions

Restrict Claude Code's Bash tool to specific subcommands:

```bash
exec pty:true command:"claude --allowedTools 'Bash(git:*,npm:*),Read,Edit,Write,Glob,Grep' 'Your task'"
```

---

## Session Continuity

Track and resume sessions across conversations.

```bash
# Start a task
exec pty:true workdir:~/project background:true command:"claude --permission-mode acceptEdits 'Build feature X'"

# Continue latest session
exec pty:true workdir:~/project command:"claude --continue"

# Resume specific session by ID
exec pty:true workdir:~/project command:"claude --resume abc123"

# Resume with interactive search (finds sessions matching the term)
exec pty:true workdir:~/project command:"claude --resume 'auth module'"

# Fork when resuming (creates new session ID, preserves original)
exec pty:true workdir:~/project command:"claude --continue --fork-session"

# Resume session linked to a PR
exec pty:true workdir:~/project command:"claude --from-pr 130"

# List recent sessions (find session IDs)
exec command:"claude sessions list"
```

### HANDOFF.md Pattern (Long Sessions)

For tasks that exceed context limits, write progress to a handoff file:

```bash
# In the Claude Code session, ask it to write progress
# Then start a fresh session picking up from the handoff
exec pty:true workdir:~/project command:"claude 'Read HANDOFF.md and continue the work described there'"
```

---

## Patterns

### Quick Start: One-Shot Task

```bash
# Foreground with PTY
exec pty:true workdir:~/project command:"claude --permission-mode acceptEdits 'Add error handling to API calls'"

# Headless one-shot
exec command:"claude -p 'Summarize the codebase structure' --output-format json"
```

### Background Task with Monitoring

```bash
# 1. Start
exec pty:true workdir:~/project background:true timeout:3600 command:"claude --permission-mode acceptEdits 'Build a complete auth module with JWT tokens'"

# 2. Monitor
process action:log sessionId:XXX
process action:poll sessionId:XXX

# 3. Send input if needed
process action:submit sessionId:XXX data:"yes"

# 4. Kill if stuck
process action:kill sessionId:XXX
```

### PR Review (Safe — Never in Live Workspace)

**⚠️ CRITICAL: Never review PRs in OpenClaw's own project folder!**

```bash
# Clone to temp dir and checkout PR
exec command:"git clone https://github.com/user/repo.git /tmp/pr-review && cd /tmp/pr-review && gh pr checkout 130"

exec pty:true workdir:/tmp/pr-review command:"claude --permission-mode plan 'Review this PR. Focus on bugs, security issues, and performance. Show diff summary.'"

# Clean up
exec command:"rm -rf /tmp/pr-review"
```

### Parallel Issue Fixing with Git Worktrees

```bash
# 1. Create worktrees
exec command:"git worktree add -b fix/issue-78 /tmp/issue-78 main"
exec command:"git worktree add -b fix/issue-99 /tmp/issue-99 main"

# 2. Launch Claude Code in each (background + PTY)
exec pty:true workdir:/tmp/issue-78 background:true command:"claude --permission-mode acceptEdits 'Fix issue #78: <description>. Commit when done.

When finished, run: openclaw system event --text \"Done: Fixed issue #78\" --mode now'"

exec pty:true workdir:/tmp/issue-99 background:true command:"claude --permission-mode acceptEdits 'Fix issue #99: <description>. Commit when done.

When finished, run: openclaw system event --text \"Done: Fixed issue #99\" --mode now'"

# 3. Monitor
process action:list

# 4. Create PRs
exec command:"cd /tmp/issue-78 && git push -u origin fix/issue-78"
exec command:"gh pr create --repo user/repo --head fix/issue-78 --title 'fix: ...' --body '...'"

# 5. Cleanup
exec command:"git worktree remove /tmp/issue-78"
exec command:"git worktree remove /tmp/issue-99"
```

### Fan-Out Pattern (Bulk Operations)

Distribute work across parallel headless invocations:

```bash
# Migrate multiple files in parallel (shell script via exec)
exec command:"for file in \$(cat files-to-migrate.txt); do claude -p \"Migrate \$file to new API\" --output-format json --max-budget-usd 1.00 & done; wait"
```

### Writer/Reviewer Pattern (Dual Sessions)

Two parallel sessions — one implements, one reviews:

```bash
# Session A: implement
exec pty:true workdir:~/project background:true command:"claude --permission-mode acceptEdits 'Implement the feature described in SPEC.md'"

# Session B: review (read-only)
exec pty:true workdir:~/project background:true command:"claude --permission-mode plan 'Watch for new changes and review them. Focus on correctness and test coverage.'"
```

### Inline Dynamic Subagents

Define agents without any files on disk:

```bash
exec pty:true command:"claude --agents '{
  \"code-reviewer\": {
    \"description\": \"Expert code reviewer\",
    \"prompt\": \"You are a senior code reviewer. Focus on correctness, security, and performance.\",
    \"tools\": [\"Read\", \"Grep\", \"Glob\", \"Bash\"],
    \"model\": \"sonnet\"
  },
  \"implementer\": {
    \"description\": \"Feature implementer\",
    \"prompt\": \"You implement features following existing patterns.\",
    \"tools\": [\"Read\", \"Edit\", \"Write\", \"Bash\", \"Glob\", \"Grep\"],
    \"model\": \"sonnet\"
  }
}'"
```

---

## Auto-Notify on Completion

For long-running background tasks, append a wake trigger so OpenClaw gets notified immediately:

```bash
exec pty:true workdir:~/project background:true command:"claude --permission-mode acceptEdits 'Build a REST API for todos.

When completely finished, run this command to notify me:
openclaw system event --text \"Done: Built todos REST API with CRUD endpoints\" --mode now'"
```

---

## Progress Updates

When spawning background agents, keep the user informed:

- Send 1 short message on start (what's running + where)
- Update only on changes: milestone complete, agent needs input, error, or finish
- If killing a session, say why immediately
- Never let the user see "Agent failed" with zero context

---

## Safety Rules

1. **Always use `pty:true`** for interactive mode
2. **Use `--permission-mode acceptEdits`** for background tasks to prevent prompt stalls
3. **Never run in `~/.openclaw/`** workspace
4. **Never checkout branches** in live OpenClaw project dir
5. **`--dangerously-skip-permissions`** gets explicit danger warning — prefer `acceptEdits`
6. **Respect user's tool choice** — don't silently take over if agent fails
7. **Be patient** — don't kill sessions because they're "slow"
8. **Budget cap automation** — use `--max-budget-usd` for unattended headless runs
9. **Max 3-4 active sessions** — more causes resource contention
10. **Timeout guidance** — use 1800s+ for real tasks, don't let timeouts kill mid-work
