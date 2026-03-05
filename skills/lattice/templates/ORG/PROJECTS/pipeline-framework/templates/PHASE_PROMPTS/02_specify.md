# Phase 2: Specify

You are executing Pipeline Phase 2: Specify for project `<project>`.

## Goal
Define precise requirements and acceptance criteria based on research results. This is the authoritative definition of "what to do"; subsequent implementation and testing will strictly follow this.

## Files You Need to Read
- `ORG/PROJECTS/<project>/pipeline/CONSTITUTION.md` (Project principles and constraints)
- `ORG/PROJECTS/<project>/pipeline/RESEARCH.md` (Research report)

## Files You Need to Produce
Write to path: `ORG/PROJECTS/<project>/pipeline/SPECIFICATION.md`

Must include the following sections:
1. **Functional Requirements List** (Each requirement has a unique ID, e.g., FR-001, and is testable)
2. **Non-functional Requirements** (Performance, reliability, maintainability, compatibility)
3. **Interface Definitions** (Input/output formats, API contracts, data structures)
4. **Acceptance Criteria** (Each functional requirement corresponds to at least one acceptance condition, format: Given/When/Then or equivalent)
5. **Exclusions** (Explicitly what NOT to do, aligned with CONSTITUTION.md boundary constraints)

## Completion Criteria
- SPECIFICATION.md exists and is not empty
- Each functional requirement has corresponding acceptance criteria
- Requirements do not contradict CONSTITUTION.md constraints
- Requirements are consistent with RESEARCH.md recommended direction

## Constraints
- Do not modify CONSTITUTION.md or RESEARCH.md
- Do not modify system config/gateway
- Output must be written to the specified path
- Output a brief summary (3-5 lines) upon completion

## If Review Feedback Exists
(Orchestrator will inject feedback from REVIEW_REPORT.md here, if any)
<review_feedback>
None
</review_feedback>
