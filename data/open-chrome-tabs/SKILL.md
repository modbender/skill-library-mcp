---
name: chrome-open-tabs
description: Read currently open browser tabs from Chrome or other Chromium browsers (Arc, Brave, Edge, etc.). Use when you need to know what URLs the user has open, or want to list tabs from a synced device (e.g. Chrome on their phone).
---

# chrome-open-tabs

Install once: `npm install -g @mindsocket/chrome-open-tabs`

Or one-off: `npx @mindsocket/chrome-open-tabs ...`

## Hierarchy

`--user-data` (browser) → `--profile` → `--device`

| Option | Default | Notes |
|---|---|---|
| `--user-data` | Chrome | path to browser's User Data dir |
| `--profile` | `Default` | Try `Profile 1`, `Profile 2` etc if Default not right |
| `--device` | all | filter to one synced device; requires browser to be closed |

## Mode

Always prints to stderr: `[sync-data]` or `[session-files]`

- **sync-data** — reads Chrome sync LevelDB; shows tabs across all synced devices
- **session-files** — reads local SNSS session file; local tabs only, no device info; used when browser has no sync data or is running

## Common workflow

```bash
# 1. Find which devices are synced
chrome-open-tabs --profile "Profile 1" devices
# → MacBook Air
# → Pixel 9a

# 2. Get tabs from a specific device
chrome-open-tabs --profile "Profile 1" --device "Pixel 9a" --json

# 3. Get all tabs across all devices
chrome-open-tabs --profile "Profile 1" --json
```

## Other browsers

```bash
# Arc
chrome-open-tabs --user-data "$HOME/Library/Application Support/Arc/User Data"
```

## Notes

- `--device` and `devices` require sync data — both error if the browser is running
- If the browser is running, falls back to session files automatically (local tabs only)