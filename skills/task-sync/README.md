English | [中文](README_CN.md)

# Task Sync

Bidirectional sync between **TickTick** and **Google Tasks** with smart list support.

Built as an [OpenClaw](https://openclaw.ai/) skill — runs automatically via cron or manually on demand.

## Features

- **Bidirectional list sync** — Google Task Lists and TickTick Projects are auto-matched by name or created as needed
- **Bidirectional task sync** — titles, completion status, notes/content
- **Priority mapping** — TickTick priority levels appear as Google task title prefixes (`[★]` high, `[!]` medium)
- **Smart lists** (one-way, TickTick → Google):
  - **Today** — overdue + today's tasks
  - **Next 7 Days** — upcoming week
  - **All** — every active task (with dates)
- **Date strategy** that prevents Google Calendar duplicates (see below)
- **Idempotent** — safe to run repeatedly without creating duplicates

## Date Strategy

Google Tasks with due dates automatically appear in Google Calendar. To prevent duplicates across lists, dates are handled carefully:

| List Type | Dates in Google | Reason |
|-----------|:-:|--------|
| Regular lists | No | Dates forwarded to TickTick, then cleared from Google |
| "All" smart list | Yes | Single Calendar source of truth |
| "Today" / "Next 7 Days" | No | Filtered views only |

## Architecture

```
sync.py                        Main sync orchestrator
utils/
  google_api.py                Google Tasks API wrapper (pagination, token refresh)
  ticktick_api.py              TickTick Open API wrapper
scripts/
  setup_google_tasks.py        Google OAuth setup
  setup_ticktick.py            TickTick OAuth setup
config.json                    Paths to tokens and data files
data/sync_db.json              Task/list mapping database (auto-generated)
data/sync_log.json             Sync statistics log (auto-generated)
e2e_test.py                    End-to-end test suite (15 tests)
```

### Sync Flow

```
1. List Sync (bidirectional)
   Google Lists <──────────> TickTick Projects
   - Match by name (case-insensitive)
   - "My Tasks" <-> "Inbox" (special case)
   - Unmatched lists create counterparts

2. Task Sync (bidirectional, per list pair)
   Google Tasks <──────────> TickTick Tasks
   - New tasks synced both ways
   - Completion propagated both ways
   - Dates: Google → TickTick (forwarded), then cleared from Google
   - Priority: TickTick → Google (title prefix)
   - Notes/content synced on creation

3. Smart Lists (one-way: TickTick → Google)
   TickTick ──────────────> Google "Today" / "Next 7 Days" / "All"
   - Stale tasks auto-removed when no longer matching
```

## Setup

### Prerequisites

- Python 3.10+
- Google Cloud project with Tasks API enabled
- TickTick developer app (from [developer.ticktick.com](https://developer.ticktick.com/))

### 1. Install dependencies

```bash
pip install google-auth google-auth-oauthlib google-api-python-client requests
```

### 2. Configure Google Tasks

```bash
python scripts/setup_google_tasks.py
```

Place your Google OAuth desktop client JSON at `config/google_credentials.json`
(or set `GOOGLE_CREDENTIALS_FILE`), then follow the OAuth flow.
The token is written to `config.json`'s `google_token` path when configured,
or `data/google_token.json` by default.

### 3. Configure TickTick

```bash
python scripts/setup_ticktick.py
```

Create `config/ticktick_creds.json` from `config/ticktick_creds.json.example`
(or set `TICKTICK_CREDENTIALS_FILE`), then follow the OAuth flow.
The token is written to `config.json`'s `ticktick_token` path when configured,
or `data/ticktick_token.json` by default.

### 4. Edit config.json

```json
{
  "google_token": "/path/to/google/token.json",
  "ticktick_token": "/path/to/ticktick/token.json",
  "sync_db": "/path/to/data/sync_db.json",
  "sync_log": "/path/to/data/sync_log.json",
  "ticktick_api_base": "https://api.ticktick.com/open/v1"
}
```

### 5. Run

```bash
python sync.py
```

## Automation

Set up a cron job for periodic sync:

```bash
# Every 10 minutes
*/10 * * * * /path/to/python /path/to/sync.py >> /path/to/sync.log 2>&1
```

Or use OpenClaw's built-in cron system for managed scheduling.

## Testing

The project includes a comprehensive end-to-end test suite that tests against live APIs:

```bash
python e2e_test.py
```

### Test Coverage (15 tests)

| # | Test | Direction |
|---|------|-----------|
| 1 | New task sync | Google → TickTick |
| 2 | New task sync | TickTick → Google |
| 3 | Completion sync | Google → TickTick |
| 4 | Completion sync | TickTick → Google |
| 5 | Due date forward & clear | Google → TickTick |
| 6 | Due date in "All" list only | TickTick → Google |
| 7 | "Today" smart list population | TickTick → Google |
| 8 | "Next 7 Days" smart list population | TickTick → Google |
| 9 | High priority `[★]` prefix | TickTick → Google |
| 10 | Smart list names don't leak to TickTick | Guard |
| 11 | Medium priority `[!]` prefix | TickTick → Google |
| 12 | Notes/content sync | Google → TickTick |
| 13 | Idempotency (no duplicates) | Both |
| 14 | New list → project creation | Google → TickTick |
| 15 | Stale smart list task removal | Cleanup |

## API References

- [Google Tasks REST API](https://developers.google.com/workspace/tasks/reference/rest)
- [TickTick Open API](https://developer.ticktick.com/)

## License

MIT
