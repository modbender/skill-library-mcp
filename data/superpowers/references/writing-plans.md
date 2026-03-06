# Writing Plans Reference

Source: obra/superpowers writing-plans skill

## Overview

Write a detailed implementation plan before touching code. Each task must be granular enough
for an agent with no project context to execute correctly.

Announce at start: "I'm using the writing-plans skill to create the implementation plan."

## Plan File Location

`docs/plans/YYYY-MM-DD-<feature-name>.md`

## Plan Document Header (required)

```markdown
# [Feature Name] Implementation Plan

> **For implementer:** Use TDD throughout. Write failing test first. Watch it fail. Then implement.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2–3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Granularity

Each step = one action, 2–5 minutes:

```markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py`
- Test: `tests/exact/path/to/test_file.py`

**Step 1: Write the failing test**
[paste exact test code]

**Step 2: Run test — confirm it fails**
Command: `pytest tests/path/test.py::test_name -v`
Expected: FAIL — "function not defined" or similar

**Step 3: Write minimal implementation**
[paste exact implementation code]

**Step 4: Run test — confirm it passes**
Command: `pytest tests/path/test.py::test_name -v`
Expected: PASS

**Step 5: Commit**
`git add <files> && git commit -m "feat: <description>"`
```

## Rules

- Exact file paths always — no vague references
- Complete code in plan — not "add validation here"
- Exact commands with expected output
- DRY, YAGNI, TDD, frequent commits after each green test

## Execution Handoff

After saving plan, offer:

> "Plan saved to `docs/plans/<filename>.md`. Two execution options:
>
> 1. **Subagent-Driven** — I dispatch a fresh sub-agent per task, review between tasks
> 2. **Manual** — You run the tasks yourself
>
> Which approach?"

If Subagent-Driven: proceed to subagent-development phase.
