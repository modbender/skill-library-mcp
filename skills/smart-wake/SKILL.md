---
name: smart-wake
version: 1.0.0
owner: platform-team
description: Prevent subagent timeout using checkpoint + cron wake + resume via session spawn mechanism.
---

# SKILL: smart-wake

## Objective
Ensure long-running tasks do not lose progress when subagent timeout occurs.

Standard mechanism:
1. **Auto-save state** before timeout / reaching timeout threshold.
2. **Cron wake** to re-invoke agent at scheduled time.
3. **Resume task** from latest checkpoint using `sessions_spawn` (or `session_spawn` depending on runtime) with appropriate `wakeMode`.

---

## Activation Triggers
Use `smart-wake` when any of the following conditions are met:
- Task duration exceeds default subagent timeout.
- Requires periodic polling (by minute/hour) to continue processing.
- Multi-step workflow that may pause mid-execution but must resume accurately.
- Running overnight / off-hours but still needs to auto-continue.

---

## Available Tools (Built-in)
- `sessions_spawn` / `session_spawn` (spawn new work session)
- Gateway cron jobs (schedule wake events)
- Memory/slot for state persistence (state checkpoint)

> Do not create new tools. Only use existing mechanisms.

---

## State Contract (MANDATORY)
Each task must implement checkpointing with minimum schema:

```json
{
  "task_id": "smartwake_<slug>_<timestamp>",
  "goal": "Final objective",
  "status": "running|waiting|blocked|done|failed",
  "current_step": "step_name",
  "progress_pct": 0,
  "last_completed": ["step_a", "step_b"],
  "next_actions": ["action_1", "action_2"],
  "artifacts": ["path/file1", "path/file2"],
  "errors": [],
  "retry_count": 0,
  "updated_at": "ISO_TIMESTAMP"
}
```

Requirements:
- Update checkpoint after each completed step.
- Final checkpoint before timeout.
- Resume always reads latest checkpoint; never re-run blindly.

---

## Standard Workflow

### Step 1 — Preflight (Estimate Timeout)
- Determine subagent timeout and total task duration.
- If `estimated_duration > 70% timeout`: enable `smart-wake` immediately.
- Create `task_id` and initial checkpoint.

### Step 2 — Execute by Small Chunks
- Divide task into 5–15 minute chunks.
- After each chunk:
  - Write progress to checkpoint,
  - Record artifact/path,
  - Update `next_actions`.

### Step 3 — Pre-timeout Auto-save
- When ~10–20% timeout remains:
  - Flush final checkpoint,
  - Set `status = waiting`,
  - Prepare resume payload (task_id + next_actions).

### Step 4 — Schedule Cron Wake
- Register Gateway cron job to wake after appropriate interval (e.g., 2–10 minutes depending on load).
- Cron payload MUST contain:
  - `task_id`
  - `resume_from=latest_checkpoint`
  - `reason=timeout_recovery`

### Step 5 — Spawn Resume Session
- At wake time, call `sessions_spawn` (or `session_spawn`) with `wakeMode` enabling auto-resume via cron.
- Pass concise context:
  - objective,
  - latest checkpoint,
  - next step,
  - completion criteria.

### Step 6 — Resume + Idempotency Guard
- New session must:
  1. Read checkpoint,
  2. Verify artifacts exist,
  3. Skip completed steps,
  4. Continue exact `next_actions`.
- When entire task completes: set `status = done`, cancel remaining cron wakes.

---

## Sample Resume Packet (Reference)

```json
{
  "task": "Resume long-running task",
  "task_id": "smartwake_repo_scan_20260301T120000Z",
  "wakeMode": "cron",
  "resume": {
    "from": "latest_checkpoint",
    "current_step": "collect_phase_2",
    "next_actions": ["fetch page 6-10", "dedupe", "export report"]
  },
  "done_criteria": [
    "output file generated",
    "validation passed",
    "status marked done"
  ]
}
```

> Note: Field names may vary by Gateway/OpenClaw version, but checkpoint + wakeMode + resume context principles are mandatory.

---

## Operational Rules
1. **Never resume without valid checkpoint.**
2. **Never overwrite artifacts without checksum/timestamp verification.**
3. **No infinite wake loops**: limit `retry_count` (e.g., max 5).
4. **Every wake must have clear reason** (`timeout_recovery`, `dependency_ready`, `scheduled_progress`).
5. **Clean up on done**: completed task must clear related cron jobs.

---

## Output Format After Each Wake Cycle

```json
{
  "task_id": "smartwake_<...>",
  "status": "running|waiting|done|failed",
  "progress_pct": 65,
  "current_step": "...",
  "resumed_from_checkpoint": true,
  "next_wake_scheduled": true,
  "next_wake_at": "ISO_TIMESTAMP|null",
  "notes": "concise, auditable"
}
```

---

## Anti-patterns (FORBIDDEN)
- Running long tasks without periodic checkpointing.
- Waking without passing `task_id`/resume context.
- Re-running entire pipeline from start when only 1 step is missing.
- Not canceling cron after `done`.

---

## Expected Outcomes
- No state loss on subagent timeout.
- Long tasks progress steadily via cron wake.
- Full system auditability: checkpoint → wake → resume → done.
