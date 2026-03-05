---
name: subagent-driven-development
description: Execute implementation plans by dispatching one subagent per task with structured review between each — fresh context, no pollution
---

# Subagent-Driven Development — Spawn, Review, Repeat

## When to Use

Use when you have a written plan and need to execute it task by task using subagents.

## Core Principle

One subagent per task + structured review after each = high quality, no context pollution.

## Process

### For Each Task in the Plan:

#### 1. Spawn Subagent with Full Context

Provide the subagent with everything it needs upfront:

```
TASK: [Task title]

WHAT: [Exact description of what to build]

WHY: [Context — how this fits into the larger feature]

FILES:
- Create: [exact paths]
- Modify: [exact paths]

CODE:
[Complete code from the plan]

TESTING:
- Write failing test first (craftwork:test-driven-development)
- Run: [exact test command]
- Expected: PASS

CONSTRAINTS:
- [Project-specific constraints]
- [Security requirements]
- [Pattern compliance]

WHEN DONE:
1. Create MR/PR with descriptive title
2. Update task status to "review"
3. Report completion with verification evidence (craftwork:verification-before-completion)
```

#### 2. Review the Output

After subagent reports completion, review the diff using `craftwork:requesting-code-review`:

- [ ] Matches plan specification (nothing more, nothing less)
- [ ] Tests exist and cover the feature
- [ ] No hardcoded secrets
- [ ] No breaking changes
- [ ] Code is clean and follows existing patterns

#### 3. Approve or Request Fixes

**If approved:**
- Merge the MR/PR
- Mark task as done
- Move to next task

**If issues found:**
- Post specific feedback with file:line references
- Re-spawn subagent with fix instructions
- Do NOT skip the re-review after fixes

#### 4. Move to Next Task

Only after current task is merged and verified. Never skip ahead.

## Red Flags

- Never spawn multiple subagents on dependent tasks simultaneously
- Never skip review (even if subagent self-reviewed)
- Never proceed with unfixed issues
- Never merge without reading the diff
- Never let subagent read the plan file — provide full text instead
