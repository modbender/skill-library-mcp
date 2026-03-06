# Claude Code Usage Skill

Check your Claude Code OAuth API usage limits directly from Clawdbot.

## Features

- 📊 Session (5-hour) and Weekly (7-day) utilization tracking
- 🎨 Beautiful progress bars with color-coded status indicators
- ⚡ Smart caching (60s default) to avoid API spam
- 📤 JSON output for scripting
- 🦞 Telegram-friendly formatting
- 🔔 **NEW v1.1.0**: Automated monitoring with reset notifications

## Quick Test

```bash
cd /Users/ali/clawd/skills/claude-code-usage
./scripts/claude-usage.sh
```

## Example Output

```
🦞 Claude Code Usage

⏱️  Session (5h): 🟢 █░░░░░░░░░ 18%
   Resets in: 2h 48m

📅 Weekly (7d): 🟢 ░░░░░░░░░░ 2%
   Resets in: 6d 21h
```

## Usage in Clawdbot

Just ask:
- "How much Claude usage do I have left?"
- "Check my Claude Code limits"
- "What's my Claude quota?"

The skill automatically triggers and provides a formatted response.

## Automated Monitoring (v1.2.0+)

### Session Refresh Reminders (Recommended)

Get notified exactly when your 5-hour session quota refreshes!

**One-command setup:**
```bash
cd /Users/ali/clawd/skills/claude-code-usage
./scripts/session-reminder.sh
```

This creates a self-scheduling chain that:
- Checks when your session refreshes
- Schedules the next reminder for that exact time
- Notifies you automatically every 5 hours
- Runs forever with zero maintenance

### Reset Detection (Alternative)

Alternatively, monitor for quota resets by polling:

```bash
./scripts/monitor-usage.sh  # Test once
./scripts/setup-monitoring.sh  # Setup automated polling
```

See `SKILL.md` for detailed comparison and configuration options.

## Publishing to ClawdHub

To share with the community:

```bash
cd /Users/ali/clawd/skills
clawdhub publish claude-code-usage \
  --slug claude-code-usage \
  --name "Claude Code Usage" \
  --version 1.0.0 \
  --changelog "Initial release: Session & weekly usage tracking with beautiful formatting"
```

## Author

Created for Clawdbot by RZA 🦞
