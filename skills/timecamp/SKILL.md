---
name: timecamp
description: Use when the user asks about time tracking, time entries, tasks, timers, or anything related to TimeCamp. Triggers on keywords like "timecamp", "time entries", "timer", "tracking", "hours", "timesheet", "tasks list", "start timer", "stop timer", "activities", "computer activities".
metadata:
  openclaw:
    emoji: ⏱️
    requires:
      env: ["TIMECAMP_API_KEY"]
---

# TimeCamp Skill

Two tools: **CLI** for quick personal actions (timer, entries CRUD) and **Data Pipeline** for analytics/reports.

## Bootstrap (clone if missing)

Before using either tool:

1. Ask user where repos should live (default: `~/utils`, but any location is valid).
2. If repos are missing in that chosen location, ask for confirmation to clone.

Example flow and commands:

```bash
# Ask first:
# "I don't see TimeCamp repos locally. Clone to ~/utils, or use a different location?"

REPOS_DIR=~/utils  # replace if user picked a different path
mkdir -p "$REPOS_DIR"

if [ ! -d "$REPOS_DIR/timecamp-cli/.git" ]; then
  git clone https://github.com/timecamp-org/timecamp-cli.git "$REPOS_DIR/timecamp-cli"
fi

if [ ! -d "$REPOS_DIR/good-enough-timecamp-data-pipeline/.git" ]; then
  git clone https://github.com/timecamp-org/good-enough-timecamp-data-pipeline.git "$REPOS_DIR/good-enough-timecamp-data-pipeline"
fi
```

## Tool 1: TimeCamp CLI (personal actions)

CLI at `~/utils/timecamp-cli`, installed globally via `npm link`.

| Intent | Command |
|--------|---------|
| Current timer status | `timecamp status` |
| Start timer | `timecamp start --task "Project A" --note "description"` |
| Stop timer | `timecamp stop` |
| Today's entries | `timecamp entries` |
| Entries by date | `timecamp entries --date 2026-02-04` |
| Entries date range | `timecamp entries --from 2026-02-01 --to 2026-02-04` |
| All users entries | `timecamp entries --from 2026-02-01 --to 2026-02-04 --all-users` |
| Add entry | `timecamp add-entry --date 2026-02-04 --start 09:00 --end 10:30 --duration 5400 --task "Project A" --note "description"` |
| Update entry | `timecamp update-entry --id 101234 --note "Updated" --duration 3600` |
| Remove entry | `timecamp remove-entry --id 101234` |
| List tasks | `timecamp tasks` |

## Tool 2: Data Pipeline (analytics & reports)

Python pipeline at `~/utils/good-enough-timecamp-data-pipeline`. **Use this for all analytics, reports, and bulk data fetching.**

### Run command

```bash
cd ~/utils/good-enough-timecamp-data-pipeline && \
uv run --with-requirements requirements.txt dlt_fetch_timecamp.py \
  --from YYYY-MM-DD --to YYYY-MM-DD \
  --datasets DATASETS \
  --format jsonl \
  --output ~/data/timecamp-data-pipeline
```

### Available datasets

| Dataset | Description |
|---------|-------------|
| `entries` | Time entries with project/task details |
| `tasks` | Projects & tasks hierarchy with breadcrumb paths |
| `computer_activities` | Desktop app tracking data |
| `users` | User details with group info and enabled status |
| `application_names` | Application lookup table (ID → name, category) |

### Formats: ``jsonl`

### Output structure

Files land in `~/data/timecamp-data-pipeline/timecamp/*.jsonl`.

### Examples

```bash
cd ~/utils/good-enough-timecamp-data-pipeline && \
uv run --with-requirements requirements.txt dlt_fetch_timecamp.py \
  --from 2026-02-11 --to 2026-02-14 \
  --datasets entries,users,tasks \
  --format jsonl --output ~/data/timecamp-data-pipeline

cd ~/utils/good-enough-timecamp-data-pipeline && \
uv run --with-requirements requirements.txt dlt_fetch_timecamp.py \
  --from 2026-01-01 --to 2026-02-14 \
  --datasets computer_activities,users,application_names \
  --format jsonl --output ~/data/timecamp-data-pipeline

cd ~/utils/good-enough-timecamp-data-pipeline && \
uv run --with-requirements requirements.txt dlt_fetch_timecamp.py \
  --from 2026-01-01 --to 2026-02-14 \
  --datasets computer_activities,users,application_names,entries,tasks \
  --format jsonl --output ~/data/timecamp-data-pipeline
```

## Analytics with DuckDB

Query the persistent data store directly.

```bash
DUCKDB=~/.duckdb/cli/latest/duckdb
DATA=~/data/timecamp-data-pipeline/timecamp

# Hours per person
$DUCKDB -c "
SELECT user_name, round(sum(TRY_CAST(duration AS DOUBLE))/3600.0, 1) as hours
FROM read_json_auto('$DATA/entries*.jsonl')
GROUP BY user_name ORDER BY hours DESC
"

# Hours per person per day
$DUCKDB -c "
SELECT user_name, date, round(sum(TRY_CAST(duration AS DOUBLE))/3600.0, 1) as hours
FROM read_json_auto('$DATA/entries*.jsonl')
GROUP BY user_name, date ORDER BY user_name, date
"

# Top applications by time (join activities with app names)
$DUCKDB -c "
SELECT COALESCE(an.full_name, an.application_name, an.app_name, 'Unknown') as app,
       round(sum(ca.time_span)/3600.0, 2) as hours
FROM read_json_auto('$DATA/computer_activities*.jsonl') ca
LEFT JOIN read_json_auto('$DATA/application_names*.jsonl') an
  ON ca.application_id = an.application_id
GROUP BY 1 ORDER BY hours DESC LIMIT 20
"

# People who logged < 30h in a given week
$DUCKDB -c "
SELECT user_name, round(sum(TRY_CAST(duration AS DOUBLE))/3600.0, 1) as hours
FROM read_json_auto('$DATA/entries*.jsonl')
WHERE date BETWEEN '2026-02-03' AND '2026-02-07'
GROUP BY user_name
HAVING sum(TRY_CAST(duration AS DOUBLE))/3600.0 < 30
ORDER BY hours
"
```

### Pattern

1. Check existing data range with DuckDB, if data is missing, fetch it with the pipeline, if it's already there, use it
2. Query with DuckDB: `$DUCKDB -c "SELECT ... FROM read_json_auto('$DATA/entries*.jsonl') ..."`

## Important Notes

- Duration (entries) is in seconds (3600 = 1h)
- `time_span` (activities) is also in seconds
- `applications_cache.json` in pipeline dir caches app name lookups
- For JSONL output, DuckDB glob `*.jsonl` catches all files for all datasets

## Safety

- Confirm before adding, updating, or removing entries
- Show the command before executing modifications
- When stopping a timer, show what was running first
