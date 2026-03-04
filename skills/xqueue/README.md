# XQueue

A file-based post scheduler for X (Twitter). Your file system is the UI.

No database. No dashboard. No app. Just folders, text files, and a cron job.

## How It Works

```
xqueue/
  config.json
  backlog/
  Monday/
    9am/
      thread-about-shipping.md
    12pm/
    5pm/
  Tuesday/
    ...
```

- **Drop a `.md` file into a day/time folder** → it posts at that time
- **Empty slot?** → pulls the oldest file from `backlog/` automatically
- **Schedule cycles weekly** → Monday/9am fires every Monday at 9am
- **Files are deleted after posting** (configurable) so nothing repeats

## Setup

```bash
python3 xqueue-setup.py
```

The setup wizard asks how many daily posts, what times, timezone, and optional X community targets (paste the community URL, it extracts the ID). Creates the full folder structure + `config.json`.

## Tweet Formats

**Simple tweet** — just text in a `.md` file:
```
Just shipped v2. Sometimes the simplest architecture wins.
```

**Thread** — one file, `---` between tweets:
```
I built a file-based tweet scheduler with no frontend. Your filesystem is the UI.
---
Drop a .md file into Monday/9am/ and a cron job posts it. Empty slot? It pulls from backlog automatically.
---
No database, no app, no dashboard. Just folders and text files.
```

**With media** — put images in the same folder (max 4, alphabetical order):
```
9am/
  tweet.md
  screenshot.png
```

**Community post** — prefix with the community name:
```
Post to Build in Public: Just shipped my first skill. File-based tweet scheduler, no frontend needed.
```

## Backlog

The `backlog/` folder holds content without a specific time slot. When a scheduled slot is empty, the oldest backlog file gets posted. Prefix filenames with numbers (`01-`, `02-`) to control order.

Write a week of content in one sitting, dump it in backlog, and it distributes itself across your empty slots.

## Cron

Designed to run on a 15-minute cron cycle. Each tick:
1. Checks current day + time against folder structure
2. Posts slot content (or pulls from backlog if empty)
3. Logs to `posted.log`
4. Cleans up posted files

## Requirements

- Python 3
- X API credentials via environment variables:
  - `X_CONSUMER_KEY`, `X_CONSUMER_SECRET` (app credentials)
  - `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` (user credentials)
  - Optional: set `XQUEUE_KEYCHAIN_ACCOUNT` to use macOS Keychain as fallback
- A cron runner (OpenClaw cron, system cron, etc.)

## License

MIT
