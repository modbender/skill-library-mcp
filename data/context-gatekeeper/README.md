# Context Gatekeeper — Full documentation

## Purpose
**Context Gatekeeper** keeps OpenClaw sessions token-efficient by compressing the active conversation. It summarizes the tail of the thread, spots open tasks, and keeps a short log of the latest turns so you only send what matters to the model.

## Repository layout
```
skills/context-gatekeeper/
├── SKILL.md                  # Meta description (triggers and usage)
├── README.md                 # This reference for ClawHub and contributors
├── scripts/
│   ├── context_gatekeeper.py  # Builds the compact summary, highlights, and recent-turn log
│   ├── auto_monitor.py        # Watches history.txt and regenerates the summary automatically
│   └── ensure_context_monitor.sh  # Starts (or restarts) the monitor safely
├── context/
│   ├── history.txt           # Rolling log (ROLE: message)
│   ├── current-summary.md    # Briefing used before every reply
│   └── sample-history.txt    # Test data for quick verification
└── README.md                 # This document
```

## Scripts overview

### `context_gatekeeper.py`
1. Reads the history file (ROLE: message per line) and slices the text into sentences.
2. Picks up pending tasks by keyword (todo, task, follow-up, next step, etc.) and keeps up to the last four turns.
3. Outputs `current-summary.md` containing: timestamp, "Compact summary", "Pendencies and next steps" and "Last turns" sections.
4. You can tweak output length via `--max-summary-sents`, `--max-pendings`, and `--max-recent-turns`.

### `auto_monitor.py`
1. Runs in a loop and watches `context/history.txt` for modification time changes.
2. When new content appears, it executes `context_gatekeeper.py` and logs the event to `/tmp/context-gatekeeper-monitor.log`.
3. Ensures the summary is fresh before each answer, supporting 24/7 operation.

### `ensure_context_monitor.sh`
- Checks for an existing `auto_monitor.py` process (`pgrep -f auto_monitor.py`). If none exists, it launches the monitor with `nohup` and saves logs.
- Designed to be called at startup (`STARTUP.md`) so the monitor automatically restarts after `/reset`, `/new`, or any reboot.

## Daily workflow
1. Append every incoming and outgoing message as `USER: ...` / `ASSISTANT: ...` in `context/history.txt`.
2. The monitor detects the change and rewrites `context/current-summary.md` with the current briefing.
3. Before calling the model, load the summary (and the last few turns if necessary) instead of the entire history.
4. Run `/session_status` or the equivalent command to capture token consumption before responding.
5. Always append a footer line `tokens in <qty> / tokens out <qty>` to every reply so the usage is auditable.
6. When you want to force the summary update manually, run:

```bash
python3 scripts/context_gatekeeper.py \
  --history context/history.txt \
  --summary context/current-summary.md
```

## Publication details
- Published as `context-gatekeeper@0.1.1` (latest release). The version bundle includes this README plus all scripts and context templates so any user can install via `clawhub install context-gatekeeper`.
- Author: Davi Marques. Repository slug: `context-gatekeeper`.

## Installation recipe
1. Ensure `skills/context-gatekeeper` exists under `<workspace>/skills`.
2. Run `./scripts/ensure_context_monitor.sh` or rely on the STARTUP runner so the monitor stays alive.
3. Keep `context/history.txt` updated and inspect `context/current-summary.md` before talking to the model.
4. Keep `/session_status` output saved together with each response (the README explains why the token line is mandatory).

## Recommendations
- Limit the history file to the essential RECENT exchanges that drive the next turn.
- Watch `/tmp/context-gatekeeper-monitor.log` for monitor errors or long pauses.
- Update `memory/daily/YYYY-MM-DD.md` and `TOOLS.md` whenever the workflow changes so the rest of the team stays aligned.
