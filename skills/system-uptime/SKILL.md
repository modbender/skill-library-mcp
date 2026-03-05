---
name: system-uptime
description: "Get the current system uptime using the native 'uptime' command. Use when: user asks about system uptime, system status, or how long the system has been running."
metadata: { "openclaw": { "emoji": "⏱️", "requires": { "bins": ["uptime"] } } }
---

# System Uptime Skill

Get the current system uptime using the built-in `uptime` command.

## When to Use

✅ **USE this skill when:**

- "What's the system uptime?"
- "How long has the system been running?"
- "Show system status"
- "When was the last reboot?"

## When NOT to Use

❌ **DON'T use this skill when:**

- Need detailed system metrics → use monitoring tools
- Remote system uptime → use SSH or remote monitoring
- Historical uptime data → check system logs

## Commands

### Get System Uptime

```bash
# Basic uptime
uptime

# Using the skill CLI
node uptime-cli.js
```

## Example Output

```
11:30:45 up 2 days, 4:23, 2 users, load average: 1.23, 1.15, 1.08
```

## Notes

- Uses the standard Unix `uptime` command
- Works on macOS, Linux, and other Unix-like systems
- No additional dependencies required