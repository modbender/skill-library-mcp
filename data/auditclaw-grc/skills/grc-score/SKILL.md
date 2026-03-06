---
name: grc-score
description: Quick compliance score check with trend
user-invocable: true
metadata: {"openclaw":{"requires":{"bins":["python3"]}}}
---
# GRC Score

Show the current compliance score for all active frameworks.

## What to do
Using the auditclaw-grc skill, calculate and display compliance scores for all active frameworks.
Include:
- Overall weighted score
- Per-framework breakdown with health distribution
- Score trend (compared to last calculation)
- Any score drift alerts
