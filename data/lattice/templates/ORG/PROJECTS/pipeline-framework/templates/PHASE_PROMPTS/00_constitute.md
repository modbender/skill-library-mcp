# Phase 0: Constitute

You are executing Pipeline Phase 0: Constitute for project `<project>`.

## Goal
Define project principles, technical constraints, and quality standards. This is the cornerstone of the entire Pipeline; all subsequent phases will refer to this file.

## Files You Need to Read
- `ORG/PROJECTS/<project>/STATUS.md` (Current project status)
- `ORG/PROJECTS/<project>/DECISIONS.md` (Existing decisions)
- `ORG/DEPARTMENTS/<dept>/CHARTER.md` (Department responsibilities and boundaries)
- Existing docs in project repo (e.g., README, REPORT, etc.)
- Previous run's archived `ORG/PROJECTS/<project>/pipeline_archive/run-{N-1}/GAP_ANALYSIS.md` (if exists — contains improvement suggestions and deferred tasks)
- Previous run's archived `ORG/PROJECTS/<project>/pipeline_archive/run-{N-1}/DEFERRED_TASKS.json` (if exists — tasks deferred by Auto-Triage in the previous run)

## ⚠️ Previous Run Deferred Tasks
If the previous run's archive contains `DEFERRED_TASKS.json`, you must:
1. Read each deferred task's description and deferral reason
2. In CONSTITUTION.md's "Project Goal" section or a new "Carry-Over Tasks" section, explicitly mention these tasks
3. Ensure these tasks are not forgotten in this run — they should be re-incorporated during the Plan+Tasks phase

## Files You Need to Produce
Write to path: `ORG/PROJECTS/<project>/pipeline/CONSTITUTION.md`

Must include the following sections:
1. **Project Goal** (1-3 sentences, clearly stating what to achieve)
2. **Tech Stack Constraints** (Languages, frameworks, dependency limits, runtime environment)
3. **Quality Standards** (Test coverage requirements, performance metrics, documentation requirements)
4. **Boundary Constraints** (What NOT to do, security red lines, resource limits)
5. **Alignment Statement with ORG Charter** (Confirm adherence to Boot/Closeout/Persistence/Change Control)

## Completion Criteria
- CONSTITUTION.md exists and is not empty
- Contains all 5 sections above
- Each section has at least 2 specific items

## Constraints
- Do not modify system config/gateway
- Output must be written to the specified path
- Output a brief summary (3-5 lines) upon completion
