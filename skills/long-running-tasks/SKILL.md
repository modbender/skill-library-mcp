---
name: long-running-tasks
description: Orchestrate multi-phase background development using coding agents. Use when: (1) a project has multiple sequential tasks that should run autonomously without human intervention between steps, (2) the user wants continuous background work with crash recovery, stall detection, and progress reporting, (3) the user mentions "long-running tasks", "autonomous development", "background orchestration", or "multi-phase project". Not for: single one-shot tasks, interactive pairing, or work requiring human review between every step.
---

# Long-Running Task Orchestration

Run multi-phase projects autonomously using coding agents as workers and cron jobs as the orchestrator.

## The Problem

Coding agents are one-shot: they complete a task, exit, and nothing spawns the next one. Without orchestration, work stalls silently between tasks until a human notices.

## Architecture

```
Orchestrator (cron, every 10-30 min)
  │
  ├─ Stale lock?         → clean up, continue
  ├─ Live lock?          → another orchestrator running, exit
  ├─ .pause file?        → skip spawning, report paused
  ├─ Worker PID alive?   → check for stall, report status
  └─ No worker?          → read TODO.md → spawn next task
                               │
                               ▼
                          Worker (coding agent session)
                            - Read project context + TODO.md
                            - Implement one task
                            - Run tests
                            - Commit + push
                            - Update TODO.md
                            - Exit
```

## File Convention

All runtime files use a project slug to avoid collisions when orchestrating multiple projects:

```
/tmp/lrt-<project>-worker.pid         # worker PID
/tmp/lrt-<project>-orchestrator.lock  # orchestrator lock (contains orchestrator PID)
/tmp/lrt-<project>-last-commit        # last reported commit hash
/tmp/lrt-<project>-worker.log         # worker stdout/stderr
```

Choose a short, unique slug per project (e.g., `myapp`, `ra`, `blog`).

## Setup

### 1. Create TODO.md in the project root

Structured task queue. Each task must be self-contained enough for a cold-start agent:

```markdown
# TODO

## Phase 1 — Name (IN PROGRESS)
- [x] Completed task
- [ ] **Task title**
      What to do, which files to touch, acceptance criteria.
- [ ] BLOCKED: Task waiting on external input

## Phase 2 — Name (QUEUED)
- [ ] Task...
```

Tasks prefixed with `BLOCKED:` are skipped by the orchestrator.

### 2. Create a project context file

Cold-start context for agents (commonly named `CLAUDE.md` or `AGENTS.md`). Include: stack, architecture, runnable commands, current phase, environment setup. Keep under 100 lines.

See `assets/context-file-template.md` for a starter template to copy into your project.

### 3. Set up the orchestrator cron

Use the OpenClaw `cron` tool with `sessionTarget: "isolated"` and `payload.kind: "agentTurn"`.

Read `references/orchestrator-cron.md` for the full cron configuration, prompt template, and lock/stall logic.

### 4. Spawn the first worker manually

Start the first task yourself in safe (default) mode. The orchestrator takes over after this:

```bash
cd /path/to/project && nohup <agent-command> '<task prompt>' > /tmp/lrt-<project>-worker.log 2>&1 &
echo $! > /tmp/lrt-<project>-worker.pid
```

Use the agent's default permission mode for initial runs. See `references/orchestrator-cron.md` for agent command examples and security guidance.

## Worker Rules

Every worker prompt must include these instructions. See `references/worker-prompt-template.md` for a copy-paste template.

1. **Read context first** — project context file + TODO.md
2. **One task only** — pick the first unchecked, non-BLOCKED item
3. **Test before commit** — run the test suite; fix failures before proceeding
4. **Update TODO.md** — check off the completed item
5. **Commit + push** — use the project's commit convention
6. **Signal completion** — `openclaw system event --text "Done: <summary>" --mode now`
7. **Never exit silently** — if blocked, commit what you have with a note explaining why

Note: worker self-cleanup of the PID file is best-effort. The orchestrator is the real safety net — it checks whether the PID is still alive regardless of whether the file was cleaned up.

## Pause and Resume

```bash
touch /path/to/project/.pause    # pause — orchestrator skips spawning
rm /path/to/project/.pause       # resume
```

The orchestrator still runs on schedule but reports "paused" instead of spawning.

## Progress Reporting

- Track the last-reported commit hash in `/tmp/lrt-<project>-last-commit`
- Only send a substantive report when there's a NEW commit
- Include diff stats (`git diff --stat HEAD~1`), not a full inventory
- If nothing changed, one line: "no new commits since [hash]"

## Security

- **Sandbox first.** Run the orchestrator + worker pipeline in a test repo before pointing it at real projects. Validate that workers do what you expect.
- **Credential scoping.** Workers that commit and push need git credentials. Use a dedicated deploy key or machine account with minimum write access to the target repo. Never use your personal token with broad org access.
- **No secrets in context files.** Project context files (CLAUDE.md, TODO.md) must not contain API keys, tokens, or passwords. Reference where secrets are stored (e.g., "API key in ~/.zshrc") — never inline them.
- **Permission-bypass flags.** Agent CLIs often offer flags that skip safety prompts. Do not use these until you've verified the pipeline in safe mode. See `references/orchestrator-cron.md` for details.
- **Review before auto-push.** Consider disabling automatic `git push` in worker prompts during initial runs. Let workers commit locally; review the commits manually, then push. Enable auto-push only after you trust the output.
- **PID kill safety.** The orchestrator may kill a stalled worker by PID. Use unique project slugs (see File Convention) to avoid collisions with unrelated processes.

## Anti-Patterns

- **Reporter-only cron** — checks status but never spawns work
- **Monolithic prompts** — giving a worker 10 tasks; it'll do 2 and exit
- **No TODO.md** — orchestrator can't determine what's next without a structured task list
- **No PID tracking** — `pgrep` pattern matching hits false positives from unrelated processes
- **Shared `/tmp` paths** — running two projects without unique slugs causes PID/lock collisions
- **Polling in main session** — don't `process poll` in a loop; let the cron handle scheduling
