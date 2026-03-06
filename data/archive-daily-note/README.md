# Archive Daily Note

A simple cron skill that moves yesterday's Obsidian daily note into an archive folder, keeping your vault root clean.

## What It Does

Every night at 00:05, it moves the previous day's note (e.g., `02-22-2026 Sunday.md`) from the vault root into `past-days/`, using Obsidian's move command to preserve all wiki-links.

## Setup

1. Create a `past-days/` folder in your Obsidian vault
2. Set up a cron job with the prompt from `SKILL.md`
3. Adjust the date format pattern if your daily notes use a different naming convention

## Requirements

- [Obsidian CLI](https://obsidian.md) with `obsidian move` support
- Daily notes at vault root in `MM-DD-YYYY DayOfWeek.md` format

## Behavior

- ✅ Idempotent — safe to run multiple times
- 🔗 Link-safe — updates all internal references
- 🤫 Silent on skip — no noise when nothing to do

## License

MIT
