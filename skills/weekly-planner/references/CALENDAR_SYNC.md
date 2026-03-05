# Calendar publishing

Publishing is optional. Only `[[time_blocks]]` are published.

There are two supported publishing paths:

1) **Google Calendar sync (direct, destructive)** via `planner/scripts/sync_week.py` + `gog`
2) **.ics export (safe, non-destructive)** via `planner/scripts/export_ics.py`

---

## Option 1: Google Calendar sync (direct, destructive)

If enabled, `planner/scripts/sync_week.py` syncs a week’s `[[time_blocks]]` into a **dedicated Google Calendar**.

### Requirements

- Python 3.11+
- The `gog` CLI (`steipete/gogcli`) available on `PATH`
- A dedicated Google Calendar ID configured in `planner/config.toml`

Install (macOS/Homebrew):

```bash
brew install steipete/tap/gogcli
gog --version
```

Configure calendar target:

```toml
[calendar]
# Dedicated calendar for destructive sync (never use your primary calendar)
planner_calendar_id = "...@group.calendar.google.com"
write_enabled = false
```

Tip: to find calendar IDs (requires gog auth):

```bash
gog calendar calendars --max 50 --json
```

### Safety model

The sync is intentionally conservative:

- It only queries the configured calendar (`calendar.planner_calendar_id`).
- It only manages events that it can identify as **managed**.
- Default mode is **dry-run**.
- Even with `--apply`, it refuses to write unless `calendar.write_enabled = true`.

### How managed events are identified

The script uses a configurable `marker_prefix` (default: `planner`) from:

```toml
[sync]
marker_prefix = "planner"
```

It then sets and filters on Google Calendar **private extended properties**:

- `<prefix>_week = YYYY-Www`
- `<prefix>_key = YYYY-Www|<time_block_id>`
- `<prefix>_block_id = <time_block_id>`

The same markers are also written into the event description for transparency.

### Recommended workflow

1) Start with dry-run:

```bash
python3 planner/scripts/sync_week.py --week planner/weeks/2026-W10.toml
```

2) Review the printed plan (CREATE / UPDATE / DELETE).

3) If it looks correct, opt in to writes:

- edit `planner/config.toml`
- set `calendar.write_enabled = true`

4) Apply:

```bash
python3 planner/scripts/sync_week.py --week planner/weeks/2026-W10.toml --apply
```

### Troubleshooting

#### The script wants to DELETE events I care about

That means those events are considered “managed” for that week, but no longer exist in the week file.

Fix:

- Either restore the corresponding `[[time_blocks]]` entry (same `id`), or
- Accept the delete and apply.

#### Events are being created instead of updated

Common causes:

- You changed the time block `id` (which is the stable key).
- You changed `sync.marker_prefix` between runs.

Fix:

- Keep time block `id` stable.
- Don’t change marker prefix once you’ve begun syncing (unless you intentionally want a clean slate).

---

## Option 2: Export an .ics file (safe, non-destructive)

Use this if you don’t want to configure `gog`, or you want a non-destructive workflow.

Export:

```bash
python3 planner/scripts/export_ics.py --week planner/weeks/2026-W10.toml
```

This writes:

- `planner/weeks/2026-W10.ics`

The user can then import the `.ics` file into most calendar applications.
