# Implementation Guide

## Phase 1: Create Folder Structure

```bash
cd ~/.openclaw/workspace
mkdir -p state memory/archive ops
```

## Phase 2: Create State Files

### state/ACTIVE.md
```markdown
# ACTIVE.md — Current Task

> Write the user's **exact words** here BEFORE interpreting.

---

## Current Instruction

**User said:** [none yet]

**Interpretation:** [waiting for task]

**Status:**
- [ ] Waiting for instruction

---

*Updated: [timestamp]*
```

### state/HOLD.md
```markdown
# HOLD.md — Blocked Items

> Items here are BLOCKED. All agents must check before acting.

## Format
```
[YYYY-MM-DD HH:MM | session] Item — reason blocked
```

## Currently Blocked

[none]

---

*Updated: [timestamp]*
```

### state/STAGING.md
```markdown
# STAGING.md — Drafts Awaiting Approval

> Content here would be lost on context flush. Preserve drafts until published.

## Format
```
### [Item Name]
**Created:** YYYY-MM-DD
**Status:** draft | pending | approved | rejected
**Location:** path/to/file.md
```

## Currently Staged

[none]

---

*Updated: [timestamp]*
```

### state/DECISIONS.md
```markdown
# DECISIONS.md — Recent Choices

> Record significant decisions with timestamps.

## Format
```
[YYYY-MM-DD HH:MM | session] Decision made
```

## Recent Decisions

[none]

---

*Updated: [timestamp]*
```

## Phase 3: Create Ops Files

### ops/WORKSPACE-INDEX.md
```markdown
# WORKSPACE-INDEX.md — Map of the Workspace

## Core Files (Root)

| File | Purpose |
|------|---------|
| AGENTS.md | Operating rules |
| SOUL.md | Identity + personality |
| USER.md | About the human |
| MEMORY.md | Long-term memory |
| LESSONS.md | Safety rules |
| TOOLS.md | Tool notes |

## State Files (state/)

| File | Purpose |
|------|---------|
| ACTIVE.md | Current task |
| HOLD.md | Blocked items |
| STAGING.md | Drafts |
| DECISIONS.md | Choices |

## Memory (memory/)

| File | Purpose |
|------|---------|
| YYYY-MM-DD.md | Daily logs |
| recent-work.md | Last 48 hours |
| archive/ | Old logs |
```

## Phase 4: Update AGENTS.md

Add to your AGENTS.md:

```markdown
## Boot Sequence

Before doing anything:
1. Read `state/HOLD.md` — blocked items
2. Read `state/ACTIVE.md` — current task
3. Read `state/DECISIONS.md` — recent choices
4. Read `memory/recent-work.md` — last 48 hours

## 🐠 Dory-Proof Pattern

When user gives a task:
1. **IMMEDIATELY** write EXACT WORDS to `state/ACTIVE.md`
2. Then interpret
3. Then do the work
4. Mark complete when done
```

## Phase 5: Create memory/recent-work.md

```markdown
# Recent Work — Last 48 Hours

> Updated by all agents after producing deliverables.

## [Today's Date]

### [Project Name] — [STATUS]
- **Path:** `path/to/files/`
- **What:** Brief description
- **Next:** What's remaining
```

## Phase 6: Test the System

1. Give a task
2. Verify ACTIVE.md captures exact words
3. Complete the task
4. Verify recent-work.md updated
5. Simulate context flush (new session)
6. Verify boot sequence reads state correctly

## Maintenance

### Daily
- Update memory/YYYY-MM-DD.md with significant events
- Update recent-work.md after deliverables

### Weekly
- Archive daily logs older than 7 days
- Prune MEMORY.md if over 10KB
- Review HOLD.md for stale blocks

### On Incidents
- Add to LESSONS.md immediately
- Include: what happened, why, prevention
