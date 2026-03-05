# Job Execution Monitor

**Heartbeat-based cron job monitoring for OpenClaw.**

Watches your scheduled jobs and alerts you when they fail or miss their schedule. Uses periodic heartbeat checks with the cheapest LLM to minimize cost (~$0.01/day).

## Install / Update (ClawHub)

```bash
clawhub install job-execution-monitor
clawhub update job-execution-monitor
```

## Quick Start

```bash
# 1) Copy example config
cp ~/.openclaw/skills/job-execution-monitor/config/job-execution-monitor.example.json \
  ~/.openclaw/workspace/job-execution-monitor.json

# 2) Edit config
nano ~/.openclaw/workspace/job-execution-monitor.json

# 3) Run once manually
~/.openclaw/skills/job-execution-monitor/scripts/healthcheck.sh
```

## How It Works

1. Agent wakes during heartbeat polls (~every 15-30min)
2. Every ~4th wake → checks cron jobs (once/hour)
3. Compares against `job-execution-monitor.json` config
4. **On failure** → wake event → main session investigates
5. **On recovery** → confirmation wake event
6. **All OK** → silent (no alerts)

**Cost:** ~100k tokens/day using Gemini Flash (~$0.01/day)

## Config Example

```json
{
  "checkIntervalMin": 60,
  "jobs": {
    "Daily 21:00 journaling (projects + accomplishments + next day plan)": {
      "schedule": "0 22 * * *",
      "tolerance": 600,
      "critical": true
    }
  }
}
```

## Agent Behavior

When job-execution-monitor detects a problem:

```
🔴 Job Execution Monitor: "daily-wrap-up" missed schedule
Expected: 22:00 ±10min
Last run: 5h 32m ago
```

Your agent:
1. Alerts you with context (expected schedule vs last run)
2. You decide what to do next (inspect logs, rerun job, adjust schedule)

When job recovers:

```
✅ Job Execution Monitor: "daily-wrap-up" recovered
Last run: 22:02 (2min ago)
```

## Features

**Phase 1 (✅ now):**
- Schedule validation
- Timestamp checking
- Wake events on failures
- Heartbeat-based (cheap!)

**Phase 2 (🚧 next):**
- Error pattern detection
- Response length validation
- "Pong" detection for non-ping jobs

**Phase 3 (📋 future):**
- JSON schema validation
- Confidence scoring
- Structured error reporting

## Philosophy

**Smart monitoring, minimal cost.**

- Monitoring is contextual → agent analyzes with full tool access
- Check frequency: ~1/hour (sufficient for daily jobs)
- Uses cheapest LLM: Gemini Flash or Haiku
- Only wakes main session when real problems occur
- State tracking prevents alert spam

---

**See `SKILL.md` for full documentation.**
