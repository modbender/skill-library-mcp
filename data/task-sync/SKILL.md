---
name: task-sync
description: Synchronize TickTick (Dida) and Google Tasks bidirectionally, including list/project mapping, task content sync, completion sync, and smart-list export (Today, Next 7 Days, All). Use when users ask to set up OAuth, run or schedule sync, fix mismatched/deleted/completed tasks, or troubleshoot Google Calendar duplicate behavior caused by due-date handling.
---

# Task Sync

Operate and troubleshoot bidirectional task sync between TickTick and Google Tasks.

## Run

```bash
python {baseDir}/sync.py
```

## Setup Checklist

1. Python 3.10+ with: `google-auth google-auth-oauthlib google-api-python-client requests`
2. Enable Google Tasks API and run:
   ```bash
   python {baseDir}/scripts/setup_google_tasks.py
   ```
3. Create TickTick developer app and run:
   ```bash
   python {baseDir}/scripts/setup_ticktick.py
   ```
4. Configure `{baseDir}/config.json` token and data paths.

## Expected Behavior

- Sync Google Task Lists `<->` TickTick Projects by same name.
- Sync task title, completion status, and notes/content bidirectionally.
- Map TickTick priority to Google title prefix: `[★]` high, `[!]` medium.
- Export TickTick smart lists (Today, Next 7 Days, All) to Google Tasks one-way.

## Due-Date Rule (Calendar Duplicates)

- Keep due dates only in the "All" smart list.
- For other synced lists, forward date to TickTick then clear Google due date.
- Treat this as the source-of-truth rule when debugging duplicate Calendar items.

## Automation

```bash
# Cron: every 10 minutes
*/10 * * * * /path/to/python {baseDir}/sync.py >> /path/to/sync.log 2>&1
```

Use OpenClaw cron if available.

## Troubleshooting Workflow

1. Re-run both OAuth setup scripts if auth errors appear.
2. Verify `config.json` paths point to existing token files.
3. Run `python {baseDir}/sync.py` and inspect `{baseDir}/data/sync_log.json` and `{baseDir}/data/sync_db.json`.
4. Check API wrappers:
   - `{baseDir}/utils/google_api.py`
   - `{baseDir}/utils/ticktick_api.py`
