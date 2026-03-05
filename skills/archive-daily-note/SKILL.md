---
name: archive-daily-note
description: Automatically moves yesterday's Obsidian daily note into a past-days/ archive folder using the Obsidian CLI move command to preserve wiki-links.
metadata: {"openclaw":{"requires":{"bins":["obsidian"]}}}
---

# Archive Daily Note Skill

Automatically moves yesterday's Obsidian daily note into a `past-days/` archive folder.

## What It Does

Runs daily (e.g., at 12:05 AM) to move the previous day's note from the vault root into `past-days/`. Uses `obsidian move` to preserve wiki-links.

## Cron Setup

Schedule as an isolated cron job running shortly after midnight:

```
Schedule: 5 0 * * * (daily at 00:05)
Target: isolated
```

**Prompt:**
```
Move yesterday's Obsidian daily note into the past-days/ folder.
The note is at the vault root named like 'MM-DD-YYYY DayOfWeek.md'.
Use `obsidian move` so links stay updated.
If it's already in past-days or doesn't exist, skip silently.
```

## Requirements

- Obsidian CLI (`obsidian move` command)
- Daily notes named in `MM-DD-YYYY DayOfWeek.md` format
- A `past-days/` folder in the vault

## Behavior

- **Idempotent**: Safe to run multiple times; skips if already archived or missing
- **Link-safe**: Uses Obsidian's move command to update all internal links
- **Silent**: No output on skip — only reports if something goes wrong
