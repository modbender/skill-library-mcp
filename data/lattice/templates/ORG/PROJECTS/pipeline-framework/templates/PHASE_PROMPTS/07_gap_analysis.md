# Phase 7: Gap Analysis

You are executing Pipeline Phase 7: Gap Analysis for project `<project>`.

## Goal
Deeply analyze the gap between current run results and final project goals, providing structured improvement directions for the next Pipeline run.
Review answers "Is this run good enough?", you answer "How to do better next run?".

## Files You Need to Read (All)
- `ORG/PROJECTS/<project>/pipeline/CONSTITUTION.md` (Project principles and final goal baseline)
- `ORG/PROJECTS/<project>/pipeline/RESEARCH.md` (Research report)
- `ORG/PROJECTS/<project>/pipeline/SPECIFICATION.md` (Requirements specification and acceptance criteria)
- `ORG/PROJECTS/<project>/pipeline/PLAN.md` (Implementation plan)
- `ORG/PROJECTS/<project>/pipeline/TASKS.md` (Task list)
- `ORG/PROJECTS/<project>/pipeline/IMPL_STATUS.md` (Implementation status)
- `ORG/PROJECTS/<project>/pipeline/TEST_REPORT.md` (Test report)
- `ORG/PROJECTS/<project>/pipeline/REVIEW_REPORT.md` (Review report — scores and highlights)
- Historical Run Archives `ORG/PROJECTS/<project>/pipeline_archive/` (If any, for cross-run comparison)
- Code files in project repo (Spot check key modules)
- `ORG/PROJECTS/<project>/PIPELINE_STATE.json` (Check `deferredTasks` field — tasks deferred by Auto-Triage this run)

## ⚠️ Deferred Task Handling (Important)
If PIPELINE_STATE.json contains `deferredTasks` in any phase, you must:
1. Add a **"Deferred Task List"** section in GAP_ANALYSIS.md
2. List each deferred task's taskId, deferral reason, and original error summary
3. For each deferred task, provide next-run handling suggestions (re-research? change approach? split into subtasks?)
4. In the "Improvement Suggestions List", mark deferred task recovery as **High Priority**

Similarly, if this run has RELAX records (stuckInfo.triageResult.decision == "RELAX"), also:
1. List all relaxed constraints and degree of relaxation
2. Recommend restoring original constraints and re-verifying in the next run

## Analysis Dimensions

### 1. Quantified Completion
- Evaluate gap between current results and CONSTITUTION.md final goals per module
- Quantify completion of each module (percentage or score)
- Clearly mark which goals achieved, partially achieved, not started

### 2. Scenario Coverage Analysis
- Which scenarios/conditions covered
- Which boundary scenarios, extreme conditions, exception paths missing
- Depth of coverage (only happy path vs edge cases)

### 3. Chart & Visualization Sufficiency
- Are existing charts sufficient to support conclusions
- Suggest new charts (Description: X-axis, Y-axis, Data Source)
- Improvement suggestions for existing charts (if needed)

### 4. Cross-Run Progress Tracking
- Compare key metrics with previous run (if archived)
- Quantify improvement magnitude (test pass rate, coverage, score changes)
- Identify stagnant or regressing areas

### 5. Next Run Improvement Suggestions
List specific executable improvement items by priority (High/Medium/Low), each containing:
- Improvement Content Description
- Reason (Why important)
- Expected Benefit (Quantified or Qualitative)
- Suggested Phase to Focus On

### 6. Quality Standard Update Suggestions
- Whether to adjust acceptance thresholds
- Whether to add new quality dimensions
- Whether CONSTITUTION.md needs update (e.g., project direction tweak)

## Files You Need to Produce
Write to path: `ORG/PROJECTS/<project>/pipeline/GAP_ANALYSIS.md`

Must include the following sections:
1. **Analysis Summary** (One paragraph summary of the gap landscape)
2. **Quantified Completion Table**
   ```
   | Module/Goal | Completion | Note |
   |-------------|------------|------|
   | ...         | XX%        | ...  |
   ```
3. **Scenario Coverage Matrix** (Covered ✅ / Partial ⚠️ / Not Covered ❌)
4. **Cross-Run Comparison** (If historical data exists)
5. **Improvement Suggestions List** (At least 3 items, sorted by priority)
   ```
   | Priority | Item | Reason | Expected Benefit | Focus Phase |
   |----------|------|--------|------------------|-------------|
   | High     | ...  | ...    | ...              | ...         |
   ```
6. **Quality Standard Update Suggestions** (If none, write "Current standards applicable, no adjustment needed")

## Completion Criteria
- GAP_ANALYSIS.md exists and is not empty
- Contains quantified completion assessment
- Contains at least 3 prioritized improvement suggestions
- Each suggestion attached with reason and expected benefit

## Constraints
- Do not modify any pipeline files or code files (You are an analyst, not a modifier)
- Do not modify system config/gateway
- Assume Review has PASSED — your task is not to re-judge, but forward-looking analysis
- Output a brief summary (3-5 lines) upon completion
