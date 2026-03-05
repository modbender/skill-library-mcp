---
name: sentry
description: "Add observability to your OpenClaw instance — errors, logs, and traces sent to Sentry. Set up monitoring with the Sentry plugin, then investigate issues with the `sentry` CLI."
metadata:
  {
    "openclaw":
      {
        "emoji": "🐛",
        "requires": { "bins": ["sentry"] },
        "install":
          [
            {
              "id": "npm",
              "kind": "npm",
              "package": "sentry",
              "global": true,
              "bins": ["sentry"],
              "label": "Install Sentry CLI (npm)",
            },
          ],
      },
  }
---

# Sentry — OpenClaw Observability

See what your OpenClaw instance is doing: errors, structured logs, and performance traces — all in Sentry.

Two halves: **setup** (get telemetry flowing) and **investigation** (query it with the CLI).

---

## Setup

### 1. Authenticate

```bash
sentry auth login
```

OAuth device flow — follow the browser prompt. Credentials stored in `~/.sentry/cli.db`.

Alternatives (one-liners):
- `sentry auth login --token <TOKEN>` — paste an auth token directly
- `SENTRY_AUTH_TOKEN=<token>` — env var, useful in CI

### 2. Create a Project

Create a dedicated Sentry project for your OpenClaw instance:

```bash
sentry api /teams/<org>/<team>/projects/ \
  --method POST \
  --field name="my-openclaw" \
  --field platform=node
```

Don't know your org/team slugs? List them:

```bash
sentry api /organizations/                          # list orgs
sentry api /organizations/<org>/teams/              # list teams in org
```

### 3. Get the DSN

```bash
sentry project view <org>/my-openclaw --json | jq -r '.dsn'
```

Or via the keys endpoint:

```bash
sentry api /projects/<org>/my-openclaw/keys/ | jq '.[0].dsn.public'
```

### 4. Configure OpenClaw

Add the DSN to your `openclaw.json`:

```json
{
  "plugins": {
    "entries": {
      "sentry": {
        "enabled": true,
        "config": {
          "dsn": "https://examplePublicKey@o0.ingest.sentry.io/0",
          "enableLogs": true
        }
      }
    }
  }
}
```

> **Note:** Config goes under `plugins.entries.sentry.config`, not directly under `sentry`.

Then install the Sentry plugin. See `references/plugin-setup.md` for the full plugin implementation using `@sentry/node`.

> **Log buffer gotcha:** Sentry's structured logs buffer up to 100 items before auto-flushing. For low-volume services like OpenClaw, logs may sit in the buffer for a long time. The plugin should call `_INTERNAL_flushLogsBuffer(client)` periodically (e.g. every 30s) and before `Sentry.flush()` on shutdown. See `references/plugin-setup.md` for the implementation.

### 5. Verify

Restart your OpenClaw gateway, then check Sentry for incoming events:

```bash
sentry issue list <org>/my-openclaw --limit 5
```

---

## Investigation

Once telemetry is flowing, use the CLI to query your OpenClaw's errors, traces, and events.

### List Issues

```bash
sentry issue list <org>/<project>
sentry issue list <org>/<project> --query "is:unresolved" --sort freq --limit 20
sentry issue list <org>/                              # all projects in org
```

### View an Issue

```bash
sentry issue view <short-id>                          # e.g. MY-OPENCLAW-42
sentry issue view <short-id> --json                   # structured output
```

### AI Root Cause Analysis

```bash
sentry issue explain <issue-id>                       # Seer analyzes the root cause
sentry issue explain <issue-id> --force               # force fresh analysis
sentry issue plan <issue-id>                          # generate a fix plan (run explain first)
```

### Structured Logs

```bash
sentry log list <org>/<project>                       # last 100 logs
sentry log list <org>/<project> --limit 50            # last 50
sentry log list <org>/<project> -q 'level:error'      # filter by level
sentry log list <org>/<project> -q 'database'         # filter by message
sentry log list <org>/<project> -f                    # stream in real-time (2s poll)
sentry log list <org>/<project> -f 5                  # stream with 5s poll
sentry log list <org>/<project> --json                # structured output
```

View a specific log entry:

```bash
sentry log view <log-id>                              # 32-char hex ID
sentry log view <log-id> --json
sentry log view <log-id> --web                        # open in browser
```

### Inspect Events

```bash
sentry event view <event-id>                          # full stack trace + context
sentry event view <event-id> --json
```

### Direct API Calls

```bash
sentry api /projects/<org>/<project>/issues/ --paginate
sentry api /issues/<id>/ --method PUT --field status=resolved
sentry api /issues/<id>/ --method PUT --field assignedTo="user@example.com"
```

### Workflow: Investigate an Error

1. `sentry issue list <org>/<project> --query "is:unresolved" --sort date --limit 5`
2. `sentry issue view <short-id>` — context, affected users, timeline
3. `sentry issue explain <issue-id>` — AI root cause analysis
4. `sentry issue plan <issue-id>` — concrete fix steps
5. Fix → `sentry api /issues/<id>/ --method PUT --field status=resolved`

---

## Reference

- Full CLI commands: `references/cli-commands.md`
- Plugin implementation: `references/plugin-setup.md`
- CLI docs: https://cli.sentry.dev
- Sentry API: https://docs.sentry.io/api/
- Node SDK: https://docs.sentry.io/platforms/javascript/guides/node/
