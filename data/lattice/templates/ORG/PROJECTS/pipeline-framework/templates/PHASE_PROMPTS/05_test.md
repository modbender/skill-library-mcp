# Phase 5: Test

You are executing Pipeline Phase 5: Test for project `<project>`.

## Goal
Perform tiered testing on Phase 4 implementation and generate a test report. The authoritative standard for testing is the acceptance criteria in SPECIFICATION.md.

## Files You Need to Read
- `ORG/PROJECTS/<project>/pipeline/CONSTITUTION.md` (Quality standards)
- `ORG/PROJECTS/<project>/pipeline/SPECIFICATION.md` (Acceptance criteria — verify item by item)
- `ORG/PROJECTS/<project>/pipeline/TASKS.md` (Test plan for each task)
- `ORG/PROJECTS/<project>/pipeline/IMPL_STATUS.md` (Implementation status — which tasks are done, output paths)
- Code files in project repo

## Testing Tiers

### Level 1: Unit Test
- Execute test plan defined in TASKS.md for each task
- Record pass/fail for each task

### Level 2: Integration Test
- Test interfaces and data flow across tasks
- Verify correct interaction between modules

### Level 3: Acceptance Test
- Verify against SPECIFICATION.md acceptance criteria item by item
- Execute verification for each FR-xxx
- Record pass/fail/skip (must explain reason for skip)

## Files You Need to Produce
Write to path: `ORG/PROJECTS/<project>/pipeline/TEST_REPORT.md`

Must include the following sections:
1. **Test Execution Summary**
   - Total / Pass / Fail / Skip
   - Statistics by Level (Unit / Integration / Acceptance)
2. **Unit Test Details**
   - Each Task ID + Test Command + Result + Output Summary
3. **Integration Test Details**
   - Test Scenario + Result + Issue Description (if any)
4. **Acceptance Test Details**
   - Each FR-xxx + Acceptance Condition + pass/fail/skip + Evidence (Command output or screenshot path)
5. **Failure Analysis**
   - Root cause analysis and fix suggestions for each failure case
6. **Test Coverage** (If applicable)
   - Code coverage data or estimation

## Completion Criteria
- TEST_REPORT.md exists and is not empty
- All tasks in TASKS.md have unit test results
- All FR-xxx in SPECIFICATION.md have acceptance test results
- Acceptance test pass rate >= Threshold (Default 80%, subject to CONSTITUTION.md quality standards)

## If You Get Stuck
When encountering unresolvable test environment issues (dependency failure, environment incompatibility, etc.), or a test fails repeatedly and you cannot determine if it's a code bug or test plan issue, **DO NOT PERSIST BLINDLY**. Mark in TEST_REPORT.md:

```
### Stuck Items
- Test Item: <FR-xxx or T-xxx> | Error Summary: <One sentence> | Tried: <List of tried approaches> | Relevant Files: <Path>
```

Terminate task immediately after reporting. Orchestrator will automatically trigger assistance mechanism.

## Constraints
- Do not modify code files (Read-only during test phase, only run tests)
- Do not modify previous phase pipeline files
- Do not modify system config/gateway
- If environment issues prevent execution of certain tests, mark as skip and explain reason
- Output a brief summary (3-5 lines) upon completion
