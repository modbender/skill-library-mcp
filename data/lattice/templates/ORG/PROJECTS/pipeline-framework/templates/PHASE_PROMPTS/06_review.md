# Phase 6: Review

You are executing Pipeline Phase 6: Review for project `<project>`.

## Goal
Perform quality review and goal achievement analysis on the entire Pipeline run output. Your verdict (PASS/FAIL) determines whether the Pipeline archives and completes, or rolls back for rework.

## Files You Need to Read (All)
- `ORG/PROJECTS/<project>/pipeline/CONSTITUTION.md` (Project principles and quality standards)
- `ORG/PROJECTS/<project>/pipeline/RESEARCH.md` (Research report)
- `ORG/PROJECTS/<project>/pipeline/SPECIFICATION.md` (Requirements specification and acceptance criteria)
- `ORG/PROJECTS/<project>/pipeline/PLAN.md` (Implementation plan)
- `ORG/PROJECTS/<project>/pipeline/TASKS.md` (Task list)
- `ORG/PROJECTS/<project>/pipeline/IMPL_STATUS.md` (Implementation status)
- `ORG/PROJECTS/<project>/pipeline/TEST_REPORT.md` (Test report)
- `ORG/PROJECTS/<project>/PIPELINE_STATE.json` (Check `deferredTasks` and `stuckInfo.triageResult` fields)
- Code files in project repo (Spot check key modules)

## ⚠️ RELAX/DEFER Review (Important)
If PIPELINE_STATE.json contains the following records, you must perform additional review:

**Deferred Tasks** (`deferredTasks` field):
- Were the tasks deferred by Auto-Triage truly deferrable?
- After deferring these tasks, does this run's deliverable still have practical value?
- If deferred tasks exceed 50% of total tasks, consider judging FAIL

**Relaxed Constraints** (`stuckInfo.triageResult.decision == "RELAX"`):
- Were the relaxed constraints reasonable? Was the degree of relaxation excessive?
- Is the output quality after relaxation still acceptable?
- If critical constraints were relaxed, deduct points in scoring and clearly note in the report

## Review Dimensions

### 1. Spec Compliance (Weight 30%)
- Does code meet all functional requirements in SPECIFICATION.md?
- Are non-functional requirements met?
- Are interface definitions consistent?

### 2. Quality Standards (Weight 25%)
- Are quality standards defined in CONSTITUTION.md met?
- Are code style, naming, structure reasonable?
- Are there obvious bugs, security vulnerabilities, performance issues?

### 3. Test Sufficiency (Weight 20%)
- Does TEST_REPORT.md cover all critical paths?
- Is acceptance test pass rate up to standard?
- Is root cause analysis for failure cases reasonable?

### 4. Maintainability (Weight 15%)
- Are comments and documentation sufficient?
- Is module division clear?
- Is future iteration easy to extend?

### 5. Goal Achievement (Weight 10%)
- Is the project goal defined in CONSTITUTION.md achieved overall?
- Are key functions missing?

## Files You Need to Produce
Write to path: `ORG/PROJECTS/<project>/pipeline/REVIEW_REPORT.md`

Must include the following sections:
1. **Review Summary** (One paragraph summary)
2. **Scores by Dimension**
   ```
   Spec Compliance:  X/5
   Quality Standards:    X/5
   Test Sufficiency:  X/5
   Maintainability:    X/5
   Goal Achievement:    X/5
   Weighted Total:    X.X/5.0
   ```
3. **Overall Verdict**: `PASS` or `FAIL`
   - PASS Condition: Weighted Total >= 3.5 AND No Dimension <= 2
   - Otherwise FAIL
4. **If PASS**:
   - Highlights of this run (2-3 items)
   - Improvement directions for next run
5. **If FAIL**:
   - Specific Issue List (Each with file/line number)
   - Suggested Rollback Phase (constitute/research/specify/plan/implement/test)
   - Reason for Rollback
   - Specific Modification Suggestions for the rollback phase

## Completion Criteria
- REVIEW_REPORT.md exists and is not empty
- Contains scores for 5 dimensions
- Contains clear PASS/FAIL verdict
- If FAIL, contains rollback target and specific modification suggestions

## Constraints
- Do not modify any pipeline files or code files (You are a reviewer, not a modifier)
- Do not modify system config/gateway
- Remain objective and fair, do not "let it pass" just because it's "almost there"
- Output a brief summary (3-5 lines) upon completion
