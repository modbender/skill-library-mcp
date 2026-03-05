---
name: ms-todo-oauth
description: >
  A robust CLI skill to manage Microsoft To Do tasks via Microsoft Graph API.
  Supports full task lifecycle management including lists, tasks with priorities,
  due dates, reminders, recurrence patterns, views, search, and data export.
  Includes comprehensive test suite for reliability.
  THIS IS A REVISED OAUTH2-BASED VERSION OF ms-todo-sync with AI ASSISTANCE.
  ALL CREDITS TO THE ORIGINAL AUTHOR.
metadata:
  version: 1.0.3
  author: yalonghan@gmaill.com
  license: MIT License
  tags: [productivity, task-management, microsoft-todo, cli, graph-api, tested]
  category: productivity
  tested: true
  test_coverage: 29 comprehensive tests
---
# ms-todo-oauth

A fully-tested Microsoft To Do command-line client for managing tasks and lists via Microsoft Graph API.

## ⚠️This is a oauth based script. It contains a generated Azure Client ID and Secret ID

IF YOU WORRIED ABOUT YOUR PRIVACY, CONSIDER REPLACING THEM TO YOUR OWN IN `scripts\ms-todo-oauth.py`.
Just search for values below:

`client_id="ca6ec244……`

`client_secret="TwQ8Q……`

## ✨ Features

- ✅ **Full Task Management**: Create, complete, delete, and search tasks
- 🗂️ **List Organization**: Create and manage multiple task lists
- ⏰ **Rich Task Options**: Priorities, due dates, reminders, descriptions, tags
- 🔄 **Recurring Tasks**: Daily, weekly, monthly patterns with custom intervals
- 📊 **Multiple Views**: Today, overdue, pending, statistics
- 🔍 **Powerful Search**: Find tasks across all lists
- 💾 **Data Export**: Export all tasks to JSON
- 🧪 **Fully Tested**: 29 comprehensive automated tests
- 🌐 **Unicode Support**: Full support for Chinese characters and emojis

## Prerequisites

1. **Python >= 3.9** must be installed
2. **Working directory**: All commands MUST be run from the root of this skill (the directory containing this SKILL.md file)
3. **Network access**: Requires internet access to Microsoft Graph API endpoints
4. **Microsoft Account**: Personal Microsoft account (Hotmail, Outlook.com) or work/school account
5. **Authentication**: First-time use requires OAuth2 login via browser. See [Authentication](#authentication) section
   - **Token cache**: `~/.mstodo_token_cache.json` (persists across sessions, auto-refreshed)

## Installation & Setup

### First-Time Setup

Before using this skill for the first time, dependencies must be installed:

```bash
# Navigate to skill directory
cd <path-to-ms-todo-oauth>

# Create a venv in the project (creates '.venv' folder)
python3 -m venv .venv
# Activate the venv choose based on platforms:
#- Bash/Zsh: 
source .venv/bin/activate
# - Fish: 
source .venv/bin/activate.fish
#  - Windows (PowerShell):
.venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt

# Alternative (global python env, not recommended):
# pip install -r requirements.txt
```

**Dependencies:**

- `msal` (Microsoft Authentication Library) - Official Microsoft OAuth library
- `requests` - HTTP client for API calls
- Specified in `requirements.txt`

### Environment Verification

After installation, verify the setup:

```bash

# If using native venv (activate as above):
python3 scripts/ms-todo-oauth.py --help

# Expected: Command help text should be displayed
```

**Troubleshooting:**

- If `Python not found`, install Python 3.9 or higher from https://python.org


### Testing (Optional but Recommended)

Verify all functionality works correctly:

```bash
# Run comprehensive automated test suite (29 tests)
python3 test_ms_todo_oauth.py

# Expected: All tests pass (100% pass rate)
```

See [Testing](#testing) section for details.

### Security Notes

- Uses official Microsoft Graph API via Microsoft's `msal` library
- All code is plain Python (.py files), readable and auditable
- Tokens stored locally in `~/.mstodo_token_cache.json`
- All API calls go directly to Microsoft endpoints (graph.microsoft.com)
- OAuth2 standard authentication flow
- No third-party services involved

## Command Reference

All commands follow this pattern:

```
python3 scripts/ms-todo-oauth.py [GLOBAL_OPTIONS] <command> [COMMAND_OPTIONS]
```

### Global Options

| Option            | Description                                                                                                                         |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `-v, --verbose` | Show detailed information (IDs, dates, notes).**Must be placed BEFORE the subcommand.**                                       |
| `--debug`       | Enable debug mode to display API requests and responses. Useful for troubleshooting.**Must be placed BEFORE the subcommand.** |
| `--reauth`      | Force re-authentication by clearing the token cache and starting fresh login                                                        |

> ⚠️ **Common mistake**: Global options MUST come before the subcommand.
>
> - ✅ `python3 scripts/ms-todo-oauth.py -v lists`
> - ✅ `python3 scripts/ms-todo-oauth.py --debug add "Task"`
> - ❌ `python3 scripts/ms-todo-oauth.py lists -v`

---

### Authentication

Authentication uses OAuth2 authorization code flow, designed for both interactive and automated environments.

#### `login get` — Get OAuth2 authorization URL

```bash
python3 scripts/ms-todo-oauth.py login get
```

**Output example:**

```
======================================================================
🔐 OAuth2 Authorization Required
======================================================================

Please visit the following URL to authorize the application:

  https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?...

After authorization, you will be redirected to a callback URL.
Copy the 'code' parameter from the callback URL and run:

  ms-todo-oauth.py login verify <authorization_code>

======================================================================
```

**What to do:**

1. Open the provided URL in your browser
2. Sign in with your Microsoft account
3. Grant permissions when prompted
4. You'll be redirected to a URL like: `http://localhost:8000/callback?code=M.R3_BAY.abc123...`
5. Copy the entire code after `code=` (usually a long string starting with `M.R3_BAY.`)

**Agent behavior**: Present the URL to the user and explain they need to:

1. Visit the URL
2. Complete the login
3. Copy the authorization code from the callback URL
4. Provide it to you

#### `login verify` — Complete login with authorization code

```bash
python3 scripts/ms-todo-oauth.py login verify <authorization_code>
```

**Example:**

```bash
python3 scripts/ms-todo-oauth.py login verify "M.R3_BAY.abc123def456..."
```

**Output on success:**

```
✓ Authentication successful!
✓ Login information saved, you will be logged in automatically next time.
```

**Output on failure:**

```
❌ Token acquisition failed
Error: invalid_grant
Description: AADSTS54005: OAuth2 Authorization code was already redeemed...
```

**Exit code**: 0 on success, 1 on failure.

**Important notes:**

- Each authorization code can only be used ONCE
- If verification fails, you need to run `login get` again to get a new code
- Once successfully logged in, the token is cached and you won't need to login again unless:
  - You run `logout`
  - You run `--reauth`
  - The token expires and cannot be auto-refreshed

#### `logout` — Clear saved login

```bash
python3 scripts/ms-todo-oauth.py logout
```

Output: `✓ Login information cleared`

Only use when the user explicitly asks to switch accounts or clear login data. Under normal circumstances, the token is cached and login is automatic.

---

### List Management

#### `lists` — List all task lists

```bash
python3 scripts/ms-todo-oauth.py lists
python3 scripts/ms-todo-oauth.py -v lists  # with IDs and creation dates
```

**Output example:**

```
📋 Task Lists (3 total):

1. 任务
   ID: AQMkADAwATYwMAItYTQwZC04OThhLTAwAi0wMAoALgAAA0QJKpxW32BIsIlHaM...
   Created: 2024-12-15T08:30:00Z
2. Work
3. Shopping
```

#### `create-list` — Create a new list

```bash
python3 scripts/ms-todo-oauth.py create-list "<name>"
```

| Argument | Required | Description                                     |
| -------- | -------- | ----------------------------------------------- |
| `name` | Yes      | Name of the new list (supports Unicode/Chinese) |

**Example:**

```bash
python3 scripts/ms-todo-oauth.py create-list "项目 A"
```

Output: `✓ List created: 项目 A`

#### `delete-list` — Delete a list

```bash
python3 scripts/ms-todo-oauth.py delete-list "<name>" [-y]
```

| Argument/Option | Required | Description                |
| --------------- | -------- | -------------------------- |
| `name`        | Yes      | Name of the list to delete |
| `-y, --yes`   | No       | Skip confirmation prompt   |

> ⚠️ **This is a destructive operation**. Without `-y`, the command will prompt for confirmation. All tasks in the list will be deleted. Consider asking the user before deleting important lists.

Output: `✓ List deleted: <name>`

**Exit code**: 1 if list not found, 0 on success

---

### Task Operations

#### `add` — Add a new task

```bash
python3 scripts/ms-todo-oauth.py add "<title>" [options]
```

| Option                | Required | Default        | Description                                                                                                                                                                                                                             |
| --------------------- | -------- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `title`             | Yes      | —             | Task title (positional argument, supports Unicode/Chinese/emojis)                                                                                                                                                                       |
| `-l, --list`        | No       | (default list) | Target list name. If not specified, uses your Microsoft To Do default list.                                                                                                                                                             |
| `-p, --priority`    | No       | `normal`     | Priority:`low`, `normal`, `high`                                                                                                                                                                                                  |
| `-d, --due`         | No       | —             | Due date. Accepts days from now (`3` or `3d`) or date (`2026-02-15`). **Note:** Only date is supported by Microsoft To Do API, not time.                                                                                    |
| `-r, --reminder`    | No       | —             | Reminder datetime. Formats:`3h` (hours from now), `2d` (days from now), `2026-02-15 14:30` (date+time with space, needs quotes), `2026-02-15T14:30:00` (ISO format), `2026-02-15` (date only, defaults to 09:00).             |
| `-R, --recurrence`  | No       | —             | Recurrence pattern. Formats:`daily` (every day), `weekdays` (Mon-Fri), `weekly` (every week), `monthly` (every month). With interval: `daily:2` (every 2 days), `weekly:3` (every 3 weeks), `monthly:2` (every 2 months). |
| `-D, --description` | No       | —             | Task description/notes (supports multiline with quotes)                                                                                                                                                                                 |
| `-t, --tags`        | No       | —             | Comma-separated tags/categories (e.g.,`"work,urgent"`)                                                                                                                                                                                |
| `--create-list`     | No       | False          | Create the list if it doesn't exist (deprecated, lists auto-create now)                                                                                                                                                                 |

**Auto-created lists**: If the specified list doesn't exist, it will be automatically created.

**Output example:**

```
✓ Task added: Complete report
```

**With recurrence:**

```
✓ Task added: Daily standup
🔄 Recurring task created
```

**Examples:**

```bash
# Simple task
python3 scripts/ms-todo-oauth.py add "Buy milk" -l "Shopping"

# High priority task due in 3 days
python3 scripts/ms-todo-oauth.py add "Submit report" -l "Work" -p high -d 3

# Task with reminder in 2 hours
python3 scripts/ms-todo-oauth.py add "Call client" -r 2h

# Task with specific date and time reminder
python3 scripts/ms-todo-oauth.py add "Meeting" -d 2026-03-15 -r "2026-03-15 14:30"

# Daily recurring task
python3 scripts/ms-todo-oauth.py add "Daily standup" -l "Work" -R daily

# Weekday recurring task  
python3 scripts/ms-todo-oauth.py add "Gym" -R weekdays -l "Personal"

# Task with all options
python3 scripts/ms-todo-oauth.py add "Project Review" \
  -l "Work" \
  -p high \
  -d 7 \
  -r "2026-02-20 14:00" \
  -D "Review Q1 deliverables and prepare presentation" \
  -t "work,important,meeting"

# Chinese task with emoji
python3 scripts/ms-todo-oauth.py add "🎉 完成项目" -l "任务" -p high
```

#### `complete` — Mark a task as completed

```bash
python3 scripts/ms-todo-oauth.py complete "<title>" [-l "<list>"]
```

| Option         | Required | Default        | Description                      |
| -------------- | -------- | -------------- | -------------------------------- |
| `title`      | Yes      | —             | **Exact** task title       |
| `-l, --list` | No       | (default list) | List name where the task resides |

**Title matching**: Requires **exact match**. If unsure of exact title, use `search` first.

Output: `✓ Task completed: <title>`

**Exit code**: 1 if task not found, 0 on success

#### `delete` — Delete a task

```bash
python3 scripts/ms-todo-oauth.py delete "<title>" [-l "<list>"] [-y]
```

| Option         | Required | Default        | Description                      |
| -------------- | -------- | -------------- | -------------------------------- |
| `title`      | Yes      | —             | **Exact** task title       |
| `-l, --list` | No       | (default list) | List name where the task resides |
| `-y, --yes`  | No       | —             | Skip confirmation prompt         |

> ⚠️ **Destructive operation**. Without `-y`, will prompt for confirmation.

Output: `✓ Task deleted: <title>`

**Exit code**: 1 if task not found, 0 on success

---

### Task Views

#### `tasks` — List tasks in a specific list

```bash
python3 scripts/ms-todo-oauth.py tasks "<list>" [-a]
```

| Option        | Required | Description                                        |
| ------------- | -------- | -------------------------------------------------- |
| `list`      | Yes      | List name (exact match)                            |
| `-a, --all` | No       | Include completed tasks (default: incomplete only) |

**Output example:**

```
📋 Tasks in list "Work" (2 total):

1. [In Progress] Write documentation ⭐
2. [In Progress] Review PR
```

**With `-a` flag:**

```
📋 Tasks in list "Work" (3 total):

1. [In Progress] Write documentation ⭐
2. [Completed] Submit report
3. [In Progress] Review PR
```

**Exit code**: 1 if list not found, 0 on success

#### `pending` — All incomplete tasks across all lists

```bash
python3 scripts/ms-todo-oauth.py pending [-g]
```

| Option          | Required | Description           |
| --------------- | -------- | --------------------- |
| `-g, --group` | No       | Group results by list |

**Output example (with `-g`):**

```
📋 All incomplete tasks (3 total):

📂 Work:
  [In Progress] Write documentation ⭐
  [In Progress] Review PR

📂 Shopping:
  [In Progress] Buy groceries
```

**Without `-g`:**

```
📋 All incomplete tasks (3 total):

[In Progress] Write documentation ⭐
   List: Work
[In Progress] Review PR
   List: Work
[In Progress] Buy groceries
   List: Shopping
```

#### `today` — Tasks due today

```bash
python3 scripts/ms-todo-oauth.py today
```

Lists incomplete tasks with due date matching today's date.

**Output example:**

```
📅 Tasks due today (2 total):

[In Progress] Submit report ⭐
   List: Work
[In Progress] Buy groceries
   List: Shopping
```

If no tasks: `📅 No tasks due today`

#### `overdue` — Overdue tasks

```bash
python3 scripts/ms-todo-oauth.py overdue
```

Lists incomplete tasks past their due date, sorted by days overdue.

**Output example:**

```
⚠️  Overdue tasks (1 total):

[In Progress] Submit report ⭐
   List: Work
   Overdue: 3 days
```

If no overdue tasks: `✓ No overdue tasks`

#### `detail` — View full task details

```bash
python3 scripts/ms-todo-oauth.py detail "<title>" [-l "<list>"]
```

| Option         | Required | Default        | Description                                        |
| -------------- | -------- | -------------- | -------------------------------------------------- |
| `title`      | Yes      | —             | Task title (supports**partial/fuzzy match**) |
| `-l, --list` | No       | (default list) | List name                                          |

**Fuzzy matching**: Matches tasks containing the search string (case-insensitive).

When multiple tasks match:

- Prefers **incomplete** tasks over completed
- Returns most recently modified task

**Output example:**

```
============================================================
📌 Task Details
============================================================

📋 Title: Complete Q1 Report
🔖 Status: [In Progress]
⚡ Priority: ⭐ High
📅 Created: 2026-01-15 08:30:00
📝 Modified: 2026-02-10 14:22:00
⏰ Due: 2026-02-20 00:00:00
🔔 Reminder: 2026-02-20 09:00:00

📝 Notes:
- Review sales figures
- Include charts
- Prepare for board meeting

🏷️  Categories: work, important, Q1

🔄 Recurrence:
   Every week on Monday
   Start date: 2026-02-17
   No end date

============================================================
```

#### `search` — Search tasks by keyword

```bash
python3 scripts/ms-todo-oauth.py search "<keyword>"
```

Searches across **all lists** in both task titles and descriptions (case-insensitive).

**Output example:**

```
🔍 Search results for "report" (2 found):

[In Progress] Complete Q1 Report ⭐
   List: Work
   Notes: Review sales figures...

[Completed] Submit weekly report
   List: Work
```

#### `stats` — Task statistics

```bash
python3 scripts/ms-todo-oauth.py stats
```

Shows aggregate statistics across all lists.

**Output example:**

```
📊 Task Statistics:

  Total lists: 3
  Total tasks: 15
  Completed: 10
  Pending: 5
  High priority: 2
  Overdue: 1

  Completion rate: 66.7%
```

#### `export` — Export all tasks to JSON

```bash
python3 scripts/ms-todo-oauth.py export [-o "<filename>"]
```

| Option           | Required | Default              | Description      |
| ---------------- | -------- | -------------------- | ---------------- |
| `-o, --output` | No       | `todo_export.json` | Output file path |

Exports complete task data from all lists in JSON format.

**Output:** `✓ Tasks exported to: <filename>`

**JSON structure:**

```json
{
  "Work": [
    {
      "id": "AQMkADAwATYwMAItYTQw...",
      "title": "Complete report",
      "status": "notStarted",
      "importance": "high",
      "createdDateTime": "2026-01-15T08:30:00Z",
      "dueDateTime": {
        "dateTime": "2026-02-20T00:00:00.0000000",
        "timeZone": "UTC"
      },
      "body": {
        "content": "Review Q1 numbers",
        "contentType": "text"
      },
      "categories": ["work", "important"]
    }
  ],
  "Shopping": [...]
}
```

---

## Error Handling

### Exit Codes

| Code  | Meaning                                                                   |
| ----- | ------------------------------------------------------------------------- |
| `0` | Success                                                                   |
| `1` | Failure (not logged in, API error, invalid arguments, resource not found) |
| `2` | Invalid command-line arguments                                            |

### Common Error Messages

| Error                                           | Cause                             | Resolution                                                                  |
| ----------------------------------------------- | --------------------------------- | --------------------------------------------------------------------------- |
| `❌ Not logged in`                            | No cached token or token expired  | Run `login get` then `login verify <code>`                              |
| `ModuleNotFoundError: No module named 'msal'` | Dependencies not installed        | Run `pip install -r requirements.txt`                      |
| `❌ List not found: <name>`                   | Specified list does not exist     | Check list name with `lists` command. Note: exact match required.         |
| `❌ Task not found: <name>`                   | No task with exact matching title | Use `search` to find exact title, or `tasks "<list>"` to list all tasks |
| `❌ Error: Invalid isoformat string`          | DateTime parsing error            | This should not occur in v1.1.0+. If you see this, report as bug.           |
| `❌ Error: Unsupported HTTP method`           | Internal API error                | This should not occur in v1.1.0+. If you see this, report as bug.           |
| `❌ Error: <API error message>`               | Microsoft Graph API error         | Retry; check network; use `--debug` for full details                      |
| `Network error` / `Connection timeout`      | No internet or API unreachable    | Check network connection; verify access to graph.microsoft.com              |

---

## Testing

This skill includes a comprehensive test suite to ensure reliability.

### Automated Testing

Run the full test suite:

```bash
cd <skill-directory>
python3 test_ms_todo_oauth.py
```

**Prerequisites:**

- Must be authenticated (logged in) before running tests
- Internet connection required
- Approximately 2-3 minutes to complete

**Test Coverage** (29 tests):

- ✅ Authentication (login/logout)
- ✅ List management (create, delete, list)
- ✅ Basic task operations (add, complete, delete, list)
- ✅ Task options (priorities, due dates, reminders, descriptions, tags)
- ✅ Recurring tasks (daily, weekly, weekdays, monthly, custom intervals)
- ✅ Task views (today, overdue, pending, search, stats)
- ✅ Data export and validation
- ✅ Error handling (non-existent resources)
- ✅ Unicode support (Chinese characters, emojis)

**Expected output:**

```
========================================================================
TEST SUMMARY
========================================================================

Total tests: 29
Passed: 29
Failed: 0
Pass rate: 100.0%

========================================================================
🎉 ALL TESTS PASSED! 🎉
========================================================================
```

### Manual Testing

For manual verification, see `MANUAL_TEST_CHECKLIST.txt` which provides:

- Step-by-step test procedures
- Expected outcomes
- 9 test categories covering all functionality

### Test Cleanup

The automated test suite:

- Creates a temporary test list (e.g., `🧪 Test List 14:23:45`)
- Runs all tests in isolation
- Deletes the test list on completion
- Cleans up any temporary files

If tests are interrupted, you may need to manually delete leftover test lists.

---

## Agent Usage Guidelines

### Critical Rules

1. **Working directory**: Always `cd` to the directory containing this SKILL.md before running commands.
2. **Dependency installation**: Before first use or when encountering import errors, ensure all dependencies are installed.
3. **Check authentication first**: Before any operation, verify authentication status:

   ```bash
   python3 scripts/ms-todo-oauth.py lists
   ```

   If this returns "Not logged in" error (exit code 1), initiate the login flow.
4. **Task list organization**: When adding tasks:

   - First, run `lists` to see available task lists
   - If user doesn't specify a list, tasks will be added to their **default list** (usually "Tasks" or "任务")
   - Intelligently categorize tasks into appropriate lists:
     - Work tasks → "Work" list
     - Personal errands → "Personal" or default list
     - Shopping → "Shopping" list
     - Project-specific → Use project name as list
   - Lists will be auto-created if they don't exist
   - Support Chinese list names and Unicode characters
5. **Destructive operations**: For `delete` and `delete-list`:

   - These commands prompt for confirmation by default (blocking behavior)
   - Use `-y` flag ONLY when:
     - User has explicitly requested to delete without confirmation
     - The deletion intent is unambiguous and confirmed through conversation
   - When in doubt, ask the user for confirmation instead of using `-y`
   - These operations return exit code 1 on failure (resource not found)
6. **Global option placement**: `-v`, `--debug`, and `--reauth` must come BEFORE the subcommand:

   - ✅ `python3 scripts/ms-todo-oauth.py -v lists`
   - ❌ `python3 scripts/ms-todo-oauth.py lists -v`
7. **Login flow**:

   - Do NOT call `login verify` until user confirms they've completed browser authentication
   - Each authorization code can only be used once
   - If verify fails, you must run `login get` again for a new code
8. **Error handling**:

   - Check exit codes: 0 = success, 1 = failure, 2 = invalid arguments
   - Parse error messages to provide helpful guidance
   - Use `--debug` flag when troubleshooting API issues

### Recommended Workflow for Agents

```
Step 1: Setup and Authentication Check
---------------------------------------
cd <skill_directory>

python3 scripts/ms-todo-oauth.py lists          # Test auth & see available lists

If exit code is 1 and output contains "Not logged in":
  a. python3 scripts/ms-todo-oauth.py login get
  b. Present URL to user
  c. Explain: "Visit this URL, login, and copy the 'code' parameter from callback URL"
  d. Wait for user to provide authorization code
  e. python3 scripts/ms-todo-oauth.py login verify "<code>"
  f. Verify success (exit code 0)

Step 2: Task Analysis and List Selection
-----------------------------------------
When user requests to add task(s):
  a. Analyze task context from user's description
  b. Review available lists (from Step 1 output)
  c. Choose appropriate list or use default:
     - Work-related → "Work"
     - Personal errands → "Personal" or default
     - Shopping items → "Shopping"
     - Project-specific → "<ProjectName>"
  d. If list doesn't exist, it will be auto-created

Step 3: Execute Operation
--------------------------
Add task with appropriate options:
  python3 scripts/ms-todo-oauth.py add "Task Title" \
    -l "Work" \
    -p high \
    -d 3 \
    -r 2h \
    -D "Detailed description" \
    -t "tag1,tag2"

Step 4: Verify and Report
--------------------------
Check exit code:
  - 0: Success → Confirm to user
  - 1: Failure → Parse error, provide guidance
  - 2: Invalid args → Fix command syntax

Optionally verify:
  python3 scripts/ms-todo-oauth.py tasks "<list>"  # Show updated list
```

### Task Title Matching Rules

- **Exact match required**: `complete`, `delete` commands
- **Partial/fuzzy match supported**: `detail`, `search` commands
- **Case-insensitive**: All search operations
- **Best practice**: Use `search` first to find exact title, then use it in subsequent commands

**Example workflow:**

```bash
# Find task with fuzzy search
python3 scripts/ms-todo-oauth.py search "report"
# Output shows: "Complete Q1 Report"

# Use exact title from search results
python3 scripts/ms-todo-oauth.py complete "Complete Q1 Report" -l "Work"
```

### Default List Behavior

- When `-l` is not specified, operations use the Microsoft To Do default list
- The default list is typically named "Tasks" (English) or "任务" (Chinese)
- To target a specific list, always provide `-l "<ListName>"`

### Example Task Categorization

**User request:** "Add these tasks: buy milk, finish report, call dentist"

**Agent approach:**

```bash
# First check available lists
python3 scripts/ms-todo-oauth.py lists

# Categorize intelligently:
python3 scripts/ms-todo-oauth.py add "Buy milk" -l "Shopping"
python3 scripts/ms-todo-oauth.py add "Finish report" -l "Work" -p high -d 2
python3 scripts/ms-todo-oauth.py add "Call dentist" -l "Personal"
# Or use default list if no specific context: add "Call dentist"
```

---

## Quick Reference

### Common Workflows

**Daily task review:**

```bash
python3 scripts/ms-todo-oauth.py today          # Check today's tasks
python3 scripts/ms-todo-oauth.py overdue        # Check overdue tasks
python3 scripts/ms-todo-oauth.py -v pending -g  # Review all pending, grouped
```

**Adding various task types:**

```bash
# Simple task (default list)
python3 scripts/ms-todo-oauth.py add "Buy milk"

# Work task with priority and deadline
python3 scripts/ms-todo-oauth.py add "Quarterly review" -l "Work" -p high -d 7

# Task with reminder
python3 scripts/ms-todo-oauth.py add "Call client" -r 3h

# Detailed task with all options
python3 scripts/ms-todo-oauth.py add "Project meeting" \
  -l "Work" \
  -p high \
  -d 2026-03-15 \
  -r "2026-03-15 14:30" \
  -D "Discuss Q1 goals and resource allocation" \
  -t "meeting,important,Q1"

# Recurring tasks
python3 scripts/ms-todo-oauth.py add "Daily standup" -R daily -l "Work"
python3 scripts/ms-todo-oauth.py add "Weekly review" -R weekly -d 7
python3 scripts/ms-todo-oauth.py add "Gym" -R weekdays -l "Personal"
python3 scripts/ms-todo-oauth.py add "Monthly report" -R monthly -p high
```

**Task completion workflow:**

```bash
# Search for task
python3 scripts/ms-todo-oauth.py search "report"

# Complete using exact title from search results
python3 scripts/ms-todo-oauth.py complete "Quarterly review" -l "Work"
```

**Data management:**

```bash
# Export for backup
python3 scripts/ms-todo-oauth.py export -o "backup_$(date +%Y%m%d).json"

# View statistics
python3 scripts/ms-todo-oauth.py stats
```

---

## Changelog

### Version 1.1.0 (Current)

- ✅ **Fixed**: DateTime parsing errors (Microsoft's 7-decimal format)
- ✅ **Fixed**: HTTP method parameter order bugs
- ✅ **Fixed**: Missing `start_date` parameter in `create_task()`
- ✅ **Fixed**: Missing `complete_task()` method
- ✅ **Fixed**: Error exit codes now correctly return 1 on failure
- ✅ **Added**: Comprehensive test suite (29 automated tests)
- ✅ **Added**: Better error messages and troubleshooting
- ✅ **Improved**: OAuth2 authentication flow documentation
- ✅ **Improved**: Unicode and emoji support documentation
- ✅ **Improved**: Agent usage guidelines

### Version 1.0.2 (Previous)

- Initial release with OAuth2 authentication
- Basic task and list management
- Recurring task support
- Multiple task views
- Data export functionality

---

## Troubleshooting

### Authentication Issues

**Problem:** `❌ Not logged in`

- **Solution**: Run `login get`, complete browser flow, then `login verify <code>`

**Problem:** `❌ Token acquisition failed: invalid_grant`

- **Cause**: Authorization code already used or expired
- **Solution**: Run `login get` again to get a fresh code

**Problem:** Login worked but now getting "Not logged in" again

- **Cause**: Token expired and auto-refresh failed
- **Solution**: Run `--reauth` to force fresh login:
  ```bash
  python3 scripts/ms-todo-oauth.py --reauth lists
  ```

### Import/Dependency Issues

**Problem:** `ModuleNotFoundError: No module named 'msal'`

- **Solution**: Install dependencies: `pip install -r requirements.txt`

### API/Network Issues

**Problem:** Connection timeout or network errors

- **Check**: Internet connection
- **Check**: Can you access https://graph.microsoft.com in browser?
- **Try**: Using `--debug` flag to see full API request/response

**Problem:** Unexpected API errors

- **Try**: Re-authenticate: `python3 scripts/ms-todo-oauth.py --reauth lists`
- **Try**: Debug mode: `python3 scripts/ms-todo-oauth.py --debug <command>`

### Task/List Not Found

**Problem:** `❌ Task not found: <title>`

- **Solution**: Use `search` to find exact title
- **Note**: `complete` and `delete` require exact title match

**Problem:** `❌ List not found: <name>`

- **Solution**: Run `lists` to see exact list names
- **Note**: List names are case-sensitive

### Test Failures

**Problem:** Tests failing with datetime errors

- **Solution**: Ensure you've applied all v1.1.0 fixes
- **Check**: Verify `_parse_ms_datetime()` helper function exists

**Problem:** Tests failing with "Not logged in"

- **Solution**: Authenticate before running tests:
  ```bash
  python3 scripts/ms-todo-oauth.py login get
  # Complete browser flow
  python3 scripts/ms-todo-oauth.py login verify <code>
  # Then run tests
  python3 test_ms_todo_oauth.py
  ```

---

## Additional Resources

- **Test Suite**: `test_ms_todo_oauth.py` - Automated tests
- **Manual Tests**: `MANUAL_TEST_CHECKLIST.txt` - Step-by-step testing guide
- **Quick Reference**: `QUICK_REFERENCE.txt` - Command cheat sheet
- **Bug Fixes**: `COMPLETE_FIX_PATCH.txt` - Documentation of v1.1.0 fixes

---

## Support & Contributing

**Reporting Issues:**

- Provide error message and command used
- Include output from `--debug` flag if applicable
- Note your Python version: `python3 --version`
- Note your OS: Windows/Mac/Linux

**Testing New Features:**

- Always run the test suite after code changes
- Add new test cases to `test_ms_todo_oauth.py` for new features
- Update `MANUAL_TEST_CHECKLIST.txt` with manual test procedures

---

## License

MIT License - See LICENSE file for details

---

**Version**: 1.1.0
**Last Updated**: 2026-02-13
**Status**: ✅ Fully Tested & Production Ready
