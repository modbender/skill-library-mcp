---
name: scheduler
description: "Schedule tasks and commands to run at specific times. Execute shell commands, agent tasks, API calls, and automations on a cron schedule. Tested on Telegram & Discord."
tags: [cron, scheduler, automation, tasks, commands, telegram, discord]
metadata:
  openclaw:
    summary: "**Scheduler:** Run commands and tasks on a schedule — shell scripts, agent tasks, API calls, file ops. Natural language, native cron, zero dependencies."
    emoji: "calendar"
user-invocable: true
command-dispatch: prompt
---

# Scheduler

Execute tasks and commands on a schedule using natural language. Run shell commands, agent tasks, API health checks, file operations, and automations — one-shot or recurring.

## Usage

```
/schedule run npm test in 5 minutes
/schedule git pull origin main tomorrow at 6am
/schedule generate weekly sales report every monday at 9am
/schedule check https://api.example.com/health every 30m
/schedule clean /tmp files every day at 3am silently
/schedule back up database every sunday at 2am
/schedule restart server in 10 minutes silently
/schedule list
/schedule cancel <jobId>
```

## Agent Instructions

When the user triggers `/schedule`, determine the intent:

- **list** → call `cron.list` and show active scheduled tasks.
- **cancel / delete / remove `<jobId>`** → call `cron.remove` with that jobId.
- **everything else** → create a new scheduled task (steps below).

---

### Step 1: Parse the Input

Extract four things: **WHAT** (the task to execute), **WHEN** (the time), **RECURRENCE** (one-shot or recurring), **DELIVERY** (announce results or run silently).

#### Identify the Task (WHAT)

Classify the user's request into a task type:

| Task Type | Trigger Words | Agent Action |
|---|---|---|
| Shell command | `run`, `execute`, `do`, command-like syntax (`npm`, `git`, `docker`, `curl`, `python`) | Execute the command using Bash tool |
| Agent task | `generate`, `summarize`, `analyze`, `write`, `create`, `compile`, `review` | Perform the task using available agent tools |
| API/health check | `check`, `ping`, `hit`, `call`, URL patterns (`https://...`) | Fetch the URL and report status |
| File operation | `clean`, `back up`, `copy`, `move`, `archive`, `compress` | Perform file operations using available tools |
| Custom prompt | anything else | Execute as a free-form agent prompt |

The WHAT becomes the `payload.message` — a clear instruction for the agent that wakes up to execute it.

#### Identify the Time (WHEN)

Use the same time-parsing pipeline as the remindme skill:

**Layer 1: Pattern Matching**

Scan for these patterns (first match wins):

**Relative durations** — `in <number> <unit>`:
| Pattern | Duration |
|---|---|
| `in Ns`, `in N seconds` | N seconds |
| `in Nm`, `in N min`, `in N minutes` | N minutes |
| `in Nh`, `in N hours` | N hours |
| `in Nd`, `in N days` | N * 24 hours |
| `in Nw`, `in N weeks` | N * 7 days |

**Absolute clock times** — `at <time>`:
| Pattern | Meaning |
|---|---|
| `at HH:MM`, `at H:MMam/pm` | Today at that time (or tomorrow if past) |
| `at Ham/pm`, `at HH` | Today at that hour |

**Named days**:
| Pattern | Meaning |
|---|---|
| `tomorrow` | Next calendar day, default 9am |
| `tonight` | Today at 8pm |
| `next monday..sunday` | Coming occurrence, default 9am |

**Recurring** — `every <pattern>`:
| Pattern | Schedule |
|---|---|
| `every Nm/Nh/Nd` | `kind: "every"`, `everyMs: N * unit_ms` |
| `every day at <time>` | `kind: "cron"`, `expr: "M H * * *"` |
| `every <weekday> at <time>` | `kind: "cron"`, `expr: "M H * * DOW"` |
| `every weekday at <time>` | `kind: "cron"`, `expr: "M H * * 1-5"` |
| `every weekend at <time>` | `kind: "cron"`, `expr: "M H * * 0,6"` |
| `every hour` | `kind: "every"`, `everyMs: 3600000` |

**Unit conversion table**:
| Unit | Milliseconds |
|---|---|
| 1 second | 1000 |
| 1 minute | 60000 |
| 1 hour | 3600000 |
| 1 day | 86400000 |
| 1 week | 604800000 |

**Layer 2: Slang & Shorthand**

| Phrase | Resolves to |
|---|---|
| `in a bit`, `shortly` | 30 minutes |
| `in a while` | 1 hour |
| `later`, `later today` | 3 hours |
| `end of day`, `eod` | Today 5pm |
| `end of week`, `eow` | Friday 5pm |
| `morning` | 9am |
| `afternoon` | 2pm |
| `evening` | 6pm |
| `midnight` | 12am next day |
| `noon` | 12pm |

**Layer 3: Ambiguity — Ask, Don't Guess**

If you can't determine WHEN, ask the user. Never silently pick a default time.

#### Identify Delivery Mode (DELIVERY)

| User says | Delivery mode |
|---|---|
| `silently`, `quietly`, `in background`, `no output` | `"none"` — runs without reporting back |
| Nothing specified, or `report`, `show results`, `announce` | `"announce"` — sends task output to channel |

### Step 2: Compute the Schedule

**Timezone rule:** ALWAYS use the user's **local timezone** (system timezone). Never default to UTC.

**One-shot** → ISO 8601 timestamp with the user's local timezone offset.
- If the computed time is in the PAST, bump to the next occurrence.

**Recurring (cron)** → 5-field cron expression with `tz` set to the user's IANA timezone.

**Recurring (interval)** → `kind: "every"` with `everyMs` in milliseconds.

### Step 3: Security Check

Before scheduling, check if the task involves destructive operations:

**Destructive patterns** (require explicit user confirmation):
- File deletion: `rm`, `del`, `remove`, `wipe`, `clean` (unless cleaning temp/cache)
- Database: `drop`, `truncate`, `delete from`, `destroy`
- Git: `reset --hard`, `push --force`, `branch -D`
- System: `kill`, `shutdown`, `reboot`, `format`
- Network: `iptables`, `firewall`, `ufw`

If a destructive pattern is detected:
1. Warn the user: "This task involves a destructive operation (`<command>`). Are you sure you want to schedule this?"
2. Only proceed after explicit confirmation.
3. Include `[CONFIRMED DESTRUCTIVE]` in the job name for audit trail.

**Safe patterns** (no confirmation needed):
- Read-only: `ls`, `cat`, `git status`, `git log`, `curl GET`, `ping`
- Build/test: `npm test`, `npm build`, `make`, `cargo test`
- Reports: `generate`, `summarize`, `analyze`, `compile report`

### Step 4: Detect the Delivery Channel

Same priority order as remindme:

1. **Explicit override** — user says "on telegram" / "on discord" etc.
2. **Current channel** — if messaging from an external channel, deliver there.
3. **Preferred channel** — from MEMORY.md.
4. **Last external channel** — `channel: "last"`.
5. **No channel + delivery mode "none"** — OK, task runs silently.
6. **No channel + delivery mode "announce"** — ask: "Where should I send the task results?"

### Step 5: Call `cron.add`

**One-shot task:**

```json
{
  "name": "Task: <short description>",
  "schedule": {
    "kind": "at",
    "at": "<ISO 8601 timestamp>"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "SCHEDULED TASK: <detailed task instruction>. Execute this task now and report the results."
  },
  "delivery": {
    "mode": "announce",
    "channel": "<detected channel>",
    "to": "<detected target>",
    "bestEffort": true
  },
  "deleteAfterRun": true
}
```

**Recurring task (cron):**

```json
{
  "name": "Recurring Task: <short description>",
  "schedule": {
    "kind": "cron",
    "expr": "<cron expression>",
    "tz": "<IANA timezone>"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "RECURRING TASK: <detailed task instruction>. Execute this task now and report the results."
  },
  "delivery": {
    "mode": "announce",
    "channel": "<detected channel>",
    "to": "<detected target>",
    "bestEffort": true
  }
}
```

**Recurring task (interval):**

```json
{
  "name": "Recurring Task: <short description>",
  "schedule": {
    "kind": "every",
    "everyMs": "<interval in milliseconds>"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "RECURRING TASK: <detailed task instruction>. Execute this task now and report the results."
  },
  "delivery": {
    "mode": "<announce or none>",
    "channel": "<detected channel>",
    "to": "<detected target>",
    "bestEffort": true
  }
}
```

**Silent task (no delivery):**

```json
{
  "name": "Task: <short description>",
  "schedule": {
    "kind": "at",
    "at": "<ISO 8601 timestamp>"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "SCHEDULED TASK (SILENT): <detailed task instruction>. Execute this task now. No delivery needed — log results only."
  },
  "deleteAfterRun": true
}
```

### Step 6: Confirm to User

After `cron.add` succeeds, reply with:

```
Task scheduled!
Command: <task description>
Runs: <friendly time description> (<ISO timestamp or cron expression>)
Delivery: <channel or "silent">
Job ID: <jobId> (use "/schedule cancel <jobId>" to remove)
```

---

## Rules

1. **ALWAYS use `deleteAfterRun: true`** for one-shot tasks. Omit for recurring.
2. **ALWAYS use `sessionTarget: "isolated"`** — tasks run in their own sandboxed session.
3. **ALWAYS use `wakeMode: "now"`** — ensures execution at the scheduled time.
4. **ALWAYS use `delivery.bestEffort: true`** when delivery mode is "announce".
5. **NEVER use `act:wait` or loops** for delays. Cron handles timing.
6. **Always use the user's local timezone.** Never default to UTC.
7. **For recurring tasks**, do NOT set `deleteAfterRun`.
8. **Always return the jobId** so the user can cancel or audit later.
9. **Confirm destructive operations** before scheduling. Never silently schedule `rm`, `drop`, `kill`, etc.
10. **Prefix job names** with `Task:` (one-shot) or `Recurring Task:` (recurring) for audit trail and scoped cleanup.

## Platform Requirements

This skill has zero bundled dependencies because it relies on OpenClaw's built-in capabilities:

- **Cron scheduling**: `cron.add`, `cron.list`, `cron.remove` are native agent tools.
- **Task execution**: Scheduled agent sessions have access to Bash, file tools, and other agent capabilities to execute commands.
- **Channel delivery**: OpenClaw holds channel credentials in `openclaw.json`. No API keys needed in this skill.
- **Timezone**: Uses the system timezone from the host OS.

## Security & Privilege

This skill creates cron jobs with `payload.kind: "agentTurn"` which wake an isolated agent session to execute tasks. The following controls are enforced:

- **`sessionTarget: "isolated"`** — every scheduled task runs in a sandboxed session. It cannot access the main session's state, history, or tools beyond what's available to a fresh agent session.
- **`deleteAfterRun: true`** — one-shot tasks self-delete after execution, preventing stale job accumulation.
- **Destructive command gate** — the skill requires explicit user confirmation before scheduling commands that modify or delete data (rm, drop, kill, etc.).
- **Scoped naming** — all jobs are prefixed with `Task:` or `Recurring Task:`, making them auditable via `cron.list` and distinguishable from other skills' jobs.
- **No `always: true`** — this skill is not always-on. It only activates when the user invokes `/schedule`.
- **User-controlled** — every job returns a `jobId` that the user can inspect (`/schedule list`) or cancel (`/schedule cancel <jobId>`) at any time.
- **No escalation** — scheduled agent sessions inherit the same permissions and tool access as any normal agent session. They cannot grant themselves elevated privileges.

## Troubleshooting

- **Task didn't run?** → `cron.list` to check. Verify gateway was running at the scheduled time.
- **Command failed?** → Check delivery output for error details. The agent reports execution results.
- **Silent task — how to check?** → Use `cron.list` to see `lastStatus` and `lastError` fields.
- **Too many old jobs?** → See `references/TEMPLATES.md` for the cleanup job.

## References

See `references/TEMPLATES.md` for copy-paste templates and cleanup setup.
