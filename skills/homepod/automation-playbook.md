# HomePod Automation Reliability Playbook

Use this playbook when Home automations are intermittent, delayed, or non-deterministic.

## Record Format

Track each automation attempt with:
- Trigger event
- Conditions evaluated
- Expected action
- Actual action
- Execution latency

## Stabilization Sequence

1. Freeze the scenario:
- Keep one canonical test automation per issue.
- Disable duplicate or overlapping automations temporarily.

2. Validate trigger quality:
- Confirm trigger source is stable and unique.
- Remove ambiguous triggers that overlap in time.

3. Validate condition logic:
- Check that conditions are observable and current.
- Avoid conditions that depend on stale states.

4. Validate action path:
- Confirm target accessory is online and writable.
- Confirm no conflicting scenes run in parallel.

5. Run deterministic retries:
- Execute three controlled runs with the same inputs.
- If results differ, classify as unstable and keep scope narrow.

## Reliability Rules

- One variable change per test cycle.
- Keep a baseline automation untouched for comparison.
- Promote fixes only after repeated pass results.
- Document rollback path for every non-trivial change.

## Exit Criteria

Automation is considered stable only when:
- Three consecutive test runs pass.
- No side effects appear in unrelated rooms or scenes.
- Latency remains inside expected user tolerance.
