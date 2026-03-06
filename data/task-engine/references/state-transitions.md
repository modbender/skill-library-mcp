# State Transitions Reference

## Task States

| From | Event | To | Notes |
|------|-------|----|-------|
| PLANNING | approve | APPROVED | Human confirms plan |
| PLANNING | reject | REJECTED | Terminal — human rejects plan |
| APPROVED | start | IN_PROGRESS | At least 1 subtask dispatched |
| IN_PROGRESS | test | TESTING | All dev subtasks DONE |
| IN_PROGRESS | block | BLOCKED | External dependency; record reason |
| IN_PROGRESS | fail | FAILED | Unrecoverable error; terminal |
| TESTING | review | REVIEW | All test subtasks DONE |
| TESTING | reopen | IN_PROGRESS | Tests failed — back to dev |
| TESTING | fail | FAILED | Unrecoverable test failure; terminal |
| REVIEW | complete | COMPLETED | Human accepts final result; terminal |
| REVIEW | reopen | IN_PROGRESS | Human requests changes |
| REVIEW | fail | FAILED | Rejected at review; terminal |
| BLOCKED | unblock | IN_PROGRESS | Blocker resolved |
| BLOCKED | fail | FAILED | Blocker unresolvable; terminal |

**Terminal states:** COMPLETED, FAILED, REJECTED

## Subtask States

| From | Event | To | Notes |
|------|-------|----|-------|
| PENDING | assign | ASSIGNED | Agent identified, dispatch instruction |
| ASSIGNED | start | IN_PROGRESS | Agent acknowledges work begun |
| IN_PROGRESS | done | DONE | Agent reports completion + result |
| IN_PROGRESS | fail | FAILED | Agent reports failure + reason |
| IN_PROGRESS | block | BLOCKED | Dependency unmet; record reason |
| ASSIGNED | block | BLOCKED | Pre-start blocker discovered |
| BLOCKED | unblock | ASSIGNED | Blocker resolved; re-queue |

**Terminal states:** DONE, FAILED

## Auto-Transitions

These transitions are evaluated by the heartbeat checker and on subtask completion:

| Condition | Event | Action |
|-----------|-------|--------|
| All `type: dev` subtasks DONE | test | Task IN_PROGRESS -> TESTING |
| All `type: test/validate` subtasks DONE | review | Task TESTING -> REVIEW |
| First subtask dispatched | start | Task APPROVED -> IN_PROGRESS |

## Auto-Alerts (heartbeat)

| Condition | Alert |
|-----------|-------|
| Subtask stuck (no progress across 3+ heartbeats) | STUCK alert, pings human |
| Task past ETA | OVERDUE alert |
| Subtask FAILED | FAILED alert, pings human |
| Subtask slow progress (< threshold across beats) | SLOW alert |

## State Diagram — Tasks

```
PLANNING ──approve──> APPROVED ──start──> IN_PROGRESS ──test──> TESTING ──review──> REVIEW ──complete──> COMPLETED
    │                                         │  │                 │  │                │
    │reject                              block│  │fail        reopen│  │fail       reopen│ fail
    v                                         v  v                 v  v                v   v
 REJECTED                                BLOCKED FAILED      IN_PROGRESS FAILED   IN_PROGRESS FAILED
                                           │
                                      unblock│
                                           v
                                      IN_PROGRESS
```

## State Diagram — Subtasks

```
PENDING ──assign──> ASSIGNED ──start──> IN_PROGRESS ──done──> DONE
                       │                    │  │
                       │block          block│  │fail
                       v                    v  v
                    BLOCKED             BLOCKED FAILED
                       │
                  unblock│
                       v
                    ASSIGNED
```
