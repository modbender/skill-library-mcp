# Session, Sandbox, Cron & Hooks Reference

Configuration for session management, code execution sandbox, job scheduling, and webhook receivers.

---

## Table of Contents
1. [Session Block](#session-block)
2. [Sandbox Block](#sandbox-block)
3. [Cron Block](#cron-block)
4. [Hooks Block](#hooks-block)

---

## Session Block

Controls conversation context scoping and automatic reset behavior.

```json5
session: {
  dmScope: "main",                    // Default agent for DMs
  threadBindings: {},                 // Thread-to-agent bindings
  reset: {
    mode: "daily",                    // daily | idle | never
    atHour: 4,                        // Hour for daily reset (0-23)
    idleMinutes: null                 // Minutes idle before reset (for idle mode)
  },
  resetByType: {},                    // Per-conversation-type reset overrides
  maintenance: {},                    // Session maintenance config
  agentToAgent: {},                   // Inter-agent session behavior
  sendPolicy: {}                      // Message send policies
}
```

### Session Reset Modes

| Mode | Behavior |
|------|----------|
| `daily` | Reset context at `atHour` every day. Agent starts fresh. |
| `idle` | Reset after `idleMinutes` of no messages. |
| `never` | Never auto-reset. Context grows indefinitely until manual `/new`. |

### Session Commands (from chat)

```
/new       - Start a new session (clear context)
/reset     - Alias for /new
/history   - Show session history
```

---

## Sandbox Block

Controls code execution isolation using Docker containers.

```json5
sandbox: {
  mode: "off",                        // off | non-main | all
  scope: "session",                   // session | agent | shared
  workspaceAccess: "none",           // none | ro | rw
  image: "openclaw-sandbox:bookworm-slim"
}
```

### Sandbox Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `off` | No sandboxing (default) | Trusted personal use |
| `non-main` | Sandbox all agents except main | Multi-user, trust main |
| `all` | Sandbox every agent including main | Maximum isolation |

**CRITICAL:** `mode: "all"` requires Docker to be installed and running. Gateway will fail if Docker is unavailable.

### Sandbox Scope

| Scope | Description |
|-------|-------------|
| `session` | New sandbox per conversation session (default) |
| `agent` | Shared sandbox per agent (persists across sessions) |
| `shared` | Single sandbox shared across all agents |

### Workspace Access

| Access | Description |
|--------|-------------|
| `none` | No workspace access from sandbox (default) |
| `ro` | Read-only workspace access |
| `rw` | Full read-write workspace access |

### Docker Configuration

```json5
sandbox: {
  mode: "all",
  docker: {
    // Docker-specific settings when sandbox is enabled
  }
}
```

---

## Cron Block

Built-in job scheduler within the Gateway.

```json5
cron: {
  enabled: true,
  store: "~/.openclaw/cron/jobs.json",
  maxConcurrentRuns: 1,              // Max jobs running simultaneously
  sessionRetention: {}               // How long to keep job session data
}
```

### Job Schema

Jobs are stored in `~/.openclaw/cron/jobs.json`:

```json
{
  "id": "morning-briefing",
  "name": "Morning Briefing",
  "schedule": {
    "kind": "cron",
    "expression": "0 9 * * 1-5"
  },
  "agentId": "main",
  "sessionTarget": "isolated",
  "prompt": "Give me my morning briefing.",
  "delivery": {
    "kind": "announce",
    "channel": "telegram",
    "peer": "@myusername"
  },
  "enabled": true,
  "maxRuntime": 300000,
  "retryOnFailure": false
}
```

### Schedule Kinds

| Kind | Format | Example |
|------|--------|---------|
| `at` | ISO 8601 datetime | `"2025-03-15T09:00:00Z"` |
| `every` | Milliseconds | `1800000` (30 minutes) |
| `cron` | 5-field cron expression | `"0 9 * * 1-5"` |

### Cron Expression Format

```
minute hour day-of-month month day-of-week
  0     9      *          *       1-5       = Weekdays at 9:00 AM
  */15  *      *          *       *         = Every 15 minutes
  0     */4    *          *       *         = Every 4 hours
  30    18     *          *       5         = Fridays at 6:30 PM
```

### Delivery Methods

| Kind | Description |
|------|-------------|
| `announce` | Send result to a specific channel/user |
| `webhook` | HTTP POST result to a URL |
| `none` | Run silently, no output |

### Cron CLI

```bash
openclaw cron list                   # List all jobs
openclaw cron add [options]          # Add a new job
openclaw cron run <id>               # Run a job now
openclaw cron runs <id>              # View run history
openclaw cron enable <id>            # Enable a job
openclaw cron disable <id>           # Disable a job
openclaw cron delete <id>            # Delete a job
openclaw cron status                 # Scheduler status
```

---

## Hooks Block

Webhook receiver for external event triggers.

```json5
hooks: {
  enabled: true,
  token: "shared-secret-token",      // Verification token
  path: "/hooks",                    // URL path prefix
  maxBodyBytes: 1048576,             // Max request body size (1MB default)

  presets: ["gmail"],                // Built-in presets

  mappings: [                        // Custom webhook mappings
    {
      path: "/hooks/github",
      agentId: "work",
      prompt: "A GitHub event arrived: {body}",
      secret: "github-webhook-secret"
    }
  ],

  gmail: {
    // Gmail-specific hook config (when "gmail" preset enabled)
  }
}
```

### Webhook URL

```
http://127.0.0.1:18789/hooks/<path>
```

For external access, use Tailscale Funnel, ngrok, or a public server.

### Built-in Presets

**Gmail:**
```json5
hooks: {
  presets: ["gmail"]
}
```

Setup: `openclaw webhooks gmail setup --account your@gmail.com`

### Custom Mappings

```json5
mappings: [
  {
    path: "/hooks/custom-event",
    agentId: "main",
    prompt: "An event arrived: {body}"
  },
  {
    path: "/hooks/stripe",
    agentId: "work",
    prompt: "Stripe event: {body}",
    filter: "$.type == 'payment_intent.succeeded'"
  }
]
```

### Template Variables

| Variable | Description |
|----------|-------------|
| `{body}` | Full JSON body |
| `{body.field}` | Specific field from body |
| `{headers.X-Custom}` | Request header value |

### Sending Webhooks

```bash
curl -X POST http://127.0.0.1:18789/hooks/custom-event \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer shared-secret-token" \
  -d '{"event": "order_placed", "amount": 99.99}'
```
