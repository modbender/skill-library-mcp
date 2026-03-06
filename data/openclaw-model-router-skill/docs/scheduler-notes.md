# Scheduler Integration Notes

This checklist captures everything needed to make the time-based model scheduler
actually switch models in production.

## Implementation Status (2026-02-28)
- ✅ Switch entry: `node src/cli.js schedule apply`
- ✅ Auth gate: `router.config.json -> auth.requiredEnv[]`
- ✅ Verify-after-switch: set + readback required in apply pipeline
- ✅ Rollback on failure: controlled by `safety.rollbackOnFailure`
- ✅ Concurrency lock: `safety.lockPath` lockfile (stale lock recovery)
- ✅ Audit logging: `router.log.jsonl` with success/failure events
- ✅ Failure classification: `auth_expired | rate_limit | provider_drift | unknown`
- ✅ Timezone-aware schedule matching: `router.schedule.json.timezone`

## A. Execution Entry & Auth
- What is the canonical command/API to switch models?
- Does it require auth (token/env vars/permissions)?
- How is success determined (exit code, stdout token, JSON response)?

## B. Current Model Query
- What command/API returns the current active model?
- How to handle query failure (skip, retry, or fallback)?

## C. Runtime Environment
- Who runs the schedule (cron/systemd/OpenClaw scheduler)?
- Required environment variables?
- Working directory assumptions?

## D. Safety & Rollback
- On switch failure, should we restore the previous model?
- How to verify the switch after apply?
- Backoff/lockout after repeated failures?

## E. Concurrency & Locks
- Could multiple jobs trigger at once?
- Do we need a PID/lock file?
- Should switching block other tasks?

## F. Schedule Semantics
- Which timezone is authoritative?
- Priority rules for overlapping windows?
- Overnight windows handling (e.g. 22:00-06:00)?

## G. Logging & Audit
- Where to log each switch (path/rotation)?
- Required fields (timestamp, from, to, reason, result)?
- Optional notifications (Feishu/Slack/Discord)?

## H. Failure Cases
- Provider unavailable?
- Model name drift?
- Quota/budget exhaustion?

