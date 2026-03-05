# Testing Matrix (Gate-Based)

Apply this matrix on every project. Expand when domain-specific risks appear.

## Gate G1 (Planning)
- Validate requirements clarity
- Validate acceptance criteria are testable
- Validate risks and assumptions listed

## Gate G2 (Architecture)
- Validate architecture supports all must-have journeys
- Validate threat model baseline exists
- Validate ADR exists with alternatives and trade-offs

## Gate G3 (Slice-1 Build)
- Unit tests for first slice pass
- Integration test for key flow passes
- Manual smoke test of one critical journey passes
- Docs updated for slice

## Gate G4 (Full Build)
- Lint/type/build clean
- Unit/integration suite pass
- E2E critical paths pass
- API contract checks pass (if relevant)
- Data migration checks pass (if relevant)

## Gate G5 (Security & Quality)
- Secret scanning baseline
- Dependency vulnerability scan baseline
- AuthN/AuthZ checks
- Input validation checks
- Error handling/logging checks
- Performance smoke checks

## Gate G6 (Release Candidate)
- Release checklist complete
- Rollback steps tested or validated
- Monitoring/alerts configured
- Versioned docs complete

## Gate G7 (Production/Handover)
- Post-deploy smoke tests pass
- Incident runbook available
- Handover notes complete
- Open risks tracked with owners

## Manual Testing Requirements

For Web Projects:
- Login flow (if auth exists)
- Core create/read/update/delete journey
- Payment happy path + failure path (if payments exist)
- Error page and recovery behavior

For CLI Projects:
- Core command success path
- Invalid input handling
- Config loading behavior
- Output format consistency

## Evidence Format

For every gate, record in `docs/test-results.md`:
- test name
- command or steps
- expected result
- actual result
- pass/fail
- evidence link/snippet
- timestamp
