# ACTIVITIES.md — Current Sprint

## PRIME DIRECTIVE
What is being created in this sprint must be a thoroughly detailed instruction set that can be followed with **zero context** every time. No step may rely on prior chat memory, implied intent, or ambiguous wording. Every directive must be executable as written by a cold-start agent.

---

## Project Queue (portfolio)

This section is the **only** authoritative queue for auto-promotion.
The controller MUST NOT scan folders to discover projects.

Queue states (closed enum): `BACKLOG | ACTIVE | COMPLETE | BLOCKED`

Deterministic promotion rule (executed only when current sprint state becomes `COMPLETE`):
1. Find the first row (top-to-bottom) with `Queue State=BACKLOG`.
2. Promote exactly that row to `ACTIVE`.
3. Import its sprint plan into `## Sprint Steps` using `Plan Path` (see `HEARTBEAT.md` “Sprint Plan Import Protocol”).
4. Emit: `PROJECT_PROMOTED from="<previous project>" to="<new project>"`.
5. If no BACKLOG rows exist: emit `HB_PORTFOLIO_COMPLETE message="all projects complete"`.

| Order | Project | Queue State | Plan Path | Notes |
|---:|---|---|---|---|
| 1 | <Your Project 1> | BACKLOG | `projects/<project-1>/sprint-plan.md` | - |

---

## Sprint Steps (manager-led multi-worker execution)

### ACTIVE Sprint
Sprint state: **PAUSED**

No active sprint. Add a BACKLOG project row above with a valid `Plan Path`, then arm automation.

---

## Worker Assignment Table

| Worker Session | Assigned Step # | State | Started | Timeout | Retry Count | Last Seen | Next Action |
|---|---:|---|---|---|---:|---|---|
| (none) | - | STOPPED | - | - | - | - | Portfolio idle (no active sprint). |

---

## BLOCKED

| Item | Blocker | Unblock Condition | Owner |
|------|---------|-------------------|-------|
| None | No active blockers. | N/A | manager |

---

## Rules

1. Exactly **one ACTIVE sprint/project** at a time.
2. Manager may run up to **2 concurrent subagents** for current sprint throughput (must not exceed configured `agents.defaults.subagents.maxConcurrent`).
3. Every dispatched worker task must have an explicit complete condition.
4. On worker completion/failure: immediately assign next concrete READY step.
   - Task-dependent subagent routing (assignment-time):
     - Coding/implementation/execution: spawn subagent with model `openai-codex/gpt-5.3-codex`.
     - Research/requirements/architecture: spawn subagent with model `openai-codex/gpt-5.2`.
   - Worker thinking selection rule (assignment-time):
     - Implementation/coding from a clear spec: subagent `thinking=off|low`.
     - Debugging a failing test/build: subagent `thinking=medium`.
     - High-risk refactor/architecture: subagent `thinking=high` (rare; time-box and revert).
5. Poll workers every 3 minutes and respawn/reassign if stalled.
6. Sprint ends only when the Definition of Done is fully satisfied, or all remaining items are BLOCKED.
7. Stop automation (disable 3-min poll + heartbeat cadence) only after final verification confirms no READY work remains and sprint state is set to COMPLETE/BLOCKED.
