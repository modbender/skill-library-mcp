# Gate Checklists

## G0 Intake Complete
- Planning questionnaire started
- Mission, scope, journeys captured
- project_mode and execution_mode selected

## G1 Planning Approved
- Requirements testable and clear
- **Specs created for all v1 features** (in `docs/specs/` or `docs/requirements.md`)
- **Each spec has acceptance criteria (testable, not vague)**
- Definition of Done captured
- Acceptance tests drafted
- Risks and assumptions listed

## G2 Architecture Approved
Common:
- architecture doc updated
- ADR-0001 completed with alternatives
- **ADRs reference relevant specs**
- test strategy and security baseline included
- **`docs/specs/` directory exists with feature specs**

Greenfield preconditions:
- bootstrap architecture is complete
- **At least one feature spec approved**

Brownfield preconditions:
- as-is architecture complete
- system inventory + dependency map complete
- characterization baseline exists
- migration plan + compatibility matrix complete
- **Existing behavior documented before changes specced**

## G3 Slice-1 Build Verified
- **Task references spec section** (e.g., `Spec: specs/auth.md#login`)
- first vertical slice implemented
- **Implementation matches spec acceptance criteria**
- unit tests pass for slice
- integration test for key path passes
- manual smoke path passes
- docs updated

## G4 Full Build Verified
- **All tasks in g4-task-plan.md have spec references**
- lint/type/build pass
- unit + integration suite pass
- e2e critical paths pass
- contract checks pass (if API boundaries exist)
- migration checks pass (brownfield)
- **All spec acceptance criteria verified**

## G5 Security & Quality Verified
- secret scanning baseline
- dependency vulnerability baseline
- auth/authorization checks
- input validation checks
- error handling/logging checks
- performance smoke checks

## G6 Release Candidate Verified
- release checklist complete
- rollback instructions tested/validated
- monitoring/alerts configured
- open risks acknowledged

## G7 Production/Handover Complete
- post-deploy smoke passes
- handover notes complete
- incident/runbook notes complete
- backlog of follow-ups created

## State Transitions
Allowed: PENDING -> IN_PROGRESS -> PASS/FAIL/BLOCKED
- FAIL requires evidence + remediation plan
- BLOCKED requires owner + unblock condition
