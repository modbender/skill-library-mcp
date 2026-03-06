# Subagent-Driven Development Reference

Source: obra/superpowers subagent-driven-development skill
Adapted for OpenClaw (sessions_spawn instead of Claude Code Task tool)

## Core Principle

Fresh sub-agent per task + two-stage review (spec then quality) = high quality, fast iteration.

## OpenClaw Dispatch Pattern

Use `sessions_spawn` for each role. Pass a structured prompt:

```
GOAL: [one sentence — what outcome]
CONTEXT: [plan file path + relevant background]
FILES: [specific paths to touch]
CONSTRAINTS: [TDD mandatory, no scope creep, no untested code]
VERIFY: [test command + expected output]
TASK: [paste full task text from plan doc]
```

## Per-Task Loop

For each task in the plan:

1. **Dispatch implementer sub-agent** via `sessions_spawn`
   - Include: full task text, plan file path, TDD constraint
   - Wait for completion announcement

2. **Dispatch spec-reviewer sub-agent** via `sessions_spawn`
   - Include: what was implemented, plan requirements, git diff
   - Must confirm: code matches spec exactly
   - If gaps found → dispatch implementer again to fix

3. **Dispatch code-quality reviewer sub-agent** via `sessions_spawn`
   - Include: git diff, description of implementation
   - Must approve: clean code, no dead code, DRY, YAGNI
   - If issues found → dispatch implementer to fix, re-review

4. Mark task complete, move to next task

## After All Tasks Complete

1. Dispatch final overall reviewer sub-agent (full diff, all tasks)
2. Fix any critical/important issues found
3. Hand off to finishing-branch phase

## Implementer Sub-Agent Prompt Template

```
You are implementing a coding task. Follow TDD strictly.

PLAN FILE: [path]
TASK: [task N text verbatim]

CONSTRAINTS:
- Write failing test FIRST. Run it. Confirm it fails. Then implement.
- Minimal implementation only — YAGNI
- Commit after each green test: git add <files> && git commit -m "..."
- Do NOT change files outside this task's scope
- Do NOT add features not in the task

VERIFY:
- Run: [test command]
- Expected: [expected output]

Report when done: what you implemented, test results, commit SHA.
```

## Spec-Reviewer Sub-Agent Prompt Template

```
You are reviewing code for spec compliance only.

PLAN FILE: [path]
TASK BEING REVIEWED: [task N text]
GIT RANGE: [base_sha..head_sha]

Review ONLY whether the implementation matches the spec.
Report:
- PASS or FAIL
- Any spec gaps (what was specified but not implemented)
- Do NOT comment on code style or quality
```

## Code-Quality Reviewer Sub-Agent Prompt Template

```
You are reviewing code quality only (not spec compliance).

GIT RANGE: [base_sha..head_sha]
DESCRIPTION: [what was implemented]

Review for:
- DRY violations
- Dead code
- YAGNI violations (unnecessary features)
- Poor naming
- Missing error handling

Severity: Critical / Important / Minor
Report: approve or list issues by severity.
```

## Review Severity Actions

| Severity | Action |
|----------|--------|
| Critical | Fix before proceeding — blocks next task |
| Important | Fix before proceeding |
| Minor | Note, address later |
