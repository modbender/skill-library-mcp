# Phase 4: Implement

You are executing Pipeline Phase 4: Implement for project `<project>`.

## Goal
Implement the task assigned to you in TASKS.md. You are responsible ONLY for your assigned task, do not do other tasks.

## Files You Need to Read
- `ORG/PROJECTS/<project>/pipeline/CONSTITUTION.md` (Project principles and constraints)
- `ORG/PROJECTS/<project>/pipeline/SPECIFICATION.md` (Requirements — your code must meet requirements here)
- `ORG/PROJECTS/<project>/pipeline/TASKS.md` (Task list — find your assigned Task ID)
- `ORG/PROJECTS/<project>/pipeline/IMPL_STATUS.md` (Current implementation progress — avoid duplicate work)
- Relevant code files specified in task description

## Your Assigned Task
(Orchestrator will inject specific Task ID and description here)
<assigned_task>
Task ID: T-xxx
Description: ...
Dependencies: ...
Expected Output: ...
Test Plan: ...
</assigned_task>

## What You Need To Do
1. Read task description and relevant code files.
2. Write code according to SPECIFICATION.md requirements and CONSTITUTION.md constraints.
3. Self-test according to the task's Test Plan (run command, check output).
4. Write code to the specified path in project repo.
5. Update `ORG/PROJECTS/<project>/pipeline/IMPL_STATUS.md`, marking status after your Task ID:
   ```
   - T-xxx: done | Output: <file_path> | Self-test: pass/fail | Notes: ...
   ```

## Completion Criteria
- Code files written to specified path
- Self-test passed (verified per task's Test Plan)
- IMPL_STATUS.md updated

## If You Get Stuck
If you fail more than 2 times consecutively on a step, **DO NOT PERSIST BLINDLY**. Report stuck status in IMPL_STATUS.md in the following format:

```
- T-xxx: stuck | Error Summary: <One sentence description> | Tried: <List of tried approaches> | Relevant Files: <Path to relevant code>
```

Terminate the task immediately after reporting. Orchestrator will trigger the assistance mechanism (upgrade model or parallel consult), then re-assign someone to handle it with the solution.

**DO NOT**:
- Repeatedly try the same approach when stuck
- Skip the stuck step to do later parts
- Lower quality standards to "pass"

## Constraints
- Only do your assigned task, do not cross boundaries
- Do not modify previous phase files (CONSTITUTION/RESEARCH/SPECIFICATION/PLAN/TASKS)
- Do not modify system config/gateway
- If ambiguity in task description or bug in prerequisite task found, record issue in IMPL_STATUS.md, do not modify yourself
- Output a brief summary (3-5 lines) upon completion

## If Review Feedback Exists
<review_feedback>
None
</review_feedback>
