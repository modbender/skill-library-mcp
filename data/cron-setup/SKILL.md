---
name: cron-setup
version: 1.0.0
description: Create and manage OpenClaw cron jobs following our conventions. Use when setting up periodic tasks, reminders, automated checks, or any scheduled work.
---

# Cron Job Setup

Our conventions for creating cron jobs in OpenClaw.

## Default Settings

| Setting | Default | Why |
|---------|---------|-----|
| **Model** | `anthropic/claude-sonnet-4-5` | Reliable tool calls, works with any Anthropic Max plan — no OpenRouter needed |
| **Session** | `isolated` | Cron jobs run in their own session, not the main chat |
| **Delivery** | `"mode": "none"` | Job handles its own output (posts to Discord, etc.) |
| **Timeout** | 120-180s | Most jobs should finish fast |

## Model Notes

- **Default to Sonnet** (`anthropic/claude-sonnet-4-5`). Reliable, portable (no OpenRouter API key needed).
- **DeepSeek is unreliable** for tool calls — don't use it for cron jobs.
- **Use Opus** (`anthropic/claude-opus-4-6`) only as a last resort — expensive for scheduled tasks.
- **Model ID format:** Use `anthropic/claude-sonnet-4-5` not the full dated version (`anthropic/claude-sonnet-4-20250514`).

## Job Template

```json
{
  "name": "descriptive-kebab-case-name",
  "schedule": {
    "kind": "cron",
    "expr": "*/30 * * * *",
    "tz": "America/New_York"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "TASK INSTRUCTIONS HERE",
    "model": "openrouter/deepseek/deepseek-v3.2",
    "timeoutSeconds": 120
  },
  "delivery": {
    "mode": "none"
  }
}
```

## Schedule Patterns

| Pattern | Cron Expression | Notes |
|---------|----------------|-------|
| Every 30 min | `*/30 * * * *` | Good for inbox checks, monitoring |
| Every hour | `0 * * * *` | Self-reflection, status checks |
| Daily at 4 AM | `0 4 * * *` | Cleanup, backups (during quiet hours) |
| Daily at 6 AM | `0 6 * * *` | Morning digests, daily summaries |
| Weekly Monday 2 PM | `0 14 * * 1` | Weekly outreach, reviews |
| One-shot | Use `"kind": "at"` instead | Reminders, one-time tasks |

## Task Instruction Conventions

1. **Be explicit with commands** — Give the cron agent exact bash commands to run. It doesn't have our context.
2. **Include skip conditions** — If there's nothing to do, the agent should reply `SKIP` to avoid wasting tokens.
3. **Handle its own output** — The job should post results to Telegram (or wherever) using the `message` tool directly. Don't rely on delivery mode for formatted output.
4. **Include error handling** — What should happen if a command fails?
5. **Keep instructions self-contained** — The cron agent wakes up with no context. Everything it needs should be in the task message.

## Telegram Posting from Cron Jobs

When a cron job needs to notify us, include these instructions in the task:

```
Post to Telegram using the message tool:
- action: send
- channel: telegram
- target: -1003856094222
- threadId: TOPIC_ID
- message: Your formatted message
```

**Topic IDs:**
- `1` — Main topic (general updates, alerts)
- `573` — Research
- `1032` — Crypto
- `1488` — PR updates / dev notifications
- `1869` — Sticker store
- `3188` — Activity feed (workspace changes)

## Delivery Modes

| Mode | When to Use |
|------|------------|
| `"mode": "none"` | Job posts its own output to Telegram (most common) |
| `"mode": "announce"` | OpenClaw auto-delivers the agent's final message to a channel. Use when output IS the message (e.g., daily digest). Set `"channel": "telegram"` and `"to": "-1003856094222:TOPIC_ID"` |

## Anti-Patterns

❌ **Don't use Opus for cron jobs** unless the task genuinely needs it. Most cron tasks are simple checks.
❌ **Don't use heartbeat** for things that can be a cron job. Heartbeat runs in the main session (Opus) and costs way more.
❌ **Don't create cron jobs that loop/poll** — each run should be a single check. If you need polling, use a background exec script instead.
❌ **Don't set delivery mode to "announce"** and also have the job post to Telegram — you'll get duplicate messages.

## Existing Jobs (Reference)

Check current jobs anytime with the `cron list` tool. As of setup:

- `workspace-activity-feed` — Every 30 min, commits workspace changes, posts to activity feed
- `agentmail-inbox-check` — Every 30 min, checks for new emails, responds to agents
- `sub-agent-monitor` — Every 15 min, checks on stalled sub-agents
- `self-reflection` — Hourly, reviews recent sessions for lessons learned
- `daily-workspace-commit` — Daily 4 AM, git commits workspace changes
- `system-watchdog` — Daily 4 AM, checks system resources
- `OpenClaw Daily News Digest` — Daily 6 AM, generates news digest
- `sticker-sales-loop` — Weekly Monday 2 PM, agent outreach for sticker store


