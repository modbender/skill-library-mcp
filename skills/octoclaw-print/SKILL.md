---
name: octoclaw
description: Control OctoPrint 3D printer — monitor status, capture webcam snapshots, manage prints, analyze gcode, and detect errors. Use when the user asks about their 3D printer, print status, filament, temperatures, or wants to start/pause/cancel a print.
metadata: { "openclaw": { "emoji": "🐙", "requires": { "bins": ["python3"] } } }
---

# OctoClaw — OctoPrint Control

Helper script: `scripts/octoprint.py` (relative to this skill directory).
Config: `config.json` (same directory) with `octoprint_url` and `api_key`.

Resolve all paths relative to this skill's directory.

## Commands

All commands: `python3 <skill-dir>/scripts/octoprint.py <command> [args]`

### Status
- `status-pretty` — Formatted status with temps, progress bar, ETA (show this to users)
- `status` — Raw JSON
- `check-errors` — Returns JSON with errors/warnings (temp anomalies, stalls, connection issues)

### Print Control
- `print <filename>` — Start a print
- `control <pause|resume|cancel>` — Control active print
- `temp <tool0|bed> <temperature>` — Set temperature

### Files
- `list-files` — List uploaded files
- `upload <local-path> [remote-name]` — Upload gcode
- `analyze <filepath>` — Extract gcode metadata (layers, time, filament, temps, dimensions)

### Webcam
- `snapshot [output-path]` — Capture webcam image (default: /tmp with timestamp)

### Telegram (if configured)
- `telegram-status` — Send formatted status to Telegram
- `telegram-snapshot` — Send webcam snapshot with progress caption
- `telegram-msg "message"` — Send custom message

## Workflows

**Check on a print:** `status-pretty` → optionally `snapshot` → `check-errors`

**Start a print:** `status-pretty` (verify Operational) → `list-files` or `upload` → optionally `analyze` → `print <file>`

**Error detection:** `check-errors` returns critical errors (>15°C deviation, connection lost) and warnings (5-15°C deviation, stalled prints). Recommend pausing on temp issues, cancelling on critical errors.

## Formatting
- Use `status-pretty` output for user display
- Always show progress %, time remaining, ETA for active prints
- Include temperature actual/target
