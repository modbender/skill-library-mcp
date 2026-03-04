# Checkpoint Formats — Context Protection

**Purpose:** Protect context through proactive checkpointing. Write before you lose it.

**WAL Protocol:** Write checkpoints to memory/episodic/[today].md BEFORE responding when context ≥70%.

---

## Thresholds & When to Checkpoint

| Context % | Action | Checkpoint Type |
|-----------|--------|-----------------|
| < 50% | 🟢 Normal operation | Quick notes only as needed |
| 50-69% | 🟡 Vigilant | Quick notes after significant exchanges |
| 70-84% | 🟠 **Active — MUST CHECKPOINT NOW** | Full checkpoint to memory/episodic/[today].md |
| 85-94% | 🔴 **Emergency — MUST CHECKPOINT NOW** | Emergency checkpoint, then pause |
| 95%+ | 🚨 Survival | Emergency checkpoint (survival data only) |

**Rule:** Write checkpoint to memory/episodic/[today].md IMMEDIATELY when context ≥70%.

---

## Checkpoint Formats

### Full Checkpoint (70-84% Context)

**Write to:** `memory/episodic/[today].md`

```markdown
## Checkpoint [HH:MM] — Context: XX%

### Current Session
**Started:** [time/date or "Session in progress"]
**Task:** [what we're working on in one line]
**Status:** in progress / blocked / completing

### Work State

**Active Files:**
- [file1.ext] — [what we're doing with it]
- [file2.ext] — [status]

**Key Decisions Made:**
- [Decision 1]: [reasoning]
- [Decision 2]: [reasoning]

**Progress:**
- [x] [Completed step]
- [x] [Completed step]
- [ ] [In progress] ← WE ARE HERE
- [ ] [Next step]
- [ ] [Future step]

### Context to Preserve

**Human's Goals:**
[What the human is ultimately trying to achieve — check GOALS.md or project docs if needed]

**Important Constraints:**
[Things we must not forget — security, preferences, limitations]

**Preferences Expressed:**
[How the human wants things done — style, approach, format]

### Resume Instructions
1. [First thing to do if context is lost]
2. [Second thing to do]
3. [Continue from step X — "We were working on..."]

### Open Questions
- [Unresolved item or question]
- [Another question that came up]

**Notes:** [Any other context worth preserving]
```

---

## Emergency Checkpoint (85-94% Context)

**Write to:** `memory/episodic/[today].md`

```markdown
## EMERGENCY CHECKPOINT [HH:MM] — Context: XX%

**TASK:** [One line - what we're doing]
**STATUS:** [One line - where we are]
**NEXT:** [One line - immediate next step]
**BLOCKED:** [If applicable, or "None"]
**FILES:** [Key files involved]
```

**Then pause and acknowledge in chat:**
```
⚠️ Emergency checkpoint written at [HH:MM]. Context at [XX%]. Pausing to await compaction recovery.
```

---

## Survival Checkpoint (95%+ Context)

**Write to:** `memory/episodic/[today].md`

**Capture ONLY critical data:**

```markdown
## SURVIVAL [HH:MM] — Context: XX%

**TASK:** [One line]
**NEXT:** [One line]
**BLOCKED:** [Yes/No]
```

---

## Pre-Operation Checkpoint

Use before any operation that could fail or take significant time (e.g., large file operations, system updates, complex refactoring).

```markdown
## Pre-Operation [HH:MM]

**About to:** [Operation in one line]
**Current state:** [Where we are right now]
**After success:** [What to do next]
**If failure:** [Recovery steps in 2-3 lines]
```

---

## Quick Notes (50-69% Context)

**Write to:** `memory/episodic/[today].md`

```markdown
### [HH:MM] Note

[Brief context worth preserving — decision, preference, important detail]
```

Use short notes to capture important context without full checkpoint overhead when context is moderate (50-69%).

---

## What to Capture

**Ask yourself before writing checkpoint:**
> **"Could future-me continue this conversation from notes alone?"**

**Include in checkpoints:**
- ✅ **Decisions made and their reasoning** — Why we chose this path
- ✅ **Action items and who owns them** — What needs to happen next
- ✅ **Open questions or threads** — Unresolved items we need to address
- ✅ **Significant learnings** — Things we discovered
- ✅ **Preferences expressed** — How they want things done
- ✅ **Blockers and constraints** — What's stopping us
- ✅ **File states** — What we're working on and where we left off

**Don't include:**
- ❌ Complete conversation history (that's in the session itself)
- ❌ Trivial details (doesn't help recovery)
- ❌ Speculation without decision (we can recover context for speculation)

---

## Recovery Procedure (After Context Loss or Compaction)

1. **Check latest checkpoint:**
   - Read `memory/episodic/[today].md`
   - Find the most recent checkpoint entry

2. **Load permanent context:**
   - Read project's main memory files (MEMORY.md, etc.)
   - Read relevant documentation
   - Read semantic decisions if available

3. **Follow resume instructions:**
   - Checkpoints include "Resume Instructions" — follow them exactly
   - Start from the step indicated (e.g., "Continue from step X: We were working on...")

4. **Acknowledge the gap:**
   ```
   "Resuming from checkpoint at [time].
   Last captured: [status summary].
   Continuing with [next action]."
   ```

5. **Verify continuity:**
   - Ask human if anything was missed or changed during the gap
   - Confirm priorities haven't shifted
   - Check if any new context emerged

---

## Critical Principle

> **Write it down NOW — not later.**
>
> Don't assume future-you will have this conversation in context. The best checkpoint is the one you write before you need it.

If context ≥70%, stopping to write checkpoint is ALWAYS worth it. A 30-second checkpoint saves minutes or hours of lost work from context recovery.

---

## Examples

### Example 1 — Full Checkpoint

```markdown
## Checkpoint 14:30 — Context: 75%

### Current Session
**Started:** 13:45, 2026-02-13
**Task:** Update TOOLS.md with gotchas section
**Status:** in progress

### Work State

**Active Files:**
- TOOLS.md — Adding tool quirks and gotchas section
- INDEX.md — Created for file organization reference

**Key Decisions Made:**
- TOOLS.md: Keep quick reference at top, add gotchas section at bottom
- INDEX.md: Adapt from template for workspace structure

**Progress:**
- [x] Read INDEX-template.md, TOOLS-template.md, checkpoint-template.md
- [x] Created INDEX.md adapted for project
- [x] Enhanced TOOLS.md with quick reference + gotchas
- [ ] Updating memory/procedural/checkpoints.md (CURRENT TASK)
- [ ] Test all new structures

### Context to Preserve

**Human's Goals:**
- Adapt templates (INDEX, TOOLS, checkpoint) into system
- Maintain hybrid memory structure

**Important Constraints:**
- Workspace protection is ABSOLUTE — double confirmation before any deletion/cleanup
- Files must match actual filesystem

**Preferences Expressed:**
- "adapt and imprint" — make templates useful, not copy blindly
- Check paths and replace to actual workspace

### Resume Instructions
1. Continue enhancing checkpoints.md with better formats from template
2. Verify all new structures match actual filesystem
3. Document changes in VERSION.md

### Open Questions
- Should KNOWLEDGE.md be created? (Template suggests it, but knowledge is dispersed)

**Notes:** Human wants tools.md "recheck path files and replace to your workspace" — VERIFIED all paths match.
```

---

### Example 2 — Emergency Checkpoint

```markdown
## EMERGENCY CHECKPOINT 19:45 — Context: 88%

**TASK:** Updating all scripts to use memory/episodic/ paths
**STATUS:** Updated 4 of 4 scripts (daily-ops.sh, weekly-review.sh, health-check.sh, status.sh)
**NEXT:** Test all scripts, document final list of changes
**BLOCKED:** None
**FILES:** scripts/daily-ops.sh, scripts/weekly-review.sh, scripts/health-check.sh, scripts/status.sh
```

Then acknowledge:
```
⚠️ Emergency checkpoint written at 19:45. Context at 88%. Pausing to await compaction recovery.
```

---

### Example 3 — Pre-Operation Checkpoint

```markdown
## Pre-Operation 20:20

**About to:** Update VERSION.md to v1.1.8 with path verification changes
**Current state:** All scripts tested and verified working, memory/procedural/checkpoints.md updated
**After success:** Create path-verification-2026-02-13.md documentation, announce completion
**If failure:** Revert VERSION.md to v1.1.7, note issue in daily log
```

---

*Checkpoint formats for context protection in autonomous systems*
*Autonomy skills: autonomy-type-based and autonomy-windowed*
