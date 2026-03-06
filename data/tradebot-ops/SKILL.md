---
name: tradebot-ops
description: "Operate and monitor the trading bot safely: detect stalls, verify
  LIVE/halting state, validate data freshness, restart cleanly, and produce
  human-readable health summaries."
---

# tradebot-ops

## Purpose
Operate and monitor the trading bot safely: detect stalls, verify LIVE/halting state, validate data freshness, restart cleanly, and produce human-readable health summaries.

## Use when
- Bot shows **LIVE** but no updates (stale heartbeat/bars)
- Chart frozen / signals file not updating
- Need to answer: “Is it running? Is it safe? Why no trades?”

## Inputs
- `dist/out/live_heartbeat_*.json`
- `dist/out/live_signals_*.csv`
- `dist/out/live_trades_*.csv` (if present)
- UI endpoints: `/api/trading/*`

## Outputs
- One-paragraph health summary
- If unhealthy: one action (restart/clear stale) + verification
- Audit log entry

## Safety rails
- Never raise `risk_pct` automatically.
- Prefer restart/self-heal over loosening risk.

## Checklist
1) Confirm UI server reachable `/api/status`.
2) Read heartbeat: mode/status/halted/in_position/last_bar_ts.
3) Freshness: `_hb_age_s`, `_bar_age_s`.
4) Confirm signals file mtime is recent.
5) If stale: stop bot PID (runtime or heartbeat pid) → apply+restart.
6) Re-check last_bar_ts advances.
