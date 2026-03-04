# Ops Playbook (Obsidian + GitHub KB Share)

## Daily

1. `bash scripts/sync_kb.sh --mode safe`
2. Write notes in canonical folders.
3. If doing batch edits, run commit mode:
   - `bash scripts/sync_kb.sh --mode commit --message "chore(kb): <scope>"`

## Conflict handling

When `pull --rebase` conflicts:

1. Preserve both sides into a new note:
   - `01_Daily/conflict-YYYY-MM-DD-HHMM.md`
2. Keep original intent and source host info.
3. Resolve file conflict, then continue rebase.
4. Push.

## Multi-host policy

- Never edit same note simultaneously on two hosts.
- Prefer append-only logs for shared daily files.
- Place agent-private iterative notes in `90_Agents/<Agent>/`.

## Suggested OpenClaw cron jobs

- 30m safe sync (no auto-commit)
- 4h status report
- 24h integrity check (markers, detached HEAD, remote availability)
