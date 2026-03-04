# Least-Privilege Policy For OpenClaw

## Objective

Enforce default non-root execution and explicit approval-first elevation with immediate privilege drop after privileged operations.

## Required Controls

1. Set default execution context to non-root.
2. Require approval before every privileged command.
3. Limit privileged commands to a reviewed allowlist (per-task scope).
4. Log privileged requests, approvals, and execution outcomes.
5. Drop elevated state immediately after privileged command completion.
6. Force elevated timeout expiration after 30 idle minutes.

## Operational Checks

1. Verify privileged command is required for task outcome.
2. Execute privileged work through wrapper:
   - `python3 scripts/guarded_privileged_exec.py --reason "required change" --use-sudo -- <command>`
3. If wrapper requests approval, require explicit user consent before command runs.
4. Execute only the approved privileged command(s):
   - Approval is tied to the exact argv you approved.
   - Any different privileged argv triggers a new approval and allowlist entry.
5. Confirm wrapper drops privilege immediately after completion.

## Control Acceptance Criteria

1. No privileged command runs without current-task user approval.
2. Elevated session is not retained after privileged work completes.
3. Idle elevated session at or above 30 minutes transitions to normal mode.
4. Session state file records UTC transition/action metadata.

## Suggested OpenClaw Config Direction

Configure OpenClaw with strict approval and allowlist behavior:

- Set execution ask behavior to always prompt.
- Set execution security mode to allowlist.
- Restrict elevated tool callers with explicit `allowFrom` entries.
- Keep sandboxing enabled for normal operations.

If exact keys differ by version, preserve intent: explicit approval + least privilege + short-lived elevation.
