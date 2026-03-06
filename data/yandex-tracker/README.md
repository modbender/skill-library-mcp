# Yandex Tracker skill for OpenClaw

Lets your OpenClaw agent work with [Yandex Tracker](https://tracker.yandex.ru) via the official Python client — no MCP server required.

## What the agent can do

- Get, create, update, and close issues
- Search with Tracker Query Language or structured filters
- Change issue status via transitions
- Add and read comments (with @-mentions and attachments)
- Log time (worklogs)
- Manage links between issues
- Bulk update, transition, or move issues across queues
- Read and write custom fields
- Find users by name or email, look up sprints and boards

## Prerequisites

Python 3 must be available in the agent's environment.

The skill declares a pip install step for `yandex_tracker_client` (from [PyPI](https://pypi.org/project/yandex-tracker-client/), official Yandex package). It is installed automatically when the skill is first used, or you can install it manually:

```bash
pip install yandex_tracker_client
```

## Setup

### 1. Get a Yandex OAuth token

Open [oauth.yandex.ru](https://oauth.yandex.ru) and create a **least-privilege** token with only Tracker read/write scope. For Yandex Cloud organizations you can use a **temporary IAM token** instead; prefer short-lived tokens where possible.

### 2. Find your organization ID

- **Yandex 360** — go to Tracker settings → Organization → copy the numeric org ID → use `TRACKER_ORG_ID`
- **Yandex Cloud** — copy the cloud org ID string → use `TRACKER_CLOUD_ORG_ID`

### 3. Declare and set credentials in OpenClaw

The skill requires `TRACKER_TOKEN` and one of `TRACKER_ORG_ID` or `TRACKER_CLOUD_ORG_ID` (declared in skill metadata). Add them to the `env` section of your `openclaw.json`:

```json
"env": {
  "TRACKER_TOKEN": "your_oauth_or_iam_token",
  "TRACKER_ORG_ID": "12345678"
}
```

For Yandex Cloud organizations use `TRACKER_CLOUD_ORG_ID` instead of `TRACKER_ORG_ID`.

## Usage examples

Once credentials are set, just ask the agent in natural language:

> «Покажи все задачи в очереди DEV, назначенные на меня»

> «Создай задачу в очереди BACKEND: "Migrate auth to OAuth 2.0", тип Task, приоритет Critical»

> «Закрой задачу DEV-42 с комментарием "Fixed in v3.1" и резолюцией fixed»

> «Сколько открытых задач в каждой очереди? Сгруппируй по исполнителям»

The agent writes and executes Python scripts using `yandex_tracker_client` to fulfil each request, aggregating data from multiple API calls into a single readable result.

## Full API reference

All available operations, field types, filter parameters, and error handling patterns are documented in `SKILL.md` inside the skill folder.
