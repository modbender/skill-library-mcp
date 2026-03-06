---
name: executing-plans
description: Use when executing implementation plans - enforces batching, checkpoints, and progress tracking
---

# Executing Plans Skill

## Core Principle

**Batched execution with checkpoints prevents cascading failures.**

Plans are executed in small batches (3-5 tasks) with mandatory checkpoints between batches. This allows early error detection, user course-correction, and resumable progress.

---

## ⛔ HARD GATES

1. **DO NOT execute more than 5 tasks without a checkpoint**
2. **DO NOT skip progress updates to memory logs**
3. **DO NOT execute tasks all at once, even if user says "no interruptions"**
4. **DO NOT rationalize away batching for "efficiency"**

Checkpoints are safety mechanisms, not annoyances. They catch errors early before they compound.

---

## Process

### Step 1: Load the Plan

**Find the plan:**
- Check `workspace/docs/plans/` for the relevant plan file
- Plans are named: `YYYY-MM-DD-<topic>-plan.md`
- Read the full plan to understand scope and task count

**Verify plan structure:**
- Each task should have clear, actionable steps
- Tasks should reference exact file paths
- Tasks should be ordered logically (dependencies first)

### Step 2: Batch Tasks

**Group tasks into batches of 3-5:**
- Batch 1: Tasks 1-3 (usually setup/foundation)
- Batch 2: Tasks 4-6 (core functionality)
- Batch 3: Tasks 7-9 (integration/polish)
- Batch 4: Task 10+ (testing/final)

**Respect logical boundaries:**
- Don't split dependent tasks across batches
- Complete a feature/module before batching
- If a task is large, it may be its own batch

**Announce the batching plan:**
```
I'll execute this plan in 4 batches:
- Batch 1 (tasks 1-3): File structure and basic loading
- Batch 2 (tasks 4-6): Core CRUD operations
- Batch 3 (tasks 7-9): CLI interface and routing
- Batch 4 (task 10): Testing and validation

Starting with batch 1...
```

### Step 3: Execute Batch (Using sessions_spawn)

**For each task in the batch:**

1. **Spawn fresh subagent for task execution:**
   ```
   sessions_spawn --label "task-N-<short-desc>" --prompt "Execute task N from plan..."
   ```

2. **Provide clear context:**
   - Task number and description
   - Exact file paths to create/modify
   - Expected outcome
   - Commands to run

3. **Isolate task execution:**
   - Fresh subagent = no context pollution
   - Each task starts clean
   - Errors are contained to one task

4. **Capture output:**
   - Did the task complete successfully?
   - Were there errors or warnings?
   - What files were created/modified?

### Step 4: Review Batch Outputs

**After batch completes, review:**

- ✅ **Success checks:**
  - All files created as expected?
  - Commands executed without errors?
  - Tests pass (if applicable)?

- ⚠️ **Warning signs:**
  - Any error messages?
  - Unexpected file changes?
  - Dependencies missing?

- 🛑 **Stop conditions:**
  - Critical error occurred
  - Next batch depends on fixing current issue
  - User needs to make a decision

**Document findings:**
```
Batch 1 complete (tasks 1-3):
✅ Created /workspace/todo/lib/storage.js
✅ Created /workspace/todo/lib/todo.js
⚠️  Warning: Missing dependency 'fs-extra' - need to install
```

### Step 5: Checkpoint

**Mandatory pause between batches:**

1. **Report batch results** (as shown above)

2. **Ask explicit checkpoint question:**
   ```
   Continue to batch 2 (tasks 4-6)?
   ```

3. **Wait for user response:**
   - ✅ "Yes" / "Continue" / "Go ahead" → Proceed
   - 🛑 "No" / "Wait" / "Pause" → Stop and wait
   - 🔧 User provides corrections → Apply, then ask again

**If user says "just do it all, no interruptions":**
- **DO NOT skip checkpoints**
- Response: "Checkpoints aren't interruptions - they catch errors early. I'll notify you after each batch so you can review progress or let me continue."

**Auto-continue option:**
If user says "auto-continue if no errors":
- Still show batch results
- Only pause if errors/warnings detected
- User can interrupt at any checkpoint

### Step 6: Update Memory

**After each batch, log to daily memory:**

File: `workspace/memory/YYYY-MM-DD.md`

```markdown
## Executing <Topic> Plan (HH:MM)

**Batch 1 (tasks 1-3):** ✅ Complete
- Created file structure
- Implemented storage layer
- Basic todo object

**Batch 2 (tasks 4-6):** 🔄 In progress
- Add todo functionality complete
- List todos in progress
```

**Why this matters:**
- Progress is resumable if interrupted
- Daily log shows work accomplished
- Future sessions can reference what was done

### Step 7: Repeat

**Continue with next batch:**
- Execute batch (Step 3)
- Review outputs (Step 4)
- Checkpoint (Step 5)
- Update memory (Step 6)
- Repeat until all tasks complete

**Final report:**
```
✅ All 10 tasks complete!

Summary:
- Batch 1: File structure ✅
- Batch 2: CRUD operations ✅
- Batch 3: CLI interface ✅
- Batch 4: Testing ✅

Full details in workspace/memory/2026-02-25.md
```

---

## OpenClaw-Specific Integration

### sessions_spawn Usage

**Spawn fresh subagent per task:**
```bash
sessions_spawn --label "task-3-storage-layer" --prompt "
Execute task 3 from /workspace/docs/plans/2026-02-25-todo-plan.md:

Create /workspace/todo/lib/storage.js with:
- loadTodos() function
- saveTodos() function
- Use fs.readFileSync/writeFileSync
- Store in ~/.todos.json

Return the complete file content.
"
```

**Benefits:**
- Isolation: Each task has fresh context
- Clarity: No pollution from previous tasks
- Debugging: Easy to identify which task failed

### Workspace Paths

**Plans location:** `/workspace/docs/plans/`
**Memory location:** `/workspace/memory/YYYY-MM-DD.md`
**Project files:** `/workspace/<project-name>/`

Always use full paths when spawning subagents - no relative path confusion.

### Memory Integration

**Check recent context:**
Before starting, read:
- `MEMORY.md` (if main session)
- `memory/YYYY-MM-DD.md` (today's log)
- `memory/YYYY-MM-DD.md` (yesterday, if relevant)

**Update progress incrementally:**
Don't wait until the end - update after each batch so progress is trackable.

---

## Rationalization Table

These excuses will try to convince you to skip batching. Here's why they're wrong:

| Excuse | Reality | Counter |
|--------|---------|---------|
| "User doesn't want interruptions" | Checkpoints ≠ interruptions | Checkpoints are for **safety**, not annoyance. They prevent compounding errors. |
| "More efficient to do it all at once" | Efficiency without safety = rework | **Batching catches errors early.** Fixing task 3 is easier than unwinding tasks 3-10. |
| "Plan is clear, don't need checkpoints" | Clear plan ≠ error-free execution | **Errors happen during execution**, not planning. Code has bugs, dependencies fail, paths are wrong. |
| "Notify at the end" | By the end, errors have compounded | **Early notification prevents cascading failures.** If task 3 fails, tasks 4-10 may be wasted work. |
| "User said 'no updates'" | User said "no updates," not "no safety" | Interpret as "don't spam me," not "skip all checkpoints." Batch updates (not per-task spam). |
| "It's only 10 tasks, not that many" | 10 tasks = 10 opportunities for failure | Even 5 tasks can compound errors. **Batching scales to plan size.** |
| "I'll rollback if there's an error" | Rollback wastes time | **Prevention > cleanup.** Catch errors at task 3, don't discover them at task 10. |

---

## 🚩 Red Flags - When You're Rationalizing

**You're about to violate this skill if you think:**

- "I'll just execute all the tasks and report at the end"
- "The user seems impatient, I'll skip checkpoints"
- "Batching is overkill for a simple plan"
- "I'll notify them if something goes wrong"
- "Checkpoints will slow me down"
- "The plan is well-written, nothing will fail"

**If you catch yourself thinking any of these, STOP and re-read the Hard Gates.**

---

## Why This Skill Exists

**Without batching and checkpoints:**
- Task 3 fails silently
- Tasks 4-10 execute based on wrong assumptions
- By the end, you have 8 broken tasks instead of 1
- User has to untangle a mess instead of fixing one issue

**With batching and checkpoints:**
- Task 3 fails, batch 1 reports it
- User fixes task 3 or adjusts plan
- Batch 2 starts from a known-good state
- Errors are caught early, fixed cheaply

**The goal:** Controlled execution with early feedback, not all-or-nothing gambling.

---

## Summary

1. **Load plan** from `workspace/docs/plans/YYYY-MM-DD-<topic>-plan.md`
2. **Batch tasks** into groups of 3-5
3. **Execute batch** using `sessions_spawn` per task
4. **Review outputs** for errors/warnings
5. **Checkpoint** - ask "Continue to next batch?"
6. **Update memory** - log progress to `workspace/memory/YYYY-MM-DD.md`
7. **Repeat** until all batches complete

**Remember:** Checkpoints are safety, not annoyance. Batching catches errors early. Execution isn't a race - it's a controlled process.
