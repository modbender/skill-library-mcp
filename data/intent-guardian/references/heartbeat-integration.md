# Intent Guardian - Heartbeat Integration Guide

Add the following block to your `HEARTBEAT.md` to enable automatic intent monitoring on every heartbeat cycle.

## Recommended HEARTBEAT.md Addition

```markdown
## Intent Guardian - Focus Monitoring

On every heartbeat:

1. **Sense**: Run `scripts/sense_activity.sh` or `scripts/sense_activitywatch.sh` to get recent window activity.

2. **Understand**: Read the last 50 entries from `memory/skills/intent-guardian/activity_log.jsonl`. Group consecutive entries with the same app into activity segments. For each segment, infer what the user was trying to do (their intent).

3. **Update Stack**: Read `memory/skills/intent-guardian/task_stack.json`. Update it:
   - Mark completed tasks (user naturally moved on after finishing)
   - Add new tasks from recent activity
   - Mark interrupted tasks as "suspended" (user switched away mid-task)

4. **Detect Forgetting**: Check for suspended tasks where:
   - Time since suspension > `interruption_threshold_minutes` (default: 5)
   - User has NOT returned to the suspended app
   - User shows wandering behavior (rapid context switching) OR is in a clearly unrelated task
   - Consult `memory/skills/intent-guardian/focus_profile.json` for personalized thresholds

5. **Remind (if needed)**: If a forgotten task is detected:
   - Check `reminder_cooldown_minutes` to avoid nagging
   - Generate a gentle, context-rich reminder
   - Include what the user was doing AND why they left (if inferable)
   - Send via the configured notification channel

6. **Learn**: After any reminder:
   - If user acts on it -> log "accepted" via `scripts/log_reminder_response.sh`
   - If user dismisses -> log "dismissed"
   - If no response within 5 minutes -> log "ignored"
   - Periodically update `focus_profile.json` with new pattern data
```

## Cron Jobs

### Daily Focus Report (recommended)

```bash
openclaw cron add --name "intent-guardian-daily" \
  --schedule "0 18 * * 1-5" \
  --prompt "Run scripts/daily_focus_report.sh and format the output as a readable daily focus summary. Include highlights, interruption patterns, and one actionable suggestion."
```

### Weekly Cleanup (recommended)

```bash
openclaw cron add --name "intent-guardian-cleanup" \
  --schedule "0 3 * * 0" \
  --prompt "Run scripts/cleanup.sh 30 to remove activity data older than 30 days."
```

### Weekly Pattern Update (optional)

```bash
openclaw cron add --name "intent-guardian-patterns" \
  --schedule "0 20 * * 0" \
  --prompt "Analyze this week's intent-guardian data (activity_log.jsonl + reminder_feedback.jsonl) and update focus_profile.json with any new patterns: which apps cause the most forgetting, what times of day focus is best/worst, and whether reminder acceptance rate is improving."
```
