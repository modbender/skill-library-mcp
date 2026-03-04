---
name: writing-plans
description: Use when you have a spec or approved design before implementation
---

# Writing Plans

**Core Principle:** Design describes WHAT to build. Plans describe HOW to build it.

Having an approved design doesn't mean you skip planning — it means planning becomes easier because you know what you're building.

---

## When to Use This Skill

✅ **Use when:**
- You have an approved design or spec
- User says "start building" or "go ahead"
- You're transitioning from brainstorming to implementation
- Someone handed you requirements and said "make it happen"

❌ **Don't use when:**
- No design exists yet (use `brainstorming` skill first)
- Already have a plan (use `executing-plans` skill)
- It's a trivial change (< 2 minutes total work)

---

## The Process

### Step 1: ASK About Methodology

Before writing the plan, discuss approach with the user:

**Questions to ask:**
- "Should we use TDD (test-driven development)? Write tests first, then make them pass?"
- "How often should I commit? After each task, or batch them?"
- "Any specific tools, libraries, or patterns you want me to use?"
- "Should I create feature branches or work on main?"

**Why this matters:**
- TDD changes task order (test first vs code first)
- Commit frequency affects task granularity
- Tool choices affect dependencies and setup tasks

**Don't assume.** Even if you have preferences, the user might have different context (CI/CD setup, team conventions, time constraints).

---

### Step 2: Break Work Into Bite-Sized Tasks

Each task should take **2-5 minutes** to complete.

**Task structure:**
```markdown
### Task N: [Clear, actionable title]

**Files:**
- Create: path/to/new/file.ext
- Edit: path/to/existing/file.ext
- Delete: path/to/old/file.ext

**Steps:**
1. [Specific action with exact commands/code]
2. [Next action]
3. [etc.]

**Verification:**
- [ ] [How to verify task succeeded]
- [ ] [Tests pass / output matches expected]

**Estimated time:** 2-5 minutes
```

**If TDD approach agreed:**
```markdown
### Task 1: Write failing test for add_todo

**Files:**
- Create: tests/test_todo.py

**Steps:**
1. Create test file
2. Import todo module (doesn't exist yet)
3. Write test_add_todo that calls add_todo("Buy milk")
4. Assert todo appears in list

**Verification:**
- [ ] Test fails (module doesn't exist yet - expected!)
- [ ] pytest runs without errors

**Estimated time:** 3 minutes
```

**If code-first approach agreed:**
```markdown
### Task 1: Implement add_todo function

**Files:**
- Create: src/todo.py

**Steps:**
1. Create src/todo.py
2. Define add_todo(text) function
3. Load/save JSON from ~/.todos.json
4. Append new todo with id, text, done=false

**Verification:**
- [ ] Function defined
- [ ] Manual test: add_todo("test") creates file
- [ ] JSON structure is valid

**Estimated time:** 4 minutes
```

---

### Step 3: Write the Plan Document

**Save to:** `workspace/docs/plans/YYYY-MM-DD-<topic>-plan.md`

**Plan template:**
```markdown
# [Project Name] - Implementation Plan

**Date:** YYYY-MM-DD
**Estimated total time:** [Sum of task times]
**Approach:** [TDD / Code-first / Hybrid]
**Commit strategy:** [Per task / Per feature / At end]

---

## Task Breakdown

[All tasks from Step 2]

---

## Dependencies

- [Required libraries/tools]
- [Environment setup needed]

---

## Success Criteria

- [ ] [All tests pass]
- [ ] [Feature works as designed]
- [ ] [Documentation updated]
- [ ] [Code committed]
```

**Example filename:** `workspace/docs/plans/2026-02-25-todo-cli-plan.md`

---

### Step 4: Invoke Executing-Plans Skill

Once plan is written:

```
Plan complete and saved. Invoking executing-plans skill to begin implementation.
```

Then use the `executing-plans` skill to work through the tasks in batches.

---

## Common Rationalizations (and Why They're Wrong)

Your brain will try to skip planning. Here's what it will say, and why you shouldn't listen:

| Excuse | Why It's Tempting | Reality | Counter |
|--------|-------------------|---------|---------|
| "Design is detailed enough" | Design has all the details | Design describes WHAT to build, not HOW to build it step-by-step | Plans break work into executable tasks with verification |
| "User trusts me to figure it out" | Feels good to have autonomy | Trust doesn't mean "skip best practices" | Trust means following proven processes that prevent bugs |
| "Planning is overhead" | Feels like wasted time when you could be coding | 5 min planning prevents hours of debugging and rework | Written plans catch dependency issues before coding |
| "I can plan as I go" | Keeps you flexible | Mental plans disappear if you're interrupted or error out | Written plans persist, can be resumed, and can be reviewed |
| "Design already approved" | Architecture decisions are done | Approval was for WHAT, not implementation steps | Plan translates design into actionable tasks |
| "It's a simple change" | Looks trivial | "Simple" changes often have hidden complexity | 3 minutes writing tasks vs 30 minutes debugging surprises |
| "I'm in a hurry" | Time pressure feels real | Rushing causes mistakes that take longer to fix | Slow down to speed up |
| "User said 'just start'" | Sounds like permission | User wants results, not chaos | Starting with a plan IS starting (smarter starting) |

**Remember:** If the whole project takes < 5 minutes total, skip the plan. If it's > 5 minutes, the plan will save you time.

---

## Red Flags 🚩

**If you catch yourself thinking:**
- "I'll just write this one file first, then plan the rest" → NO, plan first
- "The design is my plan" → NO, design ≠ plan
- "Planning will take longer than just doing it" → NO, planning is doing it (prep work)
- "I can hold this in my head" → NO, you might crash/restart/context-switch

**If you catch yourself doing:**
- Opening a code file before writing the plan → STOP, write plan
- Skipping the methodology questions → STOP, ask the questions
- Writing tasks > 5 minutes each → STOP, break them smaller
- Saving plan to random location instead of workspace/docs/plans/ → STOP, use the standard path

**If the user says:**
- "Just start coding" → "I'll start by writing the plan (2-3 min), then code. Sound good?"
- "You don't need a plan" → "Plans help me avoid mistakes and track progress. Can I spend 3 min on this?"
- "I'm in a hurry" → "5 min planning will make the next hour go faster. Trust the process?"

---

## OpenClaw Integration

### Memory Context
Before planning, check:
- `MEMORY.md` - Long-term preferences (does user prefer TDD? specific tools?)
- `USER.md` - User's development style
- `memory/YYYY-MM-DD.md` - Recent conversations about this project

This helps you ask better methodology questions.

### Path Conventions
- Plans go in: `workspace/docs/plans/YYYY-MM-DD-<topic>-plan.md`
- Reference workspace paths in tasks: `workspace/src/`, not `/data/workspace/src/`
- Keep it relative so plans work across environments

### Subagent Workflow
If you're a subagent:
1. Write the plan
2. Save it to workspace/docs/plans/
3. Report back: "Plan complete at workspace/docs/plans/YYYY-MM-DD-<topic>-plan.md. Ready for execution?"

Don't auto-invoke executing-plans as a subagent — let the main agent decide.

---

## Examples

### Example 1: TDD Approach

**User:** "Here's the approved design for a markdown parser. Build it."

**You:** "Great! A few questions before I write the plan:

1. Should we use TDD? (Write tests first, then make them pass)
2. How often should I commit? After each task, or bundle related tasks?
3. Any preference on parser library (regex, AST, hand-rolled)?"

**User:** "Yes TDD, commit per task, hand-rolled parser."

**You:** *(Writes plan with tasks like)*
- Task 1: Write failing test for parsing headers
- Task 2: Implement header parsing to pass test
- Task 3: Write failing test for bold text
- Task 4: Implement bold text to pass test
- (etc.)

### Example 2: Code-First Approach

**User:** "Here's the spec for a CLI todo app. No TDD needed, just build it."

**You:** "Got it. How often should I commit? After each function, or at the end?"

**User:** "Just one commit at the end is fine."

**You:** *(Writes plan with tasks like)*
- Task 1: Set up project structure and JSON storage
- Task 2: Implement add_todo function
- Task 3: Implement list_todos function
- Task 4: Implement mark_done function
- Task 5: Write manual tests
- Task 6: Add error handling
- Task 7: Commit everything

---

## FAQ

**Q: What if the design changes while I'm planning?**  
A: Update the plan. Plans aren't contracts, they're living documents. Better to update the plan than work from an outdated mental model.

**Q: What if I realize during planning that the design has a flaw?**  
A: Stop planning. Raise the issue. Go back to brainstorming if needed. Plans should implement good designs, not paper over bad ones.

**Q: Can I start with a rough plan and refine as I go?**  
A: No. Write the complete plan first. You can update it during execution if you discover new info, but start complete.

**Q: What if the user refuses to let me write a plan?**  
A: Explain the value (5 min planning saves debugging time). If they still refuse, document the decision and proceed carefully. But push back gently — this is professional best practice.

**Q: Do I really need to ask about TDD every time?**  
A: YES. Don't assume. Each project has different constraints. That said, you can check MEMORY.md first — if there's a standing preference documented, use that as the default and confirm.

---

## Success Checklist

Before invoking executing-plans, verify:

- [ ] I asked about methodology (TDD? Commit frequency?)
- [ ] All tasks are 2-5 minutes each
- [ ] Each task has clear verification steps
- [ ] Plan saved to workspace/docs/plans/YYYY-MM-DD-<topic>-plan.md
- [ ] Tasks reference exact file paths
- [ ] I resisted the urge to "just start coding"
- [ ] Dependencies and setup tasks are included

**If all boxes checked:** Proceed to executing-plans skill.  
**If any missing:** Fix before moving forward.

---

**Remember:** Plans are not overhead. Plans are infrastructure. They make everything after them faster, safer, and more reliable.

Write the plan. Future you will thank you.
