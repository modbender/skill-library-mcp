---
name: task-resume
description: Automatic interrupted-task resume workflow with queueing and recovery. Use when a user asks to resume interrupted work after temporary context switches, protect priority tasks from drift, or enforce "finish current task then auto-resume previous interrupted task" behavior.
---

# Task Resume

Use this skill to ensure interrupted tasks are recovered automatically.

## Defaults (MANDATORY)

- Make interruption enqueue the default behavior.
- On any non-explicit context switch, auto-enqueue the active unfinished task.
- Enqueue at message-time (immediately when interruption is detected), not only on periodic checks.
- Use one shared queue file for all sessions/clones so the view is unified.

## Rules

- Treat user-explicit commands (`cancel`, `pause`, `change priority`, `do it tomorrow`) as overrides.
- Treat all other topic switches as potential interruptions.
- Before switching topics, persist interruption context to queue.
- After completing the active task, immediately resume the oldest queued interrupted task.
- If queue is empty, do nothing.

## Shared Queue Storage (cross-session)

- Canonical queue file: `memory/task-resume-queue.json`
- This file is workspace-global and shared across main + clone + group sessions.
- Always pass source with session/channel identity.
- Use helper script: `scripts/task_resume_queue.py`

## Interruption Detection

Consider a task interrupted when all are true:
1. There is an active task with unfinished acceptance criteria.
2. A new user request is unrelated to finishing that active task.
3. User did not explicitly cancel/pause/defer the active task.

## Message-Time Enforcement (required)

Before handling every new user message:
1. Check whether an active task exists and is unfinished.
2. If the incoming message is an unrelated request and no explicit override is present, enqueue immediately.
3. Only then switch to the new request.

This prevents queue misses caused by timing gaps.

## Log-based Recovery (ENOENT-safe)

When recovery needs session `.jsonl` context, use:

```bash
python3 skills/task-resume/scripts/task_resume_queue.py recover \
  --log "~/.openclaw/agents/main/sessions/<session>.jsonl" \
  --title "<active task title>" \
  --acceptance "<acceptance criteria>" \
  --source "<channel>" \
  --session "<session_key_or_chat_id>"
```

If the log file is missing (`ENOENT`), treat it as expected and continue (`skipped_missing_log`), do not raise alert-level failure.

## On Interruption (auto-enqueue)

Run immediately at interruption detection:

```bash
python3 skills/task-resume/scripts/task_resume_queue.py add \
  --title "<active task title>" \
  --context "<what was done + exact next step>" \
  --acceptance "<acceptance criteria>" \
  --source "<channel>" \
  --session "<session_key_or_chat_id>"
```

Then acknowledge briefly: queued + will auto-resume.

## On Active Task Completion (resume)

Run:

```bash
python3 skills/task-resume/scripts/task_resume_queue.py pop
```

- If one item is returned, resume it immediately and announce: `Resuming previously interrupted task: <title>`.
- If empty, continue normal flow.

## Unified View

Run:

```bash
python3 skills/task-resume/scripts/task_resume_queue.py status
```

This returns total queue count + grouped counts by source/session.

## Guardrails

- Never drop queued tasks silently.
- Always include next-step quality context when enqueueing.
- Deduplicate: if same task title and near-identical context exists in queue, update timestamp instead of appending.
- Keep queue max size 30; discard oldest overflow items after logging to `memory/YYYY-MM-DD.md`.

## Watchdog Auto-Continue (Heartbeat/Cron)

When users require "not just reminder, but auto-continue execution", add a watchdog cron policy:

- Run every 30 minutes.
- First inspect unfinished primary task + queue status.
- If interrupted or no recent progress, immediately continue the next actionable step.
- Send concise progress each run: done / in-progress / next step + ETA.
- Even with no material change, send a short巡检回执（"已巡检，继续执行中"）.

Recommended cron shape for delivery reliability:

- Prefer `sessionTarget="main"` + `payload.kind="systemEvent"` for user-facing continuity checks.
- Avoid fragile announce-only chains when delivery channel config is unstable.

## Daily Hygiene

At least once daily:

```bash
python3 skills/task-resume/scripts/task_resume_queue.py list
```

If stale items (>7 days), ask user whether to cancel or schedule.
