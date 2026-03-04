---
name: superclaw
description: Complete software development workflow enforcing design → plan → execution with checkpoints
---

# Superclaw ⚔️

**Disciplined software development workflow for OpenClaw agents**

Based on [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent.

---

## What This Skill Package Does

Superclaw prevents your agent from jumping straight into code. It enforces a three-phase workflow:

1. **🧠 Brainstorming** (`brainstorming/SKILL.md`) — Design before code
2. **📋 Writing Plans** (`writing-plans/SKILL.md`) — Plan before implementation  
3. **⚙️ Executing Plans** (`executing-plans/SKILL.md`) — Batched execution with checkpoints

All three skills chain automatically when building software.

---

## How It Works

### Phase 1: Brainstorming (Design Before Code)

**Triggers:** When creating features, building components, adding functionality

**Process:**
1. Check context (MEMORY.md, USER.md, daily logs)
2. Ask Socratic questions (requirements, constraints, trade-offs)
3. Propose 2-3 approaches with pros/cons
4. Present design
5. Get approval
6. Save design document to `workspace/docs/plans/YYYY-MM-DD-<topic>-design.md`
7. **Automatically invoke writing-plans skill**

**Hard Gate:** No code until design approved.

---

### Phase 2: Writing Plans (Plan Before Implementation)

**Triggers:** When you have an approved design

**Process:**
1. **ASK about methodology** (TDD? Direct implementation?)
2. Ask about commit frequency
3. Break work into 2-5 minute tasks
4. Save implementation plan to `workspace/docs/plans/YYYY-MM-DD-<topic>-plan.md`
5. **Automatically invoke executing-plans skill**

**Key Feature:** Questions, not mandates. Respects user preferences and time constraints.

---

### Phase 3: Executing Plans (Batched Execution with Checkpoints)

**Triggers:** When you have an implementation plan

**Process:**
1. Load plan from document
2. Batch tasks into groups of 3-5
3. Execute batch (using `sessions_spawn` for isolation)
4. Review outputs
5. Checkpoint ("Batch N complete. Continue?")
6. Update `memory/YYYY-MM-DD.md` with progress
7. Repeat until complete

**Hard Gate:** Maximum 5 tasks per batch. Checkpoints cannot be skipped.

---

## Why Use Superclaw?

**Without Superclaw:**
- Agent jumps to code in seconds (no design, no plan)
- Errors compound across many tasks
- No checkpoints → can't pause/resume
- Mental plans disappear

**With Superclaw:**
- Design → Plan → Execute (enforced)
- Errors caught early (batching prevents cascades)
- Progress tracked in memory
- Resumable, reviewable, auditable

---

## Installation

```bash
npx clawhub@latest install superclaw
```

Skills auto-load when relevant tasks are detected.

---

## OpenClaw-Specific Adaptations

1. **Memory Integration** — Checks MEMORY.md, USER.md, daily logs
2. **Methodology Questions** — "Should we use TDD?" not "You must use TDD"
3. **Sessions_spawn** — Fresh subagent per task for isolation
4. **Workspace Conventions** — Saves to `workspace/docs/plans/`

---

## Testing

All skills pressure-tested with RED-GREEN-REFACTOR methodology:

| Skill | RED (without skill) | GREEN (with skill) |
|-------|---------------------|-------------------|
| Brainstorming | Coded in 12s | Asked questions, got approval |
| Writing-Plans | Coded in 73s | Asked methodology, created plan |
| Executing-Plans | 10 tasks in 40s | 4 batches with checkpoints |

**Integration test:** All 3 skills chained automatically and delivered working CLI ✅

---

## Example Workflow

**User:** "Build a markdown notes CLI"

**→ Brainstorming skill:**
- Asks: Storage format? Search needed? Tagging?
- Proposes: 3 approaches (flat files vs SQLite vs JSON)
- Presents design, gets approval
- Saves: `workspace/docs/plans/2026-02-25-notes-cli-design.md`
- **Invokes writing-plans**

**→ Writing-plans skill:**
- Asks: TDD or direct? Commit frequency?
- Creates plan: 24 tasks, 2-5 min each
- Saves: `workspace/docs/plans/2026-02-25-notes-cli-plan.md`
- **Invokes executing-plans**

**→ Executing-plans skill:**
- Batch 1 (tasks 1-5): Project setup → Checkpoint ✓
- Batch 2 (tasks 6-10): Create note feature → Checkpoint ✓
- Batch 3 (tasks 11-15): List notes feature → Checkpoint ✓
- (continues until complete)

**Result:** Working CLI tool, fully documented, tested, and memory-tracked.

---

## Individual Skill Files

- **`brainstorming/SKILL.md`** — 279 lines, full process + rationalization counters
- **`writing-plans/SKILL.md`** — 10KB, methodology questions + task templates
- **`executing-plans/SKILL.md`** — 9KB, batching logic + sessions_spawn integration

Each skill can be used independently or as part of the complete workflow.

---

## Attribution

Based on [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent.

Adapted for OpenClaw's personal assistant architecture with memory integration, methodology questions (not mandates), sessions_spawn workflow, and single workspace model.

---

## License

MIT (following obra/superpowers)

---

## Resources

- **GitHub:** https://github.com/brothaakhee/superclaw (coming soon)
- **Original Framework:** https://github.com/obra/superpowers
- **OpenClaw Docs:** https://docs.openclaw.ai
