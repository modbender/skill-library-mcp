# Verification Gates

Use these gates to determine if a phase may exit.

## Phase Exit Contract
A phase exits only when:
- required checks are executed,
- evidence is attached,
- acceptance criteria for that phase are satisfied,
- no unresolved critical blockers remain.

## Evidence Requirements
- Artifact references (files, diffs, links, logs).
- Check list with pass/fail status.
- Residual risk notes.
- Decision (`pass`, `fail`, or `partial`) with rationale.
- Hub conformance check result (`pass`, `partial`, `fail`) with remediation list when needed.

## Common Gate Types
- Build/test gate (for coding tasks).
- Behavior/acceptance gate (for product outcomes).
- Integration gate (for cross-repo/dependency tasks).
- Documentation gate (for spec and handoff integrity).
- Output conformance gate (hub schema, list structure, Mermaid fencing).

## Failure Handling
If gate fails:
1. Mark phase as `verify` -> `blocked`.
2. Create remediation task list.
3. Re-run checks after remediation.
4. Escalate to user if remediation changes intent, timeline, or scope.

## Degraded Mode
If required tools are unavailable:
- run available checks,
- mark decision `partial`,
- list missing checks explicitly,
- request user approval to proceed with known risk.

## Conformance Failure Handling
- If output conformance fails in `hard_gate`: block phase exit.
- If output conformance fails in `soft_gate` or `advisory`: mark `partial`, attach remediation, continue with scheduled check-in.
