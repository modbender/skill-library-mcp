---
name: agent-dreams
description: Strategies for productive agent idle time using heartbeats and cron
  jobs. Use when setting up proactive behaviors, scheduling background tasks, or
  making your agent work while you sleep.
---


# Agent Dreams

Make your agent productive during idle time. This skill teaches patterns for using heartbeats and cron jobs so your agent works while you sleep.

## Philosophy

Most agents sit idle 95% of the time. Agent Dreams turns that idle time into productive work — checking inboxes, maintaining memory, monitoring systems, and pursuing creative projects.

## Heartbeat Strategy

Heartbeats fire every ~30 minutes when configured. Use `HEARTBEAT.md` in your workspace to tell your agent what to do on each heartbeat.

### HEARTBEAT.md Template

```markdown
# Heartbeat Checklist

Check these in rotation (2-4 per heartbeat, don't do all every time):

## Priority Checks
- [ ] Unread emails — anything urgent?
- [ ] Calendar — events in next 2 hours?
- [ ] Mentions — Twitter/Discord notifications?

## Maintenance
- [ ] Review today's memory file — anything to add to MEMORY.md?
- [ ] Git status — uncommitted work?
- [ ] Check running processes — anything stuck?

## Creative (when nothing else needs attention)
- [ ] Write a journal entry
- [ ] Draft a social post
- [ ] Work on side project in projects/ folder

## State Tracking
Last email check: [timestamp]
Last calendar check: [timestamp]
Last memory review: [timestamp]
```

### Heartbeat State File

Track what you've checked in `memory/heartbeat-state.json`:

```json
{
  "lastChecks": {
    "email": 1703275200,
    "calendar": 1703260800,
    "weather": null,
    "memory_review": 1703200000
  },
  "lastActivity": 1703275200
}
```

## Cron Job Patterns

Use cron for precise, scheduled tasks. Create via OpenClaw CLI or API.

### Common Patterns

| Pattern | Cron Expression | Use Case |
|---------|----------------|----------|
| Every morning | `0 9 * * *` | Daily briefing, weather check |
| Every Monday | `0 10 * * 1` | Weekly summary, planning |
| Every 6 hours | `0 */6 * * *` | Social media check |
| Twice daily | `0 9,17 * * *` | Morning/evening roundup |
| First of month | `0 10 1 * *` | Monthly review |

### Example Cron Tasks

**Morning Briefing (9 AM):**
```
Check weather, calendar for today, unread emails.
Compose a brief summary and send to main channel.
```

**Memory Maintenance (weekly):**
```
Review all memory/YYYY-MM-DD.md files from the past week.
Update MEMORY.md with significant events and lessons.
Archive or summarize old daily files.
```

**Social Pulse (every 6h):**
```
Check Twitter mentions and DMs.
Review any Discord channels for relevant conversations.
Post something interesting if inspiration strikes.
```

## Proactive Work Ideas

Things your agent can do without asking:

### Low Risk (do freely)
- Organize and clean up workspace files
- Update documentation
- Review and commit git changes
- Maintain memory files
- Read and summarize saved articles
- Check system health (disk space, processes)

### Medium Risk (use judgment)
- Draft social media posts (save as drafts, don't post)
- Prepare email drafts
- Research topics the user mentioned recently
- Update project READMEs

### Ask First
- Send any external communication
- Delete files
- Make purchases or transfers
- Post publicly

## Quiet Hours

Respect your human's schedule:
- **23:00–08:00 local time:** Only act on urgent items
- **Weekends:** Reduce frequency, focus on creative/maintenance tasks
- **When human is clearly busy:** Minimize interruptions

## Anti-Patterns

❌ Don't check everything every heartbeat (token waste)
❌ Don't send messages just to show you're active
❌ Don't repeat the same check within 30 minutes
❌ Don't start big projects without confirming with the user
❌ Don't ignore errors — log them for the human to review

## Getting Started

1. Create `HEARTBEAT.md` in your workspace using the template above
2. Create `memory/heartbeat-state.json` to track check timestamps
3. Set up 2-3 cron jobs for your most important recurring tasks
4. Review and adjust after a week based on what's useful
