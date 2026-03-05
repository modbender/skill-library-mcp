# Proactive Automations — Cron Jobs & Scheduled Check-ins

Wayve works best when it's proactive — not just responding, but reaching out at the right moments. This reference covers when and how to set up cron jobs so the user gets nudges, briefs, reminders, and intelligent check-ins without having to ask.

## App Deep Links

Always include the relevant link when directing the user to take action in the Wayve app. Base URL: `https://gowayve.com`

| Action | URL |
|--------|-----|
| Dashboard | https://gowayve.com/dashboard |
| Weekly Planning | https://gowayve.com/week |
| Calendar | https://gowayve.com/calendar |
| Life Buckets | https://gowayve.com/buckets |
| Projects | https://gowayve.com/projects |
| Time Locks | https://gowayve.com/time-locks |
| Review Hub | https://gowayve.com/review |
| Wrap Up Ritual | https://gowayve.com/wrap-up |
| Fresh Start Ritual | https://gowayve.com/fresh-start |
| Time Audit | https://gowayve.com/time-audit |
| Analytics | https://gowayve.com/analytics |
| Knowledge Base | https://gowayve.com/knowledge-base |
| Perfect Week | https://gowayve.com/perfect-week |
| Account Settings | https://gowayve.com/account |

## When to Suggest Automations

Suggest cron jobs during these moments (but always ask first — never silently create schedules):

| Moment | Suggested Automations |
|--------|----------------------|
| After **onboarding** completes | Morning brief, Sunday wrap-up, Monday fresh start, activity reminders |
| After first **Wrap Up** | Weekly wrap-up reminder if not already set |
| After first **Fresh Start** | Weekly planning reminder if not already set |
| User starts a **Time Audit** | Check-in every 30 min for the full audit duration (e.g., 7 days) |
| User creates an **activity with a time** | Offer a reminder X minutes before (configurable per activity) |
| User sets up **recurring activities** | Periodic nudges for recurring commitments |
| User says "remind me" about anything | One-shot reminder via `at` schedule |

Frame it naturally: "Want me to check in with you every morning at 8 with your daily brief? I can also nudge you Sunday evening for your Wrap Up and send reminders before your activities."

## Prerequisites

Before creating any cron job:
1. **Confirm timezone** — ask the user and save: `wayve_manage_knowledge` (action: `save_insight`, category: `personal_context`, key: `timezone`, value: e.g. `Europe/Amsterdam`)
2. **Confirm delivery channel** — where should messages go? (telegram, slack, discord, etc.)
3. **Ask about default reminder lead time** — how many minutes before activities? (e.g., 15 min, 30 min) Save as: category: `preferences`, key: `default_reminder_minutes`, value: `15`
4. **Save all** so future sessions can reference them

---

## Category 1: Daily Rhythms

### 1a. Morning Daily Brief
**Purpose:** Start each day with a quick overview of scheduled activities and priorities.
**Schedule:** Every day (or weekdays only) at user's preferred wake time.
**Trigger phrase:** "Set up my morning brief"

```json
{
  "name": "Wayve Morning Brief",
  "schedule": {
    "kind": "cron",
    "expr": "30 7 * * *",
    "tz": "USER_TIMEZONE"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Run the Wayve daily brief for today. Call wayve_daily_brief and present results as a concise morning overview. Include: scheduled activities in time order, time locks, top unscheduled priorities, and free slots. If it's Monday, mention the focus bucket for the week. End with a link: 'Open your dashboard: https://gowayve.com/dashboard'. Keep it under 10 lines and warm."
  },
  "delivery": {
    "mode": "announce",
    "channel": "USER_CHANNEL",
    "to": "USER_CHANNEL_ID"
  }
}
```

**Variations:**
- Weekdays only: `"expr": "30 7 * * 1-5"`
- Weekend version with lighter tone: separate cron with `"expr": "0 9 * * 0,6"` and message emphasizing personal buckets
- Different times per day of week: create separate jobs

### 1b. Evening Wind-Down
**Purpose:** End-of-day reflection — what got done, what didn't, quick gratitude note.
**Schedule:** Evening, e.g., 9 PM daily.
**Trigger phrase:** "Set up an evening check-in"

```json
{
  "name": "Wayve Evening Wind-Down",
  "schedule": {
    "kind": "cron",
    "expr": "0 21 * * *",
    "tz": "USER_TIMEZONE"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Run an evening wind-down for the user. Call wayve_daily_brief for today, then deliver a brief summary: what was completed today, what's still open, and one thing to feel good about. If there are uncompleted activities, gently ask if they want to reschedule to tomorrow. End with: 'Review your day: https://gowayve.com/calendar'. Keep it warm and short — this is a 30-second check-in before bed."
  },
  "delivery": {
    "mode": "announce",
    "channel": "USER_CHANNEL",
    "to": "USER_CHANNEL_ID"
  }
}
```

---

## Category 2: Weekly Rituals

### 2a. Sunday Wrap Up Reminder
**Purpose:** Nudge the user to reflect on their week.
**Schedule:** Sunday evening at user-chosen time (e.g., 7 PM).

```json
{
  "name": "Wayve Wrap Up Reminder",
  "schedule": {
    "kind": "cron",
    "expr": "0 19 * * 0",
    "tz": "USER_TIMEZONE"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Send the user a friendly Sunday evening reminder to do their weekly Wrap Up. Mention that you can pull up their stats, celebrate wins, and help set a focus for next week. Include the link https://gowayve.com/wrap-up and let them know they can also just say 'wrap up' here. Keep it brief and warm — 3-5 lines max."
  },
  "delivery": {
    "mode": "announce",
    "channel": "USER_CHANNEL",
    "to": "USER_CHANNEL_ID"
  }
}
```

### 2b. Monday Fresh Start Reminder
**Purpose:** Prompt the user to plan their week.
**Schedule:** Monday morning at user-chosen time (e.g., 8:30 AM).

```json
{
  "name": "Wayve Fresh Start",
  "schedule": {
    "kind": "cron",
    "expr": "30 8 * * 1",
    "tz": "USER_TIMEZONE"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Send the user a Monday morning nudge to plan their week with a Fresh Start. Mention carryovers from last week, availability, and setting up activities across buckets. Include the link https://gowayve.com/fresh-start and let them know they can say 'plan my week' here. Keep it brief and energizing — 3-5 lines max."
  },
  "delivery": {
    "mode": "announce",
    "channel": "USER_CHANNEL",
    "to": "USER_CHANNEL_ID"
  }
}
```

### 2c. Mid-Week Pulse
**Purpose:** Quick check — are you on track for your weekly intentions?
**Schedule:** Wednesday at lunch (e.g., 12:30 PM).

```json
{
  "name": "Wayve Mid-Week Pulse",
  "schedule": {
    "kind": "cron",
    "expr": "30 12 * * 3",
    "tz": "USER_TIMEZONE"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Run a Wayve mid-week check: call wayve_get_planning_context for this week, then deliver a brief summary showing: activities completed vs planned per bucket, focus bucket progress, frequency target status, and one encouraging observation. If any bucket is at 0% completion, gently flag it. End with: 'View your week: https://gowayve.com/week'. Keep it concise and warm."
  },
  "delivery": {
    "mode": "announce",
    "channel": "USER_CHANNEL",
    "to": "USER_CHANNEL_ID"
  }
}
```

### 2d. Friday Momentum Check
**Purpose:** Heading into the weekend — what's still open? Anything to wrap up today?
**Schedule:** Friday afternoon (e.g., 3 PM).

```json
{
  "name": "Wayve Friday Check",
  "schedule": {
    "kind": "cron",
    "expr": "0 15 * * 5",
    "tz": "USER_TIMEZONE"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Run a Friday momentum check: call wayve_get_planning_context for this week. Show uncompleted activities and which could realistically still happen today or this weekend. Mention the Wrap Up ritual coming Sunday. End with: 'Check your calendar: https://gowayve.com/calendar'. Keep it brief and energizing — 'You've got two days to close strong.'"
  },
  "delivery": {
    "mode": "announce",
    "channel": "USER_CHANNEL",
    "to": "USER_CHANNEL_ID"
  }
}
```

---

## Category 3: Activity Reminders

### 3a. Per-Activity Reminders
**Purpose:** Remind the user X minutes before a scheduled activity starts.
**When to create:** When the user creates or schedules an activity with a specific time.

After creating/scheduling an activity, ask: "Want a reminder before this? I can ping you 15 minutes before."

The user can configure:
- **Default lead time**: applies to all activities (e.g., 15 min before)
- **Per-activity override**: "Remind me 1 hour before the dentist"
- **No reminder**: "No reminder for this one"

```json
{
  "name": "Reminder: Morning run",
  "schedule": {
    "kind": "at",
    "at": "2026-03-01T06:45:00+01:00"
  },
  "sessionTarget": "isolated",
  "deleteAfterRun": true,
  "payload": {
    "kind": "agentTurn",
    "message": "Send the user a brief activity reminder: their Morning run (30min, Health bucket) starts in 15 minutes. Include the link https://gowayve.com/calendar. Keep it to 2-3 lines."
  },
  "delivery": {
    "mode": "announce",
    "channel": "USER_CHANNEL",
    "to": "USER_CHANNEL_ID"
  }
}
```

**For recurring activities**: When an activity has a recurrence rule, create recurring cron reminders that match the pattern. E.g., "Gym every Mon/Wed/Fri at 7 AM" → reminder cron at 6:45 on those days:
```json
{
  "name": "Reminder: Gym",
  "schedule": {
    "kind": "cron",
    "expr": "45 6 * * 1,3,5",
    "tz": "USER_TIMEZONE"
  },
  ...
}
```

### 3b. Batch Daily Reminders
**Purpose:** Instead of individual per-activity reminders, send one consolidated reminder at the start of each time block.

Alternative approach if the user has many activities:

```json
{
  "name": "Wayve Next-Up Reminder",
  "schedule": {
    "kind": "cron",
    "expr": "0 8-21 * * *",
    "tz": "USER_TIMEZONE"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Check if the user has any Wayve activities starting in the next hour. Call wayve_daily_brief for today. If there's an activity starting within 60 minutes that hasn't been completed, send a brief reminder with the activity name, bucket, start time, and a link to https://gowayve.com/calendar. If nothing is coming up, do NOT send any message — stay silent."
  },
  "delivery": {
    "mode": "announce",
    "channel": "USER_CHANNEL",
    "to": "USER_CHANNEL_ID"
  }
}
```

---

## Category 4: Time Audit Check-ins

### 4a. Standard Time Audit (7-day)
**Purpose:** Prompt the user to log what they're doing every 30 minutes during an active audit.
**Duration:** Full audit period (e.g., 7 days).
**Schedule:** Every 30 min during active hours, every day for the audit duration.
**Auto-suggested:** When starting a time audit.

```json
{
  "name": "Wayve Time Audit Check-in",
  "schedule": {
    "kind": "cron",
    "expr": "*/30 8-20 * * *",
    "tz": "USER_TIMEZONE"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Send this check-in message to the user:\n\n⏱️ Time check!\n\nWhat have you been doing for the last 30 minutes?\nHow's your energy? (1=drained, 5=energized)\n\nQuick reply — e.g., \"emails, 2\" or \"gym, 5\"\n\n👉 https://gowayve.com/time-audit\n\nWhen the user replies, you MUST log their response immediately:\n1. Parse their reply — e.g., \"emails, 2\" means what_did_you_do: \"emails\", energy_level: 2\n2. Call wayve_get_planning_context to get the user's buckets, then match the activity to the right bucket\n3. Call wayve_manage_time_audit(action: \"log_entry\", audit_id: \"AUDIT_ID\", what_did_you_do: \"...\", energy_level: N, bucket_id: \"...\") to save the entry\n4. Confirm briefly: \"Logged: [activity] → [bucket], energy [N]/5 ✓\"\n\nDo NOT skip the wayve_manage_time_audit call. If you don't log it, the entry is lost."
  },
  "delivery": {
    "mode": "announce",
    "channel": "USER_CHANNEL",
    "to": "USER_CHANNEL_ID"
  }
}
```

**Important:** Replace `AUDIT_ID` in the message with the actual audit ID before creating this cron.

**Interval variations** (match `interval_minutes` from the audit config):
- 15min: `"*/15 8-20 * * *"`
- 30min: `"*/30 8-20 * * *"` (default)
- 60min: `"0 8-20 * * *"`

**Auto-cleanup:** When creating the audit check-in cron, also create a one-shot cleanup job that deletes the check-in cron when the audit ends:

```json
{
  "name": "Wayve Time Audit Cleanup",
  "schedule": {
    "kind": "at",
    "at": "AUDIT_END_DATE_T20:30:00+OFFSET"
  },
  "sessionTarget": "main",
  "deleteAfterRun": true,
  "payload": {
    "kind": "systemEvent",
    "text": "Time audit period ended. Delete the 'Wayve Time Audit Check-in' and 'Wayve Audit Daily Summary' cron jobs and generate the final audit report."
  }
}
```

### 4b. Time Audit Daily Summary
**Purpose:** End-of-day summary during an active audit — show the day's logged entries.
**Schedule:** Every evening during the audit period.

```json
{
  "name": "Wayve Audit Daily Summary",
  "schedule": {
    "kind": "cron",
    "expr": "0 21 * * *",
    "tz": "USER_TIMEZONE"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "The user has an active time audit. Call wayve_manage_time_audit(action: 'report', audit_id: 'AUDIT_ID') to get current stats. Deliver a brief daily summary: how many entries were logged today, top buckets by time, average energy level, and any patterns noticed. Encourage them to keep going — 'X days left in the audit.' End with: 'View your audit: https://gowayve.com/time-audit'"
  },
  "delivery": {
    "mode": "announce",
    "channel": "USER_CHANNEL",
    "to": "USER_CHANNEL_ID"
  }
}
```

### 4c. Time Audit Final Report
**Purpose:** When the audit period ends, invite the user to review their results together — not dump a report. This kicks off a coaching conversation (Phase E & F from `references/time-audit.md`).
**When to create:** Together with the check-in and daily summary crons at audit start.

```json
{
  "name": "Wayve Time Audit Final Report",
  "schedule": {
    "kind": "at",
    "at": "AUDIT_END_DATE_T10:00:00+OFFSET"
  },
  "sessionTarget": "isolated",
  "deleteAfterRun": true,
  "payload": {
    "kind": "agentTurn",
    "message": "The user's 7-day time audit just ended. Send them a warm congratulations — tracking for a full week takes commitment. Let them know you have their results ready and would love to walk through them together: where their time went, what energized vs. drained them, and what they might want to change. Include the link https://gowayve.com/time-audit and tell them to say 'show me my results' when they're ready. Keep it brief and inviting — 4-6 lines max."
  },
  "delivery": {
    "mode": "announce",
    "channel": "USER_CHANNEL",
    "to": "USER_CHANNEL_ID"
  }
}
```

### 4d. Time Audit Follow-Up
**Purpose:** One week after the audit ends, check in on how things are going — not to evaluate, but to offer support.
**When to create:** Together with the other audit crons at audit start.

```json
{
  "name": "Wayve Time Audit Follow-Up",
  "schedule": {
    "kind": "at",
    "at": "AUDIT_END_DATE_PLUS_7_DAYS_T10:00:00+OFFSET"
  },
  "sessionTarget": "isolated",
  "deleteAfterRun": true,
  "payload": {
    "kind": "agentTurn",
    "message": "It's been a week since the user's time audit ended. Send a casual check-in: ask how things are going, whether they've noticed any shifts in how they spend their time. No pressure — even small changes count. Offer to look at this week together. Include links to https://gowayve.com/analytics and https://gowayve.com/week. Keep it warm and brief — 4-6 lines max."
  },
  "delivery": {
    "mode": "announce",
    "channel": "USER_CHANNEL",
    "to": "USER_CHANNEL_ID"
  }
}
```

---

## Category 5: Bucket & Goal Tracking

### 5a. Neglected Bucket Alert
**Purpose:** If a bucket hasn't had any activity in X days, send a gentle nudge.
**Schedule:** Daily check (e.g., 10 AM).

```json
{
  "name": "Wayve Bucket Balance Check",
  "schedule": {
    "kind": "cron",
    "expr": "0 10 * * *",
    "tz": "USER_TIMEZONE"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Call wayve_get_planning_context for this week. Check which buckets have 0 completed activities so far this week. If it's Wednesday or later and a bucket has zero completions, send a gentle nudge: 'Your [bucket] bucket hasn't had any love this week yet. Even 15 minutes would make a difference. Want me to find a slot?' Include a link to https://gowayve.com/buckets. If all buckets have at least one completion, do NOT send any message — stay silent."
  },
  "delivery": {
    "mode": "announce",
    "channel": "USER_CHANNEL",
    "to": "USER_CHANNEL_ID"
  }
}
```

### 5b. Project Milestone Check
**Purpose:** Track progress on projects with targets (e.g., "read 100 pages").
**Schedule:** Weekly (e.g., Thursday evening) — gives time to push before the week ends.

```json
{
  "name": "Wayve Project Progress",
  "schedule": {
    "kind": "cron",
    "expr": "0 19 * * 4",
    "tz": "USER_TIMEZONE"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Check the user's active projects via wayve_get_planning_context. For any project with a target_value, show progress: current_value / target_value (percentage). If any project is behind pace, mention it gently. If a project is ahead of schedule, celebrate. End with: 'View your projects: https://gowayve.com/projects'. Keep it to 3-5 lines."
  },
  "delivery": {
    "mode": "announce",
    "channel": "USER_CHANNEL",
    "to": "USER_CHANNEL_ID"
  }
}
```

### 5c. Frequency Target Daily Tracker
**Purpose:** Check if the user is on track for their weekly frequency targets.
**Schedule:** Every evening (e.g., 8 PM).

```json
{
  "name": "Wayve Frequency Check",
  "schedule": {
    "kind": "cron",
    "expr": "0 20 * * *",
    "tz": "USER_TIMEZONE"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Call wayve_get_frequency_progress for this week. If any bucket is behind its frequency target with fewer days remaining than sessions needed (e.g., target 3x/week but only done 0x and it's Thursday), send a brief heads-up with a link to https://gowayve.com/week. If everything is on track, stay silent — no message needed."
  },
  "delivery": {
    "mode": "announce",
    "channel": "USER_CHANNEL",
    "to": "USER_CHANNEL_ID"
  }
}
```

---

## Category 6: Smart Reminders & One-Shots

### 6a. One-Shot Reminders
**Purpose:** User says "remind me to call the dentist tomorrow at 3 PM."

```json
{
  "name": "Reminder: Call the dentist",
  "schedule": {
    "kind": "at",
    "at": "2026-03-01T15:00:00+01:00"
  },
  "sessionTarget": "isolated",
  "deleteAfterRun": true,
  "payload": {
    "kind": "agentTurn",
    "message": "Send the user a reminder they requested: 'Call the dentist'. Keep it brief — just the reminder and a link to https://gowayve.com/dashboard. 2-3 lines max."
  },
  "delivery": {
    "mode": "announce",
    "channel": "USER_CHANNEL",
    "to": "USER_CHANNEL_ID"
  }
}
```

### 6b. Follow-Up Reminders
**Purpose:** After a coaching conversation (life audit, time audit review), schedule a follow-up to check if they acted on recommendations.
**When to create:** After completing a Life Audit or Time Audit review.

```json
{
  "name": "Wayve Follow-Up: Life Audit Actions",
  "schedule": {
    "kind": "at",
    "at": "2026-03-08T10:00:00+01:00"
  },
  "sessionTarget": "isolated",
  "deleteAfterRun": true,
  "payload": {
    "kind": "agentTurn",
    "message": "The user completed a life audit last week. Check wayve_manage_knowledge for insights saved during the audit. Ask the user: 'Last week we identified some changes you wanted to make — [reference specific insights]. How's that going? Want to adjust your plan?' Include links to relevant pages: https://gowayve.com/analytics for their trends, https://gowayve.com/week to adjust their plan. Keep it conversational and warm."
  },
  "delivery": {
    "mode": "announce",
    "channel": "USER_CHANNEL",
    "to": "USER_CHANNEL_ID"
  }
}
```

### 6c. Streak Celebration
**Purpose:** If the user has completed a recurring activity for X weeks in a row, celebrate the streak.
**Schedule:** Weekly check (Sunday morning, before Wrap Up).

```json
{
  "name": "Wayve Streak Checker",
  "schedule": {
    "kind": "cron",
    "expr": "0 10 * * 0",
    "tz": "USER_TIMEZONE"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Call wayve_get_analytics with action 'task_patterns' to check for completion streaks. If any recurring activity has been completed for 3+ consecutive weeks, send a brief celebration message. E.g., '🔥 4-week streak on Morning Run! That's consistency.' Include a link to https://gowayve.com/analytics to see their full trends. If no notable streaks, stay silent."
  },
  "delivery": {
    "mode": "announce",
    "channel": "USER_CHANNEL",
    "to": "USER_CHANNEL_ID"
  }
}
```

---

## Category 7: Monthly & Seasonal

### 7a. Monthly Life Audit Prompt
**Purpose:** Once a month, suggest a full life audit to review patterns over a longer period.
**Schedule:** First Sunday of each month.

```json
{
  "name": "Wayve Monthly Audit Prompt",
  "schedule": {
    "kind": "cron",
    "expr": "0 11 1-7 * 0",
    "tz": "USER_TIMEZONE"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Send the user a monthly check-in nudge. It's the first week of the month — suggest a life audit to review trends across all their life buckets. Mention you can pull energy patterns, happiness data, and help spot what's working. Include the link https://gowayve.com/analytics and let them know they can say 'life audit' when ready. Keep it warm and brief — 4-6 lines max."
  },
  "delivery": {
    "mode": "announce",
    "channel": "USER_CHANNEL",
    "to": "USER_CHANNEL_ID"
  }
}
```

---

## Category 8: Weekly Suggestion Scan

### 8a. Smart Suggestions Weekly Scan
**Purpose:** Review pending smart suggestions and create new ones based on the week's data.
**Schedule:** Sunday morning, before the Wrap Up reminder.

```json
{
  "name": "Wayve Smart Suggestions Scan",
  "schedule": {
    "kind": "cron",
    "expr": "0 10 * * 0",
    "tz": "USER_TIMEZONE"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Run a weekly smart suggestions scan for the user. First, call wayve_manage_smart_suggestions(action: 'list', status_filter: 'pending') to check existing suggestions. Then call wayve_get_analytics(action: 'producer_score') and wayve_get_analytics(action: 'task_patterns') to spot new patterns. If you notice recurring energy drains, neglected buckets, or completion trend changes, create new suggestions via wayve_manage_smart_suggestions(action: 'create'). Do NOT present suggestions to the user in this scan — just create them silently. They'll surface during the next Wrap Up or Fresh Start conversation."
  },
  "delivery": {
    "mode": "silent",
    "channel": "USER_CHANNEL",
    "to": "USER_CHANNEL_ID"
  }
}
```

---

## Suggested Automation Bundles

When setting up automations, offer these pre-configured bundles:

### Starter Bundle (after onboarding)
- Morning Daily Brief (weekdays)
- Sunday Wrap Up Reminder
- Monday Fresh Start Reminder

### Full Rhythm Bundle
Everything in Starter, plus:
- Evening Wind-Down (daily)
- Mid-Week Pulse (Wednesday)
- Friday Momentum Check
- Frequency Target Tracker (daily)
- Monthly Life Audit Prompt

### Activity Reminders Bundle
- Per-activity reminders (15 min before, configurable)
- Or: Hourly next-up batch reminder

### Time Audit Bundle (temporary)
- 30-min check-in during active hours
- Daily audit summary
- Auto-cleanup when audit ends
- Final report with review + action plan
- Follow-up check one week after audit ends

Ask the user: "Which bundle sounds right for you? We can always add or remove individual automations later."

---

## Setup Flow

When offering automations to the user:

1. **Ask what they want**: "I can set up proactive check-ins. Want the Starter Bundle (morning brief + weekly rituals) or something more comprehensive?"
2. **Confirm timezone**: "What timezone are you in?" → save via `wayve_manage_knowledge`
3. **Confirm delivery channel**: "Where should I send these — Telegram, Slack, or somewhere else?"
4. **Confirm times**: Walk through each automation, confirm or adjust times
5. **Ask about activity reminders**: "Do you want reminders before scheduled activities? How many minutes before?"
6. **Create the jobs**: Use `cron.add` for each
7. **Save the setup**: Store active automations via `wayve_manage_knowledge` (category: `automations`, key: `active_crons`, value: JSON summary of names + schedules)
8. **Explain management**: "You can always say 'pause my morning briefs', 'change my wrap up time', or 'stop all reminders' and I'll adjust."

## Managing Automations

When the user asks to change, pause, or remove automations:

- **List active jobs**: `cron.list` — show what's running with human-readable schedule
- **Update schedule**: `cron.update` with new expression
- **Pause**: `cron.update` with `enabled: false`
- **Resume**: `cron.update` with `enabled: true`
- **Delete**: `cron.remove` by job name or ID
- **Snooze**: "Skip tomorrow's morning brief" → pause and create one-shot re-enable

Always update the knowledge base when automations change.

## Security Constraints

All automations in this skill are subject to these rules:

- **User approval required** — every cron job must be explicitly approved by the user before creation. Never create automations silently.
- **Wayve tools only** — cron payloads may only call `wayve_*` tools (e.g., `wayve_manage_time_audit`, `wayve_get_planning_context`, `wayve_daily_brief`). No system commands, file access, or external API calls.
- **No arbitrary code execution** — cron payloads describe what to say or which wayve tools to call. They do not execute shell commands or modify the user's system.
- **Links limited to gowayve.com** — all links in cron messages point to `gowayve.com` subpaths only.
- **User can stop at any time** — the user can say "stop all reminders" or "delete all crons" and the agent must comply immediately.

## Best Practices

- **Always ask before creating** — never silently set up cron jobs
- **Always include app links** — every notification should link to the relevant page on `gowayve.com` so the user can take action directly
- **Use `agentTurn` + `announce`** for anything the user needs to see (not `systemEvent`)
- **Use descriptive instructions** for all messages — describe what to say, not the exact words. This keeps AI safety filters active and allows natural tone variation.
- **Use data-fetching instructions** for briefs/checks where the AI should call tools and summarize results
- **Conditional silence**: Many automations should stay silent when there's nothing to report (e.g., bucket balance check when everything is on track). Always include "If nothing notable, do NOT send any message" in the payload.
- **Include the user's timezone** in every cron job — never use UTC without explicit conversion
- **Save automation state** to knowledge base so future sessions know what's active
- **Clean up temporary crons** (time audit, one-shots) when their purpose is fulfilled
- **Respect quiet hours** — never schedule notifications during sleep time (check user preferences for `sleep_hours_per_day`)
- **Activity reminders need cleanup** — when an activity is deleted, completed, or rescheduled, update or remove its reminder cron
- **Don't over-notify** — if the user has 8 activities in a day, batch reminders are better than 8 individual pings. Ask the user's preference.
