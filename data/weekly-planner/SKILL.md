---
name: weekly-planner
description: File-based weekly planning system (TOML) with inbox capture,
  time-block scheduling, weekly review, and optional calendar publishing (Google
  Calendar via gogcli or .ics export). Use when a user asks to plan or
  time-block a week, triage an inbox of tasks, roll over unfinished work, run a
  weekly review, or publish a weekly schedule to a calendar. Do NOT use for full
  project-management tools (Jira/Linear/etc.) unless explicitly requested.
---


# Weekly Planner

A lightweight, **file-based weekly planner** that lives in a workspace folder as plain text (`.toml`). It supports:

- **Inbox capture** (`planner/inbox.toml`) for fast, append-only task capture
- **Weekly plans** (`planner/weeks/YYYY-Www.toml`) with:
  - scheduled **time blocks** (can be published to a calendar)
  - unscheduled **weekly bits** / **daily bits**
  - an end-of-week **review**
- **A runbook** (`planner/runbook.toml`) of recurring blocks copied into each new week
- Optional **mode cards** (`planner/modes/*.md`) describing how the user wants to work in different contexts


## When to use this skill

Use this skill when the user asks for any of the following:

- “Plan my week”, “time-block my week”, “create a weekly plan”, “make a schedule for next week”
- “Capture this in my inbox”, “add this to my planner”, “triage my tasks”
- “Create a new week file”, “roll over last week’s unfinished tasks”
- “Publish/sync my planner to my calendar”, “export an .ics for my week”
- “Do an end-of-week review”

Don’t use this skill for full project-management systems (Jira/Linear/etc.) unless the user explicitly wants that.


## Quick start

### 1) Ensure the planner folder exists

Look for a `planner/` folder in the current workspace that contains `planner/config.toml`.

If it doesn’t exist, initialise a fresh planner skeleton (safe: refuses to overwrite existing folders):

```bash
python3 {baseDir}/scripts/init_planner.py --target ./planner
```

This creates:

- `planner/config.toml`
- `planner/inbox.toml`
- `planner/runbook.toml`
- `planner/weeks/WEEK_TEMPLATE.toml`
- `planner/modes/*.md`
- `planner/scripts/new_week.py`
- `planner/scripts/rollover_week.py`
- `planner/scripts/validate.py`
- `planner/scripts/sync_week.py` (Google Calendar sync via `gog`)
- `planner/scripts/export_ics.py` (calendar export without Google tooling)
- `planner/logs/`

### 2) Tell the user what to customise

Ask the user to review **`planner/config.toml`** and customise:

- `timezone` (IANA tz name, e.g. `Europe/Berlin`)
- `modes.*` (their mode names + labels)
- (Optional) calendar publish settings (see “Publish to calendar” below)

### 3) Create (or roll over) a week

Create a new week file:

```bash
python3 planner/scripts/new_week.py --week-start 2026-03-02
```

Or roll over unfinished tasks from the most recent week:

```bash
python3 planner/scripts/rollover_week.py --next
```

### 4) Validate before “publishing” anything

Run validation after edits (especially before calendar publish):

```bash
python3 planner/scripts/validate.py --week planner/weeks/2026-W10.toml
```


## Core workflows

### A) Inbox capture

Goal: capture tasks with minimal friction.

Rules:

- Treat `planner/inbox.toml` as **append-only**.
- Add one `[[items]]` block per task.
- Keep each entry small; use `notes` only when it helps.

When the user says “add this to my inbox”, append a new item like:

```toml
[[items]]
created = "YYYY-MM-DDTHH:MM:SS+01:00"
text = "(task description)"
mode = "ops"               # any key from config.toml [modes.*]
est_minutes = 30
priority = "medium"        # low|medium|high
status = "todo"            # todo|doing|done|dropped
notes = ""
```

If the user doesn’t specify `mode`, choose a reasonable default (usually their “ops/admin” mode).


### B) Triage inbox → weekly plan

Goal: turn raw inbox items into (a) 2–3 outcomes, (b) a small set of scheduled blocks, and (c) a manageable list of unscheduled bits.

Process:

1) Read `planner/inbox.toml`.
2) Ask the user for:
   - hard constraints (deadlines, appointments, travel)
   - 2–3 outcomes they care about this week
   - anything non-negotiable (exercise, family time, admin)
3) Convert inbox items into one of:
   - **time blocks** (must happen at a specific time)
   - **weekly bits** (do sometime this week)
   - **daily bits** (do sometime on a specific day)
   - or mark as **dropped** if it’s not happening this week

Keep the plan intentionally small:
- 2–5 focus tasks
- A few high-leverage time blocks
- A short “bits” list the user can realistically finish


### C) Create a new week file

Use when the user wants to start planning a new week.

1) Determine `week_start` (a Monday date in `YYYY-MM-DD`).

2) Generate the file (copies runbook blocks into `[[time_blocks]]`):

```bash
python3 planner/scripts/new_week.py --week-start 2026-03-02
```

3) Then edit `planner/weeks/2026-W10.toml`:

- Fill `[goals]` outcomes (2–3 crisp outcomes)
- Add `focus_tasks` (2–5 items max)
- Add / adjust `[[time_blocks]]` (scheduled blocks)
- Add `[[weekly_bits]]` and `[[daily_bits]]` for unscheduled tasks


### D) Roll over unfinished work (optional)

Use when the user has an existing week file and wants to start the next week without retyping.

Typical flow:

```bash
python3 planner/scripts/rollover_week.py --next
```

This:

- finds the most recent week in `planner/weeks/`
- creates the next week (week_start + 7 days)
- copies runbook blocks into the new week’s `[[time_blocks]]`
- carries over unfinished `weekly_bits` and `daily_bits`


### E) Publish time blocks to a calendar (optional)

Only `[[time_blocks]]` are published.

Two safe options:

#### Option 1: Google Calendar sync (direct, destructive)

This workflow is **destructive by design** — it updates/deletes managed events.

Safety rules (must follow):

- Only ever sync to a **dedicated planner calendar** (never the user’s main calendar).
- Always run **dry-run first**.
- Only run with `--apply` if BOTH are true:
  1) The user explicitly asked you to apply changes.
  2) `calendar.write_enabled = true` in `planner/config.toml`.

Requirements:

- `gog` CLI installed + authenticated (`steipete/gogcli`)

Dry-run:

```bash
python3 planner/scripts/sync_week.py --week planner/weeks/2026-W10.toml
```

Apply:

```bash
python3 planner/scripts/sync_week.py --week planner/weeks/2026-W10.toml --apply
```

#### Option 2: Export an .ics file (safe, non-destructive)

Works without Google tooling.

```bash
python3 planner/scripts/export_ics.py --week planner/weeks/2026-W10.toml
```

This writes `planner/weeks/2026-W10.ics`, which the user can import into most calendar apps.


### F) End-of-week review

At the end of the week, help the user fill:

- `review.score` (0–10)
- `review.wins` (1–5 bullets)
- `review.fails` (1–5 bullets)
- `review.what_i_learned` (short paragraph)
- `review.next_week_focus` (1–2 sentences)


## Quality gates

Before publishing/syncing:

1) Run validation:

```bash
python3 planner/scripts/validate.py --week planner/weeks/2026-W10.toml
```

2) Fix all **errors**.
3) Treat **warnings** as “strong suggestions” (overlaps, out-of-bounds blocks, unknown modes).


## References

- File formats and schema: `references/PLANNER_SCHEMA.md`
- Calendar publish & safety model: `references/CALENDAR_SYNC.md`


## Troubleshooting

### “Python can’t import tomllib” / “No module named tomllib”

You’re on Python < 3.11.

Fix: install Python 3.11+ and re-run.

### “gog: command not found”

Google Calendar sync requires the `gog` CLI.

Fix: either install `gogcli` (see references) or use the `.ics` export instead.

### “Refusing to apply changes: calendar.write_enabled is false”

Intentional safety latch.

Fix: have the user set `calendar.write_enabled = true` once they’re confident in the dry-run output.
