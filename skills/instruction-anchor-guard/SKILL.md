---
name: instruction-anchor-guard
version: 1.1.0
description: Preserve user-critical instructions across long sessions and context compaction. Use when users mark constraints as important/must/always/never/highest-priority/rules, and enforce anchor checks before and after compaction to prevent plan drift.
metadata:
  openclaw:
    emoji: "[ANCHOR]"
    category: resilience
---

# Instruction Anchor Guard

Prevent loss or drift of user-critical constraints during compaction, session restart, or long multi-turn tasks.

## When To Trigger

Trigger when any of these appear:
- User marks an instruction as important, critical, must, always, never, highest priority, rule, or constraint
- A task has more than 3 steps and spans multiple turns
- Compaction happened (or is likely) and the task has non-negotiable requirements
- Agent behavior shows possible drift from prior explicit user constraints

## Anchor Ledger Schema

Store anchors in first available path:
1. `memory/anchors.md`
2. `memory/instruction-anchors.md`
3. `.anchors.md` (workspace root fallback only)

Entry schema (append-only, one section per anchor):
```markdown
## Anchor: <id>
- **source**: <session-id|message-id|user>
- **instruction**: <canonical instruction text>
- **verbatim**: <short quote from user>
- **priority**: P0 | P1 | P2
- **scope**: global | session | task:<id> | channel:<id>
- **createdAt**: <ISO-8601 timestamp>
- **expiresAt**: <ISO-8601 timestamp or "never">
- **status**: active | paused | expired | superseded
- **signature**: <stable hash of canonical instruction>
- **supersedes**: <anchor-id or none>
```

## Workflow

### 1) Capture
- Parse latest user message for candidate anchor statements
- Keep only instruction/constraint content; remove examples/chatter
- Assign default values:
  - priority: P1 (unless user says critical/highest -> P0)
  - scope: session (unless user explicitly asks global/task scope)
  - expiresAt: session end (unless user explicitly sets never/date)

### 2) Confirm for Broad Anchors
- If scope is `global` or priority is `P0`, ask a one-line confirmation before persisting
- Do not auto-promote P2/P1 to P0 without explicit user intent

### 3) Persist
- Append anchor entry to ledger
- If new anchor conflicts with old same-scope anchor, mark old one `superseded`
- Never rewrite history silently; keep audit trail

### 4) Rehydrate (each turn and after compaction)
- Load active anchors (status=active and not expired)
- Build an in-memory `ANCHOR_SET` sorted by priority and recency
- Inject `ANCHOR_SET` into planning phase before tool execution

### 5) Drift Check (before final answer and before destructive actions)
- Compare current plan against active anchors
- On conflict:
  - P0 conflict: stop and correct plan immediately
  - P1 conflict: auto-correct and note adjustment
  - P2 conflict: continue only if no user-level contradiction
- Emit `DRIFT_CHECK` block in response

## Conflict Resolution

Priority order:
1. System and safety policy
2. User anchors (P0 > P1 > P2)
3. Current-turn temporary preferences

Tie-breakers:
- More specific scope wins (`task` > `session` > `global`) if same priority
- Newer anchor wins if same priority and same scope
- Explicit user override wins only when safety is not violated

## Output Template

When anchors exist, include this compact block:

```markdown
ANCHORS_ACTIVE
| ID | P | Scope | Expires | Instruction |
|----|---|-------|---------|-------------|
| anchor-001 | P0 | global | never | Never perform destructive data deletion without confirmation |

PLAN_GUARD
- Current action: <action>
- Conflicts: none | <anchor ids>
- Decision: clear | corrected | paused-awaiting-user

DRIFT_CHECK
- Last anchor sync: <timestamp>
- Drift: no | yes
- Fix applied: <none|what changed>
```

## Safety Boundaries

- Never store tokens, API keys, passwords, cookies, or auth headers
- Never store raw personal data unless strictly required by user instruction
- Redact sensitive literals as `[REDACTED]`
- Store constraints, not datasets
- Do not execute destructive commands solely because an anchor exists; still require explicit confirmation for destructive actions

## Expiry and Maintenance

- Mark `expired` when `expiresAt < now`
- Support control intents:
  - `/anchors list`
  - `/anchors pause <id>`
  - `/anchors resume <id>`
  - `/anchors delete <id>`
  - `/anchors pin <id> never`
- Rotate ledger when > 200 entries into `memory/anchors-archive-YYYY-MM.md`

## Integration Notes

- Pair with `memory-self-heal` for retry/fallback after drift correction
- Pair with `task-execution-guard` to enforce anchor checks at each milestone
- Keep this skill deterministic and concise; avoid free-form interpretation when conflict exists
