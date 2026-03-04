---
name: cron-health-check
displayName: Cron Health Check | OpenClaw Skill
description: Monitors OpenClaw cron job health, identifies failures, timeouts, and delivery issues.
version: 1.0.0
---

# Cron Health Check | OpenClaw Skill

## Description

Monitors OpenClaw cron job health, identifies failures, timeouts, and delivery issues.

# Cron Health Check | OpenClaw Skill

Monitors the health of OpenClaw cron jobs by analyzing run history and identifying patterns of failures, timeouts, and delivery issues.


## Usage

- As a scheduled cron job to monitor job health proactively
- Manually to check current cron job status
- After fixing cron job errors to verify improvements

```bash
# Check health of all cron jobs (last 24 hours)
python3 /Users/ghost/.openclaw/workspace/skills/cron-health-check/scripts/check_cron_health.py

# Check last 48 hours
python3 /Users/ghost/.openclaw/workspace/skills/cron-health-check/scripts/check_cron_health.py --hours 48

# Output JSON format
python3 /Users/ghost/.openclaw/workspace/skills/cron-health-check/scripts/check_cron_health.py --json
```


## What this skill does

- **Analyzes** cron job run history from the last N hours
- **Identifies** jobs with consecutive failures, timeouts, or delivery issues
- **Reports** health status (healthy/warning/critical) for each job
- **Suggests** fixes (e.g., adding --best-effort-deliver for delivery failures)
- **Detects** OpenRouter API limit issues


## Integration as a Cron Job

This skill can run periodically to monitor cron job health:

```json
{
  "payload": {
    "kind": "agentTurn",
    "message": "Run cron-health-check skill to analyze cron job health.",
    "model": "openrouter/google/gemini-2.5-flash",
    "thinking": "low",
    "timeoutSeconds": 60
  },
  "schedule": {
    "kind": "cron",
    "cron": "0 */6 * * *"
  },
  "delivery": {
    "mode": "announce",
    "bestEffort": true
  },
  "sessionTarget": "isolated",
  "name": "Cron Health Monitor"
}
```


## Output

Health status for each job:
- **healthy**: No issues detected
- **warning**: Some issues but not critical
- **critical**: Multiple consecutive failures or timeouts

Issues detected:
- Consecutive errors
- Timeout patterns
- Delivery failures (suggests --best-effort-deliver)
- OpenRouter API limit exceeded


## Exit Codes

- `0`: All jobs healthy
- `1`: Warning issues found
- `2`: Critical issues found
