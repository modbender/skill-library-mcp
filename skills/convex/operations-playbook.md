# Convex Operations Playbook

Use this file for release readiness and incident response.

## Pre-Deploy Gate

1. Confirm schema and function compatibility with active clients.
2. Verify auth checks on all new entry points.
3. Rehearse rollback for the exact change set.
4. Confirm observability for high-risk paths.

## Rollout Strategy

- Roll out additive schema changes before behavior switches.
- Gate risky logic behind explicit flags where possible.
- Prefer staged traffic or staged feature activation over big-bang flips.

## Incident Triage

When production breaks:
1. Capture failing function and affected records.
2. Classify: data integrity, auth leak, performance, or external dependency.
3. Stop harmful writes first.
4. Apply smallest safe mitigation.
5. Publish user-impact summary and next checkpoint.

## Post-Incident Learning

- Log root cause in `~/convex/memory.md`.
- Add a prevention rule to test or review checklists.
- Remove temporary mitigations once durable fix is live.

## Webhook and Action Safety

- Require idempotency keys for retried events.
- Validate payload signature and event freshness.
- Persist processing state to avoid replay side effects.

## Operational Anti-Patterns

- Deploying schema and risky logic in one irreversible step.
- Treating missing auth context as harmless defaults.
- Fixing incidents without writing a durable prevention rule.
