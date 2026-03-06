---
content_hash: sha256:8ef39465c4343eebe2654c17aeceea6d9183211db485b1aac0ba2aeba2cf0300
generation_id: 1
generator: monitoring@1.0.0
layer: ops
skill: monitoring
tags:
  - capabilities
  - reference
type: summary
updated: "2026-02-19T08:57:54.276Z"
version: 1
---
# Monitoring Capabilities

## Commands
- `monitor status` — System health summary
- `monitor tokens [--period 7d|30d] [--by model|skill]` — Token usage
- `monitor crons` — Cron job health
- `monitor tasks [--failed]` — Task history
- `monitor cost [--period month|week]` — Cost breakdown
- `monitor ingest token|task|cron` — Manual event ingestion
- `monitor aggregate` — Compute daily aggregates
- `monitor refresh` — Regenerate interchange files
- `monitor backup` / `monitor restore` — Backup and restore

## What It Monitors
- Token spend by model and skill
- Task success/failure/timeout rates
- Cron job reliability and timing
- Daily cost aggregates
