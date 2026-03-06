# Intent Guardian

**Never lose your train of thought again.**

Intent Guardian is an OpenClaw skill that watches your desktop activity, maintains a real-time task stack, and reminds you when you've forgotten what you were doing after an interruption.

## Why This Exists

Knowledge workers are interrupted every 3 minutes on average. After each interruption, there's a significant chance you simply forget what you were doing before. This skill acts as your always-on focus companion that remembers your intentions when you can't.

## Quick Start

```bash
# Install
npx playbooks add skill openclaw/skills --skill intent-guardian

# Start activity sensing (macOS)
bash ~/.openclaw/skills/intent-guardian/scripts/sense_activity.sh &

# Add heartbeat integration (see references/heartbeat-integration.md)
```

## How It Works

1. **Sense** - Polls active window title/app every few seconds (via native OS APIs or ActivityWatch)
2. **Understand** - LLM segments activity stream into logical tasks and infers intent
3. **Track** - Maintains a task stack: what you're doing, what got interrupted, what's completed
4. **Detect** - Identifies when a suspended task was likely *forgotten* (not deliberately abandoned)
5. **Remind** - Sends a gentle, context-rich nudge to get you back on track
6. **Learn** - Builds a personal focus profile from your patterns over time

## Features

- Zero-dependency macOS setup (uses `osascript`)
- Optional ActivityWatch integration for richer data
- Optional screenshot analysis with vision models
- Privacy-first: all data stays local
- Integrates with existing skills (personal-analytics, daily-review, screen-monitor)
- Personalized over time: learns which apps cause you to forget most

## Files

```
intent-guardian/
  SKILL.md                              # Main skill definition
  _meta.json                            # Skill metadata
  README.md                             # This file
  scripts/
    sense_activity.sh                   # macOS window polling
    sense_activitywatch.sh              # ActivityWatch API integration
    sense_screen.sh                     # Optional screenshot capture
    get_task_stack.sh                   # Read current task stack
    get_focus_profile.sh                # Read focus profile
    get_recent_activity.sh              # Get recent activity log entries
    log_reminder_response.sh            # Log user feedback on reminders
    daily_focus_report.sh               # Generate daily focus summary
    cleanup.sh                          # Clean old data
  references/
    heartbeat-integration.md            # How to set up heartbeat + cron
    forgetting-detection.md             # Algorithm details for detection
```

## License

MIT
