# Architecture

## Goal

Provide an auditable, deterministic incident pipeline:

1. Detect anomalies from structured runtime data.
2. Apply guardrails (in-flight + cooldown).
3. Emit actions for investigator/remediator agents.

## Data model

- Detector output: JSONL stream (`ops-detector.jsonl`)
- Router output: JSONL stream (`router-actions.jsonl`)
- Guard state: JSON object keyed by `check_id`

Example guard state entry:

```json
{
  "cron_failure": {
    "in_flight": false,
    "flow_started_utc": null,
    "last_completed_utc": "2026-02-24T02:10:00Z",
    "last_severity": "Sev-2",
    "cooldown_until_utc": "2026-02-24T02:40:00Z"
  }
}
```

## Recommended thresholds

- `context_warn`: Sev-3
- `context_high`: Sev-2
- `context_crit`: Sev-2 + manual approval path
- `cron_failure`: Sev-2 when failures > 0 in lookback
- `heartbeat_gap`: Sev-2 when critical job run gap exceeds threshold
- `dangling_sessions`: Sev-2 when count > 0
- `token_spike`: Sev-3 when daily usage > 2x prior snapshot

## Safe rollout

1. start with dry-run mode
2. verify 0 false-positive loops for at least 3-7 days
3. enable live lock acquisition
4. keep writes/remediation behind human approval
