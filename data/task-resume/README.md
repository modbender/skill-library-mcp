# task-resume

Automatic interrupted-task resume workflow for OpenClaw agents.

`task-resume` solves a common execution failure: important tasks get interrupted by new requests and never get resumed. This skill adds a deterministic queue + recovery pattern so an agent can finish the current interrupting task and then automatically resume previously interrupted work.

---

## Why this skill exists

In real assistant workflows, context switching is unavoidable:

- A priority task is in progress
- A user asks something else in the middle
- The agent switches focus
- The original task gets dropped

`task-resume` prevents this by enforcing:

1. **Interruption detection**
2. **State capture into a queue**
3. **Automatic resume after current task completion**
4. **FIFO recovery order + deduplication**
5. **Default auto-enqueue on non-explicit interruption**
6. **Unified cross-session queue view (main + clone + group sessions)**

---

## Core capabilities

- Queue interrupted tasks with:
  - title
  - context (done + exact next step)
  - acceptance criteria
  - source channel/session
- Pop and resume oldest interrupted task (FIFO)
- Deduplicate near-identical repeated interruptions
- List, status, and clear queue for operations/debugging
- Persist queue to workspace-global memory file shared across sessions
- Include `source` and `session` metadata for unified observability

Queue file:

- `memory/task-resume-queue.json`

---

## Files

```text
task-resume/
├── SKILL.md
└── scripts/
    └── task_resume_queue.py
```

---

## Command interface

### Add interrupted task

```bash
python3 skills/task-resume/scripts/task_resume_queue.py add \
  --title "<task title>" \
  --context "<done + exact next step>" \
  --acceptance "<acceptance criteria>" \
  --source "<channel>" \
  --session "<session_key_or_chat_id>"
```

### Pop oldest task (resume target)

```bash
python3 skills/task-resume/scripts/task_resume_queue.py pop
```

### List queue

```bash
python3 skills/task-resume/scripts/task_resume_queue.py list
```

### Queue status (unified cross-session view)

```bash
python3 skills/task-resume/scripts/task_resume_queue.py status
```

### Clear queue

```bash
python3 skills/task-resume/scripts/task_resume_queue.py clear
```

### Recover from session log (tolerates missing `.jsonl`)

```bash
python3 skills/task-resume/scripts/task_resume_queue.py recover \
  --log "~/.openclaw/agents/main/sessions/<session>.jsonl" \
  --title "<interrupted task title>" \
  --acceptance "<acceptance criteria>" \
  --source "<channel>" \
  --session "<session_key_or_chat_id>"
```

If the log file does not exist, the command returns `skipped_missing_log` instead of failing.

---

## Recommended policy

Treat these user commands as explicit override (do **not** auto-resume):

- `cancel`
- `pause`
- `change priority`
- `do it tomorrow`

Everything else can be considered a temporary interruption candidate.

---

## Operational guardrails

- Never drop queued tasks silently
- Always capture a precise next step when enqueueing
- Deduplicate identical title + context pairs
- Keep queue bounded (default implementation max: 30)
- Avoid storing sensitive secrets in queue content

---

## Recent updates

### v1.3 (latest)

- Added **Watchdog Auto-Continue** guidance for heartbeat/cron mode:
  - check unfinished primary task every 30 minutes
  - auto-continue when interrupted or stalled
  - send progress each run (`done / in-progress / next+ETA`)
  - still send巡检回执 when no material progress
- Added reliability recommendation:
  - prefer `sessionTarget=main` + `systemEvent` for critical continuity reminders
  - reduce dependency on fragile announce-only delivery chains

### v1.2

- Added `recover` command for log-based recovery flows:
  - `python3 skills/task-resume/scripts/task_resume_queue.py recover --log <session.jsonl> ...`
- Added **ENOENT soft-fail** behavior for missing `.jsonl` logs:
  - missing file is now treated as `skipped_missing_log` (non-fatal), not an alert-grade failure
- Improved output consistency with structured JSON statuses across commands
- Preserved queue dedup + FIFO semantics

### v1.1

- Set **auto-enqueue on interruption** as default behavior
- Added **message-time enforcement**: enqueue before context switch, not only periodic checks
- Added `--session` to enqueue command
- Added `status` command for unified queue observability
- Clarified shared queue behavior across main/clone/group sessions
- Kept all docs and skill files fully in English

## Validation performed

Stress test completed with 3 consecutive interruptions:

- enqueue A, B, C
- repeat B (dedup check)
- pop x3

Observed behavior:

- dedup worked (`updated`, queue count unchanged)
- resume order preserved (A → B → C)
- queue emptied correctly

---

## Use cases

- Long-form doc editing with frequent side interruptions
- Multi-step delivery pipelines with strict acceptance criteria
- Assistants operating across chat groups + DMs
- Task continuity in noisy real-world conversation streams

---

## Publishing to ClawHub

Package and publish from skill folder:

```bash
clawhub publish ./skills/task-resume \
  --slug task-resume \
  --name "Task Resume" \
  --version 1.0.0 \
  --changelog "Initial release: interrupted-task queue and auto-resume workflow"
```

---

## License

Use and adapt for your OpenClaw workflows.
