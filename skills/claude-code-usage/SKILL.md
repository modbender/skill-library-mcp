---
name: claude-code-usage
description: Check Claude Code OAuth usage limits (session & weekly quotas). Use when user asks about Claude Code usage, remaining limits, rate limits, or how much Claude usage they have left. Includes automated session refresh reminders and reset detection monitoring.
metadata:
  clawdbot:
    emoji: "📊"
    os:
      - darwin
      - linux
    requires:
      bins:
        - curl
---

# Claude Code Usage

Check your Claude Code OAuth API usage limits for both session (5-hour) and weekly (7-day) windows.

## Quick Start

```bash
cd {baseDir}
./scripts/claude-usage.sh
```

## Usage

```bash
# Default: show cached usage (if fresh)
./scripts/claude-usage.sh

# Force refresh from API
./scripts/claude-usage.sh --fresh

# JSON output
./scripts/claude-usage.sh --json

# Custom cache TTL
./scripts/claude-usage.sh --cache-ttl 300
```

## Output

**Text format** (default):
```
🦞 Claude Code Usage

⏱️  Session (5h): 🟢 ████░░░░░░ 40%
   Resets in: 2h 15m

📅 Weekly (7d): 🟡 ██████░░░░ 60%
   Resets in: 3d 8h
```

**JSON format** (`--json`):
```json
{
  "session": {
    "utilization": 40,
    "resets_in": "2h 15m",
    "resets_at": "2026-01-19T22:15:00Z"
  },
  "weekly": {
    "utilization": 60,
    "resets_in": "3d 8h",
    "resets_at": "2026-01-22T04:00:00Z"
  },
  "cached_at": "2026-01-19T20:00:00Z"
}
```

## Features

- 📊 **Session limit** (5-hour window) - Short-term rate limit
- 📅 **Weekly limit** (7-day window) - Long-term rate limit
- ⚡ **Smart caching** - 60-second cache to avoid API spam
- 🎨 **Beautiful output** - Progress bars, emojis, color-coded status
- 🔄 **Force refresh** - `--fresh` flag to bypass cache
- 📤 **JSON output** - Machine-readable format
- 🔔 **Automated monitoring** - Get notified when quotas reset

## Status Indicators

- 🟢 **Green** - 0-50% usage (healthy)
- 🟡 **Yellow** - 51-80% usage (moderate)
- 🔴 **Red** - 81-100% usage (high/critical)

## Requirements

- **macOS**: Uses Keychain to access Claude Code credentials
- **Linux**: Uses `secret-tool` for credential storage
- **Credentials**: Must have Claude Code CLI authenticated

## How It Works

1. Retrieves OAuth token from system keychain
2. Queries `api.anthropic.com/api/oauth/usage` with OAuth bearer token
3. Parses `five_hour` and `seven_day` utilization metrics
4. Calculates time remaining until reset
5. Formats output with progress bars and status indicators
6. Caches result for 60 seconds (configurable)

## Cache

Default cache: `/tmp/claude-usage-cache` (60s TTL)

Override:
```bash
CACHE_FILE=/tmp/my-cache CACHE_TTL=300 ./scripts/claude-usage.sh
```

## Examples

**Check usage before starting work:**
```bash
./scripts/claude-usage.sh --fresh
```

**Integrate with statusline:**
```bash
usage=$(./scripts/claude-usage.sh | grep "Session" | awk '{print $NF}')
echo "Session: $usage"
```

**Get JSON for monitoring:**
```bash
./scripts/claude-usage.sh --json | jq '.session.utilization'
```

## Automated Monitoring

### Session Refresh Reminders (Recommended)

Get notified exactly when your 5-hour session quota refreshes!

**Quick Setup:**
```bash
./scripts/session-reminder.sh
```

This creates a **self-scheduling chain** of cron jobs that:
1. Checks your current session expiry time
2. Schedules the next reminder for when your session refreshes
3. Notifies you with current usage stats
4. Auto-removes itself (the new cron takes over)

**What You'll Get:**
```
🔄 Claude Code Session Status

⏱️  Current usage: 44%
⏰ Next refresh: 2h 15m

Your 5-hour quota will reset soon! 🦞

✅ Next reminder scheduled for: Jan 22 at 01:22 AM
```

**How It Works:**
- Each reminder runs `claude-usage.sh` to find the exact session reset time
- Schedules a one-time cron for that exact moment
- Repeats every 5 hours automatically
- Self-correcting if session times ever drift

**Benefits:**
- ✅ Accurate to the minute
- ✅ No manual scheduling needed
- ✅ Adapts to your actual usage patterns
- ✅ Minimal API calls (only when needed)

### Reset Detection Monitor (Alternative)

Get automatic notifications when your Claude Code quotas reset by polling usage.

**Quick Setup:**
```bash
# Test once
./scripts/monitor-usage.sh

# Setup automated monitoring (runs every 30 minutes)
./scripts/setup-monitoring.sh
```

Or add via Clawdbot directly:
```bash
# Check every 30 minutes
clawdbot cron add --cron "*/30 * * * *" \
  --message "cd /Users/ali/clawd/skills/claude-code-usage && ./scripts/monitor-usage.sh" \
  --name "Claude Code Usage Monitor" \
  --session isolated --deliver --channel telegram
```

**What You'll Get:**
```
🎉 Claude Code Session Reset!

⏱️  Your 5-hour quota has reset
📊 Usage: 2%
⏰ Next reset: 4h 58m

Fresh usage available! 🦞
```

**How It Works:**
1. **Monitors usage** every 30 minutes (configurable)
2. **Detects resets** when usage drops significantly (>10% or <5%)
3. **Sends notifications** via Telegram when resets occur
4. **Tracks state** in `/tmp/claude-usage-state.json`

**Customization:**
```bash
# Change check interval
clawdbot cron add --cron "*/15 * * * *" ...  # Every 15 minutes
clawdbot cron add --cron "0 * * * *" ...      # Every hour

# Custom state file location
STATE_FILE=/path/to/state.json ./scripts/monitor-usage.sh
```

### Which Monitoring Method?

| Feature | Session Reminder | Reset Detection |
|---------|-----------------|-----------------|
| Accuracy | ✅ Exact minute | ~30min window |
| API calls | Minimal | Every check |
| Notification timing | Right on reset | Up to 30min delay |
| Setup | One command | One command |
| Maintenance | Self-scheduling | Cron runs forever |

**Recommendation:** Use **Session Reminder** for precise, real-time notifications.

## Troubleshooting

**No credentials found:**
- Ensure Claude Code CLI is installed and authenticated
- Run `claude` once to trigger OAuth flow

**API request failed:**
- Check internet connection
- Verify OAuth token hasn't expired
- Try `--fresh` to force new request

**Linux users:**
Install `libsecret` for credential storage:
```bash
# Debian/Ubuntu
sudo apt install libsecret-tools

# Fedora/RHEL
sudo dnf install libsecret
```
