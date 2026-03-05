---
name: Honeydew
description: Manage HoneyDew Kanban boards, cards, and labels via the REST API.
homepage: https://github.com/smartify-inc/Honeydew
metadata: {"openclaw": {"emoji": "📋"}}
---

# HoneyDew

Use this skill when the user asks you to manage tasks, boards, cards, columns, or labels on their HoneyDew Kanban board.

## When to use

- Creating, updating, moving, or deleting cards (tasks)
- Listing boards, columns, or cards
- Transferring cards between user and agent profiles
- Managing labels (create, assign, remove)
- Checking board summaries, overdue cards, or urgent items
- Moving cards across boards

## Tracking tasks

The user can open the HoneyDew board in their browser (`http://localhost:5173`) to see all tasks, their status, and what work the agent has completed. Encourage the user to check the board regularly for updates.

## Assigning work to the user

When you need something from the user — a review, approval, input, or any manual step — create a task (or transfer an existing one) to the user's profile. It will appear on their board so they know action is needed. Let the user know you have assigned them a task and they should check HoneyDew.

## Connection

- **Base URL:** `http://localhost:8000` (override with env `SMARTIFY_API_URL`)
- **Docs URL:** If optionally enabled by the user `http://localhost:8001' (override with env `SMARTIFY_DOCS_URL`)
- **Auth:** None (local app, no API key required)
- **Health check:** `GET /health` — returns `{"status": "healthy"}` when the backend is running

If the API is not reachable, ask the user to start HoneyDew (`./start.sh` in the project root).

## API reference

All endpoints are prefixed with `/api`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/boards | List all boards |
| POST | /api/boards | Create a board (optional `columns` array) |
| GET | /api/boards/{id} | Get board with columns and cards |
| DELETE | /api/boards/{id} | Delete a board |
| POST | /api/columns | Create a column (`board_id`, `name`) |
| PATCH | /api/columns/{id} | Update column name or position |
| DELETE | /api/columns/{id} | Delete a column |
| GET | /api/cards | List cards (filters: `board_id`, `column_id`, `priority`, `has_due_date`) |
| POST | /api/cards | Create a card (`column_id`, `title`, `priority`, `profile`, optional `description`, `due_date`) |
| GET | /api/cards/{id} | Get card details |
| PATCH | /api/cards/{id} | Update card fields |
| DELETE | /api/cards/{id} | Delete a card |
| POST | /api/cards/{id}/move | Move card (`column_id`, `position`) |
| POST | /api/cards/{id}/move-to-board | Move card to another board (`board_id`, optional `column_name`) |
| POST | /api/cards/{id}/transfer | Transfer card to another profile (`target_profile`) |
| GET | /api/labels | List all labels |
| POST | /api/labels | Create a label (`name`, `color`) |
| POST | /api/cards/{id}/labels/{label_id} | Add label to card |
| DELETE | /api/cards/{id}/labels/{label_id} | Remove label from card |
| GET | /api/cards/{id}/comments | List comments on a card |
| POST | /api/cards/{id}/comments | Add a comment (`body`, optional `profile`) |

Priority values: 1 = Low, 2 = Medium, 3 = High, 4 = Urgent.

## Examples

### Create a task

```bash
curl -X POST http://localhost:8000/api/cards \
  -H "Content-Type: application/json" \
  -d '{"column_id": 1, "title": "Write docs", "priority": 2, "profile": "jarvis"}'
```

### Move a card to "In Progress"

First find the column ID:

```bash
curl http://localhost:8000/api/boards/1
```

Then move:

```bash
curl -X POST http://localhost:8000/api/cards/3/move \
  -H "Content-Type: application/json" \
  -d '{"column_id": 2, "position": 0}'
```

### Transfer a card to the user

```bash
curl -X POST http://localhost:8000/api/cards/3/transfer \
  -H "Content-Type: application/json" \
  -d '{"target_profile": "tony"}'
```

## Python tools (optional)

If the user has the HoneyDew repo, `tools/kanban_tools.py` provides a higher-level Python interface:

```python
from kanban_tools import KanbanTools, Priority

kanban = KanbanTools()
card = kanban.create_task(title="Write docs", priority=Priority.HIGH)
kanban.move_card_to_column(card["id"], board_id=1, column_name="In Progress")
kanban.assign_to_user(card["id"])
kanban.mark_done(card["id"])
```

Key convenience methods: `create_task`, `assign_to_user`, `assign_to_agent`, `move_card_to_column`, `move_card_to_board`, `mark_todo`, `mark_in_progress`, `mark_blocked`, `mark_done`, `get_board_summary`, `get_overdue_cards`, `get_urgent_cards`.

## Task comments

Both users and agents can add comments to any task. Comments are visible in the task detail view in the UI. **Always add a comment when:**

- **You are blocked**: Explain specifically what you need from the user (e.g. "Need API credentials for the staging environment before I can proceed").
- **You complete a task**: Leave a brief summary of what you did and any decisions you made (e.g. "Refactored auth module into middleware, added 12 unit tests, all passing").
- **You need review or input**: Describe what to look at and any open questions.
- **You hand off work**: Note the current state so the next person (user or agent) has context.

```bash
curl -X POST http://localhost:8000/api/cards/3/comments \
  -H "Content-Type: application/json" \
  -d '{"body": "Finished the first pass, needs review.", "profile": "jarvis"}'
```

## Agent completion metadata

When you complete a task, you may report completion metadata via `PATCH /api/cards/{id}`. These optional fields are displayed in the HoneyDew UI on the task detail:

| Field | Type | Description |
|-------|------|-------------|
| `agent_tokens_used` | int | Tokens consumed |
| `agent_model` | string | Model name (e.g. `gpt-4o`) |
| `agent_execution_time_seconds` | float | Execution time in seconds |
| `agent_started_at` | string | ISO 8601 datetime when work started |
| `agent_completed_at` | string | ISO 8601 datetime when work finished |

Example with Python tools:

```python
kanban.mark_done(
    card["id"],
    agent_tokens_used=4200,
    agent_model="gpt-4o",
    agent_execution_time_seconds=12.8,
    agent_started_at="2026-02-22T10:30:00Z",
    agent_completed_at="2026-02-22T10:30:12Z",
)
```

Or via curl after moving to Done:

```bash
curl -X PATCH http://localhost:8000/api/cards/5 \
  -H "Content-Type: application/json" \
  -d '{"agent_tokens_used": 4200, "agent_model": "gpt-4o", "agent_execution_time_seconds": 12.8, "agent_started_at": "2026-02-22T10:30:00Z", "agent_completed_at": "2026-02-22T10:30:12Z"}'
```
