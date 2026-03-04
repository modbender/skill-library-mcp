---
name: indices
description: Use this skill for any operation with the Indices CLI — authentication, tasks, runs, and secrets.
---

# Indices CLI

## Global Flags

Available on every command:
- `--output markdown|json` (default: `markdown`) — use `json` for scripting
- `--api-base <url>` (default: `https://api.indices.io`)
- `--timeout <seconds>` (default: `30`)

---

## Auth

```bash
indices login                          # prompts securely for API key
indices login --api-key "<key>"        # non-interactive
indices auth-test                      # verify stored credentials
indices logout                         # remove stored API key
```

---

## Tasks

### Create

```bash
indices tasks create \
  --display-name "Apply to jobs" \
  --website "https://jobs.example.com" \
  --task "Fill and submit the form"
```

> **Never** set `is_fully_autonomous` to `true`.

After creation, the task requires manual completion in a browser. Direct the user to `https://platform.indices.io/tasks/{task_id}` (substituting the actual task ID).

Flags: `--display-name` (required), `--website` (required), `--task` (required), `--input-schema`, `--output-schema`, `--creation-params <json-object>`

### JSON input (alternative to flags)

```bash
indices tasks create --body '{"display_name":"...","website":"...","task":"..."}'
indices tasks create --file ./task.json
cat task.json | indices tasks create
```

Rules: use at most one of `--body`, `--file`, `--stdin`; do not mix with argument-mode flags.

### List / Get / Retry / Regenerate / Delete

```bash
indices tasks list
indices tasks list --status ready --limit 20   # statuses: not_ready | waiting_for_manual_completion | ready | failed
indices tasks get <task-uuid>
indices tasks retry <task-uuid>
indices tasks regenerate-api <task-uuid>
indices tasks delete <task-uuid>               # prompts for confirmation
indices tasks delete <task-uuid> --yes
```

Note: `--cursor` is unsupported and returns an error.

---

## Runs

### Create

```bash
indices runs create \
  --task-id "<task-uuid>" \
  --arguments '{"key":"value"}' \
  --secret-bindings '{"login":"<secret-uuid>"}'
```

Flags: `--task-id` (required), `--arguments <json-object>`, `--secret-bindings <json-object>`

JSON input follows the same rules as tasks create.

### List / Get

```bash
indices runs list --task-id <task-uuid>        # --task-id required
indices runs list --task-id <task-uuid> --limit 20
indices runs get <run-uuid>
```

---

## Secrets

```bash
indices secrets create MY_SECRET --value "..."   # explicit value
echo "..." | indices secrets create MY_SECRET --stdin
indices secrets create MY_SECRET                 # prompts securely
indices secrets list
indices secrets delete <secret-uuid>             # prompts for confirmation
indices secrets delete <secret-uuid> --yes
```

Empty secret values are rejected.
