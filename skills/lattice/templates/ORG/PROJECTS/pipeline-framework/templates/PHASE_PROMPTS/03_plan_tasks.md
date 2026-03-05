# Phase 3: Plan + Tasks

You are executing Pipeline Phase 3: Plan + Tasks for project `<project>`.

## Goal
Create an implementation plan and break down requirements into executable atomic tasks. Each task must be small enough to complete in a single independent session.

## Files You Need to Read
- `ORG/PROJECTS/<project>/pipeline/CONSTITUTION.md` (Project principles and constraints)
- `ORG/PROJECTS/<project>/pipeline/RESEARCH.md` (Research report)
- `ORG/PROJECTS/<project>/pipeline/SPECIFICATION.md` (Requirements specification)

## Files You Need to Produce

### File 1: `ORG/PROJECTS/<project>/pipeline/PLAN.md`
Implementation roadmap, containing:
1. **Implementation Phasing** (Phased by functional module or dependency order)
2. **Inter-phase Dependencies** (Which can be parallel, which must be serial)
3. **Technical Solution Selection** (Make final technical decisions based on RESEARCH.md recommendations)
4. **Risk Mitigation Plan** (Addressing risks identified in RESEARCH.md)

### File 2: `ORG/PROJECTS/<project>/pipeline/TASKS.md`
Atomic task list, each task containing:
- **Task ID** (T-001, T-002...)
- **Description** (One sentence clearly stating what to do)
- **Dependencies** (Which tasks must be completed first, reference by Task ID)
- **Corresponding Requirement** (Reference FR-xxx in SPECIFICATION.md)
- **Expected Output Files** (Code file paths or document paths)
- **Test Plan** (How to verify this task is done—command, assertion, or manual check item)
- **Estimated Complexity** (S: <30min / M: 30-60min / L: 60-120min)

## Completion Criteria
- PLAN.md + TASKS.md both exist and are not empty
- Every functional requirement in SPECIFICATION.md is covered by at least one task
- Every task has a test plan
- No cycles in task dependencies
- Tasks with complexity L do not exceed 30% of total (if exceeded, need further breakdown)

## Constraints
- Do not modify previous phase files
- Do not modify system config/gateway
- Output must be written to the specified path
- Output a brief summary (3-5 lines) upon completion

## If Review Feedback Exists
<review_feedback>
None
</review_feedback>
