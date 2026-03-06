# Gateway Runbook (Token-lean Operation)

## Principle
- Gateway handles repetitive low-cost sync work.
- Agent handles short decision bursts and user-facing proposals.

## Gateway-owned recurring tasks
- `run-adaptive-sync-loop.ps1` (read/sync cadence)
- optional `capture-playback-loop.ps1` (skip/playtime collection)
- periodic `capture-current-volume.ps1` (volume signal snapshots)

## Agent-owned on-demand tasks
- `decision-commands.ps1 -Action suggest-reorg`
- `decision-commands.ps1 -Action apply-reorg -HumanConfirmed`
- `decision-commands.ps1 -Action confirm-delete -HumanConfirmed`
- `recommend-commands.ps1 -Action run|show|queue`

## Cost-safe defaults
- Keep `auto_cleanup_enabled=false`
- Trigger cleanup prompts via `check-cleanup-trigger.ps1`
- Enforce preflight gates (human confirm + budget + quiet-hours)

## Suggested daily flow
1. Gateway syncs state cheaply in background.
2. Agent checks `check-cleanup-trigger.ps1` occasionally.
3. Agent asks user only when trigger says worthwhile.
4. Apply/delete only after explicit confirmation.
