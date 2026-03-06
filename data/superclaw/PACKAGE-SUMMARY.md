# Superclaw - Package Summary

**Version:** 1.0.0  
**Status:** Complete and Validated  
**Build Date:** 2026-02-25  
**Build Time:** ~3 hours (18:12 - 21:30 UTC)

---

## What is Superclaw?

OpenClaw implementation of the [Superpowers methodology](https://github.com/obra/superpowers) by Jesse Vincent. A complete software development workflow enforced through 3 chained skills.

---

## Package Contents

### 3 Core Skills (All Pressure-Tested)

#### 1. **Brainstorming** (`brainstorming/SKILL.md`)
- **Size:** 279 lines, 8.4KB
- **Purpose:** Enforces design-before-code
- **Hard Gate:** No code until design approved
- **Process:** Context check → Questions → Approaches → Design → Approval → Save → Invoke writing-plans
- **Pressure Tested:** Resists "I'm in a hurry, just start coding" (RED: 12 seconds to code, GREEN: questions + design)

#### 2. **Writing-Plans** (`writing-plans/SKILL.md`)
- **Size:** 10KB
- **Purpose:** Enforces plan-before-implementation
- **Key Feature:** ASK about methodology (TDD? Commit frequency?) instead of mandating
- **Process:** Ask methodology → Break into tasks (2-5 min each) → Save plan → Invoke executing-plans
- **Pressure Tested:** Resists "Design is detailed, just build it" (RED: 73 seconds to code, GREEN: methodology questions + plan)

#### 3. **Executing-Plans** (`executing-plans/SKILL.md`)
- **Size:** ~9KB
- **Purpose:** Enforces batched execution with checkpoints
- **Process:** Load plan → Batch (3-5 tasks) → Execute → Review → Checkpoint → Update memory → Repeat
- **Integration:** Uses sessions_spawn per task for isolation
- **Pressure Tested:** Resists "Execute all at once, no interruptions" (RED: 40 seconds all tasks, GREEN: 2:12 with 4 batches + checkpoints)

---

## OpenClaw-Specific Adaptations

1. **Memory Integration**
   - Check MEMORY.md, USER.md, daily logs for context
   - Update memory/YYYY-MM-DD.md with progress

2. **Workspace Conventions**
   - Design docs: `workspace/docs/plans/YYYY-MM-DD-<topic>-design.md`
   - Plan docs: `workspace/docs/plans/YYYY-MM-DD-<topic>-plan.md`

3. **Methodology Questions (Not Mandates)**
   - "Should we use TDD?" instead of "You must use TDD"
   - Respects user preferences and time constraints

4. **Sessions_spawn Integration**
   - Fresh subagent per task for isolation
   - Context from plan, not from main session

---

## Testing Summary

### Phase 2: Brainstorming Skill
- **RED (baseline):** Agent coded in 12 seconds without design
- **GREEN (with skill):** Agent asked questions, resisted pressure
- **Result:** PASS ✅

### Phase 3: Writing-Plans Skill
- **RED (baseline):** Agent coded in 73 seconds without plan
- **GREEN (with skill):** Agent asked methodology, committed to plan
- **Result:** PASS ✅

### Phase 4: Executing-Plans Skill
- **RED (baseline):** Agent executed all 10 tasks in 40 seconds, no batching
- **GREEN (with skill):** Agent batched into 4 groups, checkpointed between each
- **Result:** PASS ✅

### Phase 5: Integration Test
- **Scenario:** "Build a markdown notes CLI"
- **Skills chained:** brainstorming → writing-plans → executing-plans (automatic)
- **Documents created:** Design doc, plan doc, execution log
- **Deliverable:** Working CLI tool
- **Result:** PASS ✅

---

## Test Artifacts

All test results preserved in `/data/workspace/superclaw-tests/`:
- Baseline scenarios (RED phase)
- Baseline results (rationalizations documented)
- GREEN phase results (skill compliance)
- Integration test results

---

## Attribution

Based on [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent.

Adapted for OpenClaw's multi-surface, personal assistant architecture with:
- Memory system integration
- Methodology questions (not mandates)
- Sessions_spawn workflow
- Single workspace model (no git worktrees)

---

## Installation (Future)

```bash
openclaw hub install superclaw
```

Skills will auto-load when relevant tasks are detected.

---

## License

MIT (following obra/superpowers)

---

## Build Metadata

- **Methodology:** Dogfooding (built using superpowers principles)
- **Build approach:** RED-GREEN-REFACTOR for each skill
- **Total build time:** ~3 hours
- **Skills created:** 3
- **Total lines:** ~1000+ (across all skills)
- **Test scenarios:** 12 (RED + GREEN for each skill, plus integration)

**Status:** Ready for ClaWHub distribution
