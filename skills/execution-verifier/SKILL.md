---
name: execution-verifier
description: Enforce real progress for long-running tasks by separating execution from reporting. Use when users complain that the agent is "saying it's working" without concrete output, when a task is stalling, or when you need a hard proof loop (file changes, commit checks, and blocker alerts) every 15-30 minutes.
---

# Execution Verifier

Use this skill to prevent fake progress.

## Core policy

- Treat "no artifact change" as "no progress".
- Report only hard evidence: file changes, line deltas, commits, test outputs.
- If no evidence is detected in the time window, report blocker + immediate next action.

## Minimal operating loop (30 min)

1. **Execute** one concrete next action from OPEN_TASKS.
2. **Write artifacts** (target files must change).
3. **Verify** with `scripts/verify_progress.py`.
4. **Report** in strict 3-line format.

## Strict report format

1) 已完成：`<file path + concrete change>`
2) 进行中：`<current actionable step>`
3) 下一步+ETA：`<next step + time>`

If verification fails, replace line 1 with: `本轮无新增（原因：<blocker>）`.

## Verifier command

```bash
python3 skills/execution-verifier/scripts/verify_progress.py \
  --project-dir projects/ai-human-co-production \
  --status projects/ai-human-co-production/STATUS.md \
  --open-tasks projects/ai-human-co-production/OPEN_TASKS.md \
  --window-min 30
```

## Closed-loop mode (verify → auto-execute → re-verify)

Use built-in script:

```bash
python3 skills/execution-verifier/scripts/verify_execute_verify.py \
  --verify-cmd "python3 skills/execution-verifier/scripts/verify_progress.py --project-dir projects/ai-human-co-production --status projects/ai-human-co-production/STATUS.md --open-tasks projects/ai-human-co-production/OPEN_TASKS.md --window-min 30" \
  --execute-cmd "openclaw cron run fc567f18-83fa-426c-8181-71a10f4568b3 --force"
```

Behavior:
- Step A: verify current progress
- Step B: if no progress, auto-trigger executor
- Step C: verify again
- Output JSON includes `before`, `triggered_execute`, `after`

## Cron pattern (recommended)

Use two jobs:

- **Executor job (isolated agentTurn, every 30m):** do real work + write files.
- **Verifier job (main systemEvent, every 30m offset +5m):** run closed-loop script above.

Never run report-only cron without verifier.
