# HEARTBEAT.md

## On Every Wake-Up — Mandatory
1. Read `STATE.md`
2. Read `memory/YYYY-MM-DD.md` (today) — create if missing
3. Read `MEMORY.md`

## 🔍 Health Check (silent = good, report only issues)

### Crons
- `cron list` → check **consecutiveErrors > 0** → alert immediately
- Frequent crons not running >2 hours → alert

### Critical Processes
- [Add your process checks here]

### Gateway
- `openclaw gateway status` → running? if not → alert

## 📝 Documentation
- Everything that happens → write to `memory/YYYY-MM-DD.md`
- New decision → write to MEMORY.md
- Never trust "mental notes" — **file written or it didn't happen**
