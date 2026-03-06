---
name: kimi-usage-monitor
description: Monitor Kimi K2.5 API usage and quota from the Kimi console. Use when the agent needs to (1) Check remaining usage percentage and reset timers, (2) Make autonomous decisions about task prioritization based on available quota, (3) Monitor rate limit status before starting intensive operations, (4) Log usage patterns over time for resource planning. Essential for self-managing agents operating under quota constraints.
---

# Kimi Usage Monitor

Monitor Kimi K2.5 usage quotas from the Kimi console to make informed decisions about task prioritization and resource allocation.

## When to Use This Skill

- **Before intensive operations**: Check quota before starting multi-step research or coding tasks
- **Autonomous planning**: Self-prioritize tasks based on remaining usage percentage
- **Rate limit awareness**: Know when quotas reset to time high-priority work
- **Usage tracking**: Log patterns for long-term capacity planning

## Quick Start

**Prerequisites:** Chrome with OpenClaw extension attached
1. Open Chrome → `https://www.kimi.com/code/console?from=membership`
2. Click OpenClaw extension icon (badge should show ON)
3. Ensure you're logged into Kimi

```bash
# Check current usage (Linux/macOS/WSL)
./check_usage.sh

# Windows native
check_usage.bat           # CMD
.\check_usage.ps1         # PowerShell

# JSON output for automation (all platforms)
python3 scripts/fetch_usage.py --json
```

**Platform Support:** Linux ✅ | macOS ✅ | Windows (WSL) ✅ | Windows (Native) ✅

## Usage Data Available

The Kimi console shows:

| Metric | Description | Decision Threshold |
|--------|-------------|-------------------|
| **Weekly Usage** | Percentage of weekly quota consumed | >75% = prioritize |
| **Weekly Reset** | Hours until quota resets | Plan heavy tasks after reset |
| **Rate Limit** | Additional rate limiting quota | Secondary resource |
| **Rate Reset** | Hours until rate limit resets | Short-term buffer |

## Autonomous Decision Guidelines

When operating autonomously, use these heuristics:

**🟢 High Capacity (>50% remaining)**
- Proceed with full capability
- Accept multi-step research tasks
- Spawn subagents as needed
- Enable verbose reasoning

**🟡 Moderate Capacity (25-50% remaining)**
- Batch similar operations
- Prefer concise outputs
- Use subagents sparingly
- Disable non-essential reasoning

**🔴 Low Capacity (<25% remaining)**
- Essential tasks only
- Single-step operations
- Avoid subagent spawning
- Prioritize user-directed work over proactive tasks

## Pre-Flight Checks for Intensive Operations

Before spawning subagents or starting multi-step tasks, check capacity:

```bash
# Check if operation should proceed
python3 scripts/preflight_check.py [light|standard|intensive]

# Light: single query, simple task (needs 10%)
# Standard: normal subagent, research (needs 25%)
# Intensive: multi-subagent, deep research (needs 50%)
```

Returns exit code 0 if cleared, 1 if blocked. Use in scripts:

```bash
if python3 scripts/preflight_check.py intensive; then
    # Proceed with intensive operation
    sessions_spawn "Complex research task..."
fi
```

## Subagent Guard

Check specifically before spawning subagents:

```bash
python3 scripts/subagent_guard.py
```

Returns JSON with `can_spawn` boolean:
```json
{
  "can_spawn": true,
  "usage_percent": 45,
  "remaining_percent": 55,
  "resets_hours": 36
}
```

## Integration Ideas

**Hourly monitoring cron:**
```bash
# Add to crontab or OpenClaw jobs
0 * * * * cd /path/to/kimi-usage-monitor && python3 scripts/usage_logger.py
```

**Pre-task validation:**
```python
import subprocess
result = subprocess.run(
    ["python3", "scripts/preflight_check.py", "intensive"],
    capture_output=True
)
if result.returncode == 0:
    # Proceed with task
    pass
```

## Script Reference

| Script | Purpose |
|--------|---------|
| `scripts/fetch_usage.py` | Main usage scraper (browser-based) |
| `scripts/usage_logger.py` | Autonomous logging + decision wrapper |
| `scripts/preflight_check.py` | Pre-flight validation for operations |
| `scripts/subagent_guard.py` | Check before spawning subagents |
| `check_usage.sh` | Quick CLI wrapper |

**Note:** Alternative Playwright-based scraper (`fetch_kimi_usage.py`) available for non-OpenClaw environments (requires system dependencies).

## Troubleshooting

**"Browser not available"**
- Ensure Chrome extension is attached (badge shows ON)
- Verify the Kimi console tab is open

**"Could not detect usage"**
- Make sure you're logged into Kimi
- Check that the console page has fully loaded

**Authentication errors**
- Re-authenticate at `https://www.kimi.com/code/console`
- The browser tool uses your existing Chrome session

## Output Format

### Human-Readable (default)
```
📊 Kimi Usage Monitor
========================================

🗓️  Weekly Usage
   Used: 45%
   Remaining: 55%
   Resets in: 36 hours
   Status: 🟡 Moderate — plan accordingly

⚡ Rate Limit
   Used: 2%
   Resets in: 3 hours
```

### JSON (`--json` flag)
```json
{
  "weekly_usage_percent": 45,
  "weekly_resets_hours": 36,
  "rate_limit_percent": 2,
  "rate_limit_resets_hours": 3,
  "timestamp": "2026-02-12 21:15:00"
}
```

## License

MIT License - Feel free to modify and distribute.
