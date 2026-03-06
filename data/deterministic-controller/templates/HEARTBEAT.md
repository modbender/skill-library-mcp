# HEARTBEAT.md — Controller Runtime (Deterministic)

## Scope
This file defines the only valid control loop.
Execute exactly as written.
Do not use prior chat context.

## Trigger Set
Valid trigger values:
- `HEARTBEAT_TICK`
- `POLL_TICK`
- `WORKER_EVENT`
- `MANUAL_RECONCILE`

Every trigger MUST run the same function: `controller_tick(trigger)`.

## Trigger Ingress Contract
A control cycle is valid only when one of the explicit trigger sources below is present.

- `HEARTBEAT_TICK`
  - Required ingress text (exact first line): `TRIGGER=HEARTBEAT_TICK`
- `POLL_TICK`
  - Required ingress text (exact first line): `TRIGGER=POLL_TICK`
- `WORKER_EVENT`
  - Required worker lines:
    - `TRIGGER=WORKER_EVENT`
    - `WORKER_STATE=COMPLETED|FAILED|TIMED_OUT`
    - `STEP=<step id or title>`
- `MANUAL_RECONCILE`
  - Required ingress text (exact first line): `TRIGGER=MANUAL_RECONCILE`

If no explicit trigger source is present, do not run `controller_tick`.

## Required Reads by Trigger (token-efficient)
- `HEARTBEAT_TICK` (full context refresh):
  - `AGENTS.md`, `IDENTITY.md`, `USER.md`, `SOUL.md`, `MEMORY.md`, `memory/YYYY-MM-DD.md` (today), `memory/YYYY-MM-DD.md` (yesterday), `ACTIVITIES.md`
- `POLL_TICK`:
  - `ACTIVITIES.md` only
  - Exception (queue promotion only): if and only if the current sprint transitions to `COMPLETE` and a next project is promoted from `BACKLOG`, the controller may also read exactly one additional file: the promoted row’s `Plan Path`, to import the next sprint plan into `ACTIVITIES.md`.
- `WORKER_EVENT`:
  - `ACTIVITIES.md` only
- `MANUAL_RECONCILE`:
  - default: `ACTIVITIES.md` only
  - full refresh only if operator explicitly requests it (then read the same set as `HEARTBEAT_TICK`).

## State Model
Step: `TODO | DOING | DONE | BLOCKED`
Sprint: `ACTIVE | BLOCKED | COMPLETE | PAUSED`
Queue: `BACKLOG | ACTIVE | COMPLETE | BLOCKED`

## Invariants
- No step may be `DONE` without evidence.
- Sprint cannot be `COMPLETE` if any step is `TODO` or `DOING`.
- If READY exists and capacity exists, dispatch must occur in the same control cycle.

## Logging Contract
All control-plane logs must be sent to a single destination.

**Destination (configure):**
- Telegram group id: `<TELEGRAM_GROUP_ID>`

Executable rule:
When this spec says "Emit <LINE>", do BOTH:
1) Print `<LINE>` in output.
2) Send via `message(action=send, channel="telegram", target="<TELEGRAM_GROUP_ID>", message="<LINE>")`.

Lifecycle logs:
- `HB_START trigger=<...>`
- `HB_COMPLETE trigger=<...> state=<WORKING|BLOCKED|COMPLETE> doing=<n> todo=<n> blocked=<n>`

Project logs:
- `PROJECT_TASK_STARTED task="..."`
- `PROJECT_TASK_COMPLETE task="..."`
- `PROJECT_TASK_FAILED task="..." reason="..." retry="n/max"`
- `PROJECT_TASK_BLOCKED task="..." reason="..."`

Portfolio logs:
- `PROJECT_PROMOTED from="<A>" to="<B>"`
- `HB_PORTFOLIO_COMPLETE message="all projects complete"`

## Sprint Plan Import Protocol (external plan files)
- Purpose: keep `ACTIVITIES.md` small even with many queued projects.
- Each queue row MUST include a `Plan Path`.
- On promotion (`BACKLOG -> ACTIVE`):
  1) Read the promoted row’s `Plan Path`.
  2) Replace the entire `## Sprint Steps (manager-led multi-worker execution)` section in `ACTIVITIES.md` with the sprint block from that file.
  3) Ensure the imported sprint block declares `Sprint state: **ACTIVE**`.
  4) Dispatch Step 1 per same-cycle rules.
- The controller MUST NOT read any other backlog plan files besides the one being promoted.

## Canonical Control Function (high-level)
1) Emit `HB_START trigger=<trigger>`.
2) Read required files.
3) Abort safely if `ACTIVITIES.md` unreadable.
4) Acquire lock; snapshot previous state.
5) Reconcile worker outcomes into step states.
6) Enforce same-cycle dispatch.
7) If sprint becomes COMPLETE: archive/flush, then promote+import next plan if any.
8) Persist `ACTIVITIES.md`.
9) Emit `HB_COMPLETE ...`.
