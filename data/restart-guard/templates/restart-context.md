---
reason: ""
triggered_at: ""
triggered_by: ""
restart_id: ""
origin_session_key: ""
notify_mode: "origin"
channel_selection: {}
effective_notify_plan: {}
state_timestamps: {}
diagnostics_file: ""
delivery_status: ""
verify:
  # Each entry: { command: "...", expect: "..." }
  # postcheck.py runs each command and checks if output contains 'expect'
  - command: "openclaw health --json"
    expect: "ok"
resume:
  # Steps for the agent to execute after successful restart
  - "向用户汇报重启结果"
rollback:
  # Path to config backup (auto-filled by restart.py)
  config_backup: ""
---

# Restart Context

## Reason

<!-- Why is this restart needed? What changed? -->

## Changes Made

<!-- What config/files were modified before restart? -->

## Pre-Restart State

<!-- Brief snapshot of current state: running tasks, pending work, etc. -->

## Notes

<!-- Any additional context for post-restart recovery -->
