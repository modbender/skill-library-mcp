---
name: task-finish-contract
description: Enforce task completion with explicit Goal/Progress/Next state. Prevent mid-task stalls and ensure evidence-based completion.
---

# Task Finish Contract

Prevent mid-task stalls. Every task must finish with explicit state and evidence.

## Problem

Agents often:
- Stop mid-task without explanation
- Output plans without execution
- Lack clear completion criteria
- Missing evidence artifacts

## Workflow

### 1. State Output (Each Substantial Step)

```markdown
**Goal**: What finished looks like
**Progress**: What has been done
**Next**: One concrete action executing now
```

### 2. Completion Proof Format

For tasks with 2+ steps, include:

```markdown
**DONE_CHECKLIST**:
- [ ] Item 1 completed
- [ ] Item 2 completed

**EVIDENCE**:
- Executed: command/action summary
- Artifact: path/URL/id
- Verified: check command result

**NEXT_AUTONOMOUS_STEP**:
- One follow-up that runs without user input
```

### 3. Anti-Stall Rule

- Planning-only replies: max 1
- Next reply MUST contain execution evidence
- Never end with "I will now..." without tool result

## Executable Completion Criteria

| Criteria | Verification |
|----------|-------------|
| Goal stated | `Select-String "Goal" memory/{date}.md` matches |
| Progress tracked | `Select-String "Progress" memory/{date}.md` matches |
| Next action defined | `Select-String "Next" memory/{date}.md` matches |
| Evidence present | Artifact path/URL exists |
| No unresolved markers | `Select-String "TODO|PENDING|TBD" artifact` returns nothing |

## Privacy/Safety

- No sensitive data in completion evidence
- Artifact paths use relative or workspace paths
- No credentials in task logs

## Self-Use Trigger

Use when:
- Starting any multi-step task
- Resuming after interruption
- Handoff to another agent

---

**Finish what you start. Prove it with evidence.**
