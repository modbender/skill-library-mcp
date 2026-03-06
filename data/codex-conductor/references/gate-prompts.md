# Gate Prompt Templates (Codex)

Copy/adapt these templates per gate. Keep prompts explicit and evidence-oriented.

## Common Prompt Header

```text
You are implementing Gate <GATE_ID> for this project.

Constraints:
- Follow AGENTS.md workflow rules exactly.
- Update documentation after every meaningful change.
- Run required validations and report evidence.
- Do not claim completion without test outputs.
- Do not assume requirements; if unclear, stop and ask.
- If spec reference is missing for implementation work, return BLOCKED and do not code.

Output contract (mandatory):
- STATUS: DONE | BLOCKED
- TASK: <single task>
- SPEC_REF: <reference or BLOCKED reason>
- FILES_CHANGED: <list>
- VALIDATION_RUN: <commands + outcomes>
- OPENCLAW_VERIFY: <cli checks + browser checks or N/A>
- RISKS: <list or NONE>

Required docs updates:
- docs/tasks.md
- docs/progress.md
- docs/change-log.md
- docs/traceability.md
- docs/test-results.md

When fully done, run:
openclaw gateway wake --text "Done: <GATE_ID> completed with evidence" --mode now
```

## G1 Planning Prompt

```text
Objective: Complete planning artifacts.

Tasks:
1) Finalize requirements with testable acceptance criteria.
2) Capture Definition of Done.
3) List assumptions and risks.
4) If research_mode=true, produce docs/research-notes.md with options and recommendation.

Validations:
- Ensure requirements are testable and unambiguous.
- Ensure acceptance criteria map to at least one test each.

Done condition:
- docs/requirements.md complete
- docs/plan.md updated
- docs/progress.md updated for G1
```

## G2 Architecture Prompt

```text
Objective: Complete architecture baseline and ADR.

Tasks:
1) Update docs/architecture.md (components, data flow, deployment, security baseline).
2) Update docs/adr/ADR-0001-initial-architecture.md with alternatives and trade-offs.
3) For brownfield, ensure as-is architecture + migration artifacts are current.

Validations:
- Architecture supports must-have journeys.
- ADR includes at least 2 alternatives.

Done condition:
- G2 artifacts complete and cross-linked in docs/traceability.md
```

## G3 Slice-1 Prompt

```text
Objective: Deliver and verify first vertical slice.

Tasks:
1) Implement first slice for the top priority user journey.
2) Add unit and integration tests for this slice.
3) Execute manual smoke test for the slice.

Validations:
- unit tests pass
- integration tests pass
- manual smoke scenario recorded in docs/test-results.md

Done condition:
- slice-1 works end-to-end with evidence
```

## G4 Full Build Prompt

```text
Objective: Complete full build and baseline verification.

Tasks:
1) Implement remaining in-scope v1 features.
2) Run full validation suite.
3) Resolve failures or document blockers.

Validations:
- lint/type/build pass
- unit/integration/e2e pass
- contract checks pass if API boundaries exist

Done condition:
- all in-scope features implemented and verified
```

## G5 Security & Quality Prompt

```text
Objective: Execute security and quality gate.

Tasks:
1) Run dependency/secret baseline checks.
2) Verify auth/input validation/error handling.
3) Run performance smoke checks.

Validations:
- no unresolved critical/high issues
- mitigation plan logged for medium/low issues

Done condition:
- security and quality evidence logged
```

## G6 Release Candidate Prompt

```text
Objective: Prepare and verify release candidate.

Tasks:
1) Complete release checklist.
2) Validate rollback instructions.
3) Confirm monitoring/alerts baseline.

Validations:
- release-checklist complete
- rollback approach validated
- docs versioned and coherent

Done condition:
- RC ready for approval/deployment
```

## G7 Handover Prompt

```text
Objective: Complete handover and close orchestration.

Tasks:
1) Execute post-deploy smoke tests.
2) Finalize handover notes + runbook pointers.
3) Create next-iteration backlog.

Validations:
- critical journeys pass in deployed environment
- unresolved risks have owners

Done condition:
- docs/progress.md reaches 100% and project is handover-ready
```
