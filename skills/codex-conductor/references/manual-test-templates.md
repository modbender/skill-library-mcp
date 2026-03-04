# Manual Test Templates

Use these templates for human-verifiable checks. Record all runs in `docs/test-results.md`.

## Mandatory Orchestrator Behavior

- The orchestrator itself performs manual verification after coding agent changes.
- For web/UI systems: run real browser checks.
- For CLI systems: run actual commands and inspect outputs.
- If verification fails: orchestrator re-spawns coding agent with a fix prompt, then re-tests.

## Web App Manual Tests

### WT-001: Auth Login Journey (if auth exists)
- Preconditions: test user account exists
- Steps:
  1. Open login page in a real browser
  2. Submit valid credentials
  3. Confirm landing on authenticated area
- Expected: login succeeds, no console/server errors

### WT-002: Core CRUD Journey
- Steps:
  1. Create an entity
  2. View it in listing/detail
  3. Edit it
  4. Delete it
- Expected: data lifecycle works end-to-end

### WT-003: Failure Path
- Steps:
  1. Trigger invalid input
  2. Trigger API/server failure scenario
- Expected: graceful errors, no crash, clear recovery path

### WT-004: Payment Journey (if payments exist)
- Steps:
  1. Execute success path
  2. Execute failure/cancel path
- Expected: both handled correctly with consistent state

## CLI Manual Tests

### CT-001: Happy Path Command
- Steps: run primary command with valid inputs
- Expected: success exit code and expected output

### CT-002: Invalid Input Handling
- Steps: run command with malformed/missing args
- Expected: clear error, non-zero exit, no crash

### CT-003: Config Handling
- Steps: run with expected config + missing config
- Expected: explicit behavior and guidance

### CT-004: Output Contract
- Steps: verify stdout/stderr format against docs
- Expected: output consistent and parseable if required

## Brownfield Migration Tests

### BT-001: Legacy/Modern Parity Check
- Steps: run same scenario against old and new path
- Expected: equivalent behavior for supported scope

### BT-002: Rollback Rehearsal
- Steps: deploy migration slice then execute rollback procedure
- Expected: service restored cleanly to prior known-good state

### BT-003: Contract Compatibility
- Steps: verify consumer/provider boundary contracts
- Expected: no breaking contract changes
