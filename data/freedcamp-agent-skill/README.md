# Freedcamp skill for OpenClaw / Clawdbot

A dependency-free **AgentSkill** that integrates **Freedcamp** via the **Freedcamp REST API (v1)** using **HMAC-SHA1 secured credentials** (API Key + API Secret).

- No npm dependencies
- Node.js 18+ (uses built-in `fetch`, `crypto`)
- JSON-only output (designed for agent tool calls)
- Supports both:
  - Personal task management (my tasks / triage / notifications)
  - Project workflows (task creation, status updates, comments, task lists, groups)

## Repo layout

- `SKILL.md` -- skill instructions for the agent runtime
- `README.md` -- human-facing quickstart (this file)
- `AGENTS.md` -- agent-facing development guide
- `scripts/freedcamp.mjs` -- CLI (the only executable)
- `references/REFERENCE.md` -- implementation notes and API links
- `_meta.json` -- OpenClaw/ClawHub metadata

## Prerequisites

- Node.js **18+**
- A Freedcamp account
- Freedcamp **API Key** and **API Secret**

## Setup (API credentials)

1. Get your API Key and API Secret from your Freedcamp account settings https://freedcamp.com/manage/account#integrations-api.
2. Provide them to the runtime as `FREEDCAMP_API_KEY` and `FREEDCAMP_API_SECRET`.

### Recommended: store credentials in OpenClaw config (non-interactive)

This keeps secrets out of prompts and reduces accidental leakage.

**Recommended:**

```bash
openclaw config set skills.entries.freedcamp.enabled true
openclaw config set skills.entries.freedcamp.apiKey "YOUR_API_KEY"
openclaw config set skills.entries.freedcamp.env.FREEDCAMP_API_SECRET "YOUR_API_SECRET"
```

**Verify what is stored:**

```bash
openclaw config get skills.entries.freedcamp
openclaw config get skills.entries.freedcamp.enabled
openclaw config get skills.entries.freedcamp.apiKey
```

**Remove stored credentials:**

```bash
openclaw config unset skills.entries.freedcamp.apiKey
openclaw config unset skills.entries.freedcamp.env.FREEDCAMP_API_SECRET
```

### Local smoke test

```bash
export FREEDCAMP_API_KEY="YOUR_KEY"
export FREEDCAMP_API_SECRET="YOUR_SECRET"
node scripts/freedcamp.mjs me
```

## Common workflows

### 1) Discover your workspace

```bash
node scripts/freedcamp.mjs me
node scripts/freedcamp.mjs groups-projects
```

### 2) List tasks in a project

```bash
node scripts/freedcamp.mjs tasks --project <project_id> --all
```

### 3) List tasks with filters

```bash
node scripts/freedcamp.mjs tasks --project <project_id> --status in_progress,not_started --assigned_to 2,-1 --all
```

### 4) Get a single task with comments and files

```bash
node scripts/freedcamp.mjs task <task_id>
```

### 5) Create a task

```bash
node scripts/freedcamp.mjs create-task --project <project_id> --title "New task"
```

With description and task list:

```bash
node scripts/freedcamp.mjs create-task --project <project_id> --title "New task" --description "Details" --task_group <group_id>
```

### 6) Create a task by project name

```bash
node scripts/freedcamp.mjs create-task-by-name --project_name "My Project" --app_name "Tasks" --title "New task"
```

### 7) Update a task

```bash
node scripts/freedcamp.mjs update-task <task_id> --status completed
node scripts/freedcamp.mjs update-task <task_id> --title "Updated title" --status in_progress
```

### 8) Add a comment

Plain text (auto-wrapped in `<p>` tags):

```bash
node scripts/freedcamp.mjs comment <item_id> --app_name "Tasks" --text "My comment"
```

HTML:

```bash
node scripts/freedcamp.mjs comment <item_id> --app_name "Tasks" --html "<p>Bold <b>text</b></p>"
```

### 9) Task lists

```bash
node scripts/freedcamp.mjs task-lists --project <project_id>
```

### 10) Notifications

```bash
node scripts/freedcamp.mjs notifications
node scripts/freedcamp.mjs mark-read <notification_uid>
```

## Install as a local skill

OpenClaw loads skills from (highest precedence first):

1. `<workspace>/skills`
2. `~/.openclaw/skills`
3. bundled skills

Copy this folder into your workspace skills directory, e.g.:

`<your_openclaw_workspace>/skills/freedcamp/`

## Publishing to ClawHub

### Install the CLI

```bash
npm i -g clawhub
clawhub --help
```

### First-time publish (run from this folder)

```bash
clawhub publish . --slug freedcamp --name "Freedcamp" --version 1.0.0 --tags latest --changelog "Initial release"
```

## Troubleshooting

- **401 Unauthorized**: API key/secret missing or invalid. Verify `FREEDCAMP_API_KEY` and `FREEDCAMP_API_SECRET` are set correctly.
- **Comment formatting broken**: Ensure comments are wrapped in `<p>` tags. The CLI does this automatically for `--text` input.
- **Pagination**: Max 200 tasks per request. Use `--all` to auto-paginate or `--offset` for manual control.

See `references/REFERENCE.md` for links and implementation notes.
