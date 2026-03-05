# Monitoring Skill

System health monitoring for OpenClaw — tracks token spend, task success rates, cron health, and skill usage.

## Commands
```
monitor status                                          # Health summary
monitor tokens [--period 7d|30d] [--by model|skill]    # Token report
monitor crons                                           # Cron health
monitor tasks [--failed]                                # Task history
monitor cost [--period month|week]                      # Cost breakdown
monitor ingest token|task|cron                          # Manual ingestion
monitor aggregate [--date YYYY-MM-DD]                   # Daily aggregates
monitor refresh                                         # Regenerate interchange
monitor backup [--output path]                          # Backup DB
monitor restore <file>                                  # Restore DB
```

## Interchange
- `ops/capabilities.md` — Command reference (shareable)
- `ops/health.md` — Status indicators only (shareable, no costs/tokens)
- `state/status.md` — Full detailed status (private)
- `state/token-spend.md` — Token/cost breakdown (private)
