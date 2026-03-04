# Superclaw ⚔️

**A complete software development workflow for OpenClaw agents**

Superclaw enforces discipline through three chained skills: design before code, plan before implementation, batched execution with checkpoints.

Based on [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent, adapted for OpenClaw's personal assistant architecture.

---

## What It Does

Your agent doesn't just jump into code. It:

1. **🧠 Brainstorms with you** — Socratic questions, design proposals, approval before coding
2. **📋 Writes TDD-ready plans** — Breaks work into 2-5 minute tasks (with methodology questions, not mandates)
3. **⚙️ Executes in batches** — Groups tasks, checkpoints between batches, updates memory

---

## Installation (Future)

```bash
openclaw hub install superclaw
```

Skills auto-load when relevant tasks are detected.

---

## Skills Included

### 1. Brainstorming (`brainstorming/SKILL.md`)
**Enforces design-before-code**

- **Triggers:** When creating features, building components, adding functionality
- **Hard Gate:** No code until design approved
- **Process:** Context check → Questions → Approaches → Design → Approval → Save
- **Then:** Automatically invokes writing-plans skill

**Example:**
```
User: "Build a todo CLI"
Agent: [Asks questions about storage, features]
Agent: [Proposes 2-3 approaches with trade-offs]
Agent: [Presents design, gets approval]
Agent: [Saves design doc, invokes writing-plans]
```

### 2. Writing-Plans (`writing-plans/SKILL.md`)
**Enforces plan-before-implementation**

- **Triggers:** When you have an approved design
- **Key Feature:** ASKS about methodology (TDD? Commit frequency?) instead of mandating
- **Process:** Ask methodology → Break into tasks → Save plan
- **Then:** Automatically invokes executing-plans skill

**Example:**
```
Agent: "Should we use TDD (tests first) or direct implementation?"
User: "Direct implementation"
Agent: [Creates plan with 10 tasks, 2-5 min each]
Agent: [Saves plan doc, invokes executing-plans]
```

### 3. Executing-Plans (`executing-plans/SKILL.md`)
**Enforces batched execution with checkpoints**

- **Triggers:** When you have an implementation plan
- **Process:** Batch tasks (3-5) → Execute → Review → Checkpoint → Update memory → Repeat
- **Integration:** Uses sessions_spawn per task for isolation

**Example:**
```
Agent: "Executing batch 1 (tasks 1-3)..."
Agent: [Completes batch 1]
Agent: "Batch 1 complete. Continue to batch 2?"
User: "Yes"
Agent: [Continues to batch 2]
```

---

## Why Superclaw?

**Without Superclaw:**
- Agent jumps to code in seconds (no design, no plan)
- Errors compound across many tasks
- No checkpoints, can't pause/resume
- Mental plans get lost

**With Superclaw:**
- Design → Plan → Execute (enforced workflow)
- Errors caught early (batching prevents cascades)
- Progress tracked in memory
- Resumable, reviewable, auditable

---

## OpenClaw-Specific Features

1. **Memory Integration** — Checks MEMORY.md, USER.md, daily logs for context
2. **Methodology Questions** — "Should we use TDD?" not "You must use TDD"
3. **Sessions_spawn** — Fresh subagent per task for isolation
4. **Workspace Conventions** — Design/plan docs in `workspace/docs/plans/`

---

## Testing

All skills pressure-tested with RED-GREEN-REFACTOR:

| Skill | RED (no skill) | GREEN (with skill) |
|-------|----------------|-------------------|
| Brainstorming | Coded in 12s | Asked questions, got approval |
| Writing-Plans | Coded in 73s | Asked methodology, created plan |
| Executing-Plans | 10 tasks in 40s | 4 batches, checkpointed |

**Integration test:** All 3 skills chained automatically and delivered working CLI ✅

---

## Example Workflow

**User:** "Build a markdown notes CLI"

**Brainstorming skill:**
- Asks: Storage format? Search needed? Tagging?
- Proposes: 3 approaches (flat files vs SQLite vs JSON)
- Presents design, gets approval
- Saves: `workspace/docs/plans/2026-02-25-notes-cli-design.md`
- **Invokes writing-plans**

**Writing-plans skill:**
- Asks: TDD or direct? Commit frequency?
- Creates plan: 24 tasks, 2-5 min each
- Saves: `workspace/docs/plans/2026-02-25-notes-cli-plan.md`
- **Invokes executing-plans**

**Executing-plans skill:**
- Batch 1 (tasks 1-5): Project setup
- Checkpoint ✓
- Batch 2 (tasks 6-10): Create note feature
- Checkpoint ✓
- Batch 3 (tasks 11-15): List notes feature
- Checkpoint ✓
- (continues until complete)

**Result:** Working CLI tool, fully documented, tested, and tracked in memory.

---

## Attribution

Based on [obra/superpowers](https://github.com/obra/superpowers) by Jesse Vincent.

Adapted for OpenClaw with:
- Memory system integration
- Methodology questions (not mandates)
- Sessions_spawn workflow
- Single workspace model

---

## License

MIT (following obra/superpowers)

---

## Structure

```
superclaw/
├── brainstorming/
│   └── SKILL.md              # Design-before-code enforcement
├── writing-plans/
│   └── SKILL.md              # Plan-before-implementation enforcement
├── executing-plans/
│   └── SKILL.md              # Batched execution with checkpoints
├── README.md                 # This file
└── PACKAGE-SUMMARY.md        # Build metadata and testing summary
```

---

**Status:** ✨ Complete and validated (2026-02-25)  
**Ready for:** ClaWHub distribution
