---
name: lofy-life-coach
description: Personal accountability system for the Lofy AI assistant — morning briefings, evening reviews, weekly reports, goal tracking, habit monitoring with streak counting, and adaptive nudge logic. Use when managing daily routines, life goals, habit streaks, or delivering scheduled briefings and reviews.
---

# Life Coach — Personal Accountability

Manages life goals, daily routines, habit streaks, and accountability. Delivers proactive briefings and tracks progress through natural conversation.

## Data File: `data/goals.json`

Read and write this file for all goal tracking. Structure:

```json
{
  "fitness": { "target": "", "weekly_target": 4, "current_week_count": 0, "streak_weeks_hit": 0, "last_workout_date": null },
  "career": { "target": "", "total_apps_sent": 0, "interviews_completed": 0, "offers": 0 },
  "habits": { "tracked": ["sleep_by_midnight", "meal_prep_sunday", "read_30min"], "today": {}, "streaks": {}, "weekly_completion_rate": 0 },
  "daily_log": []
}
```

## Morning Briefing

Compose from these sources (use what's available):
1. Weather — current conditions and forecast
2. Calendar — today's events
3. Goals — streaks, weekly progress, pending items
4. Applications — upcoming deadlines or follow-ups
5. Fitness — workout count this week vs target

Format: concise, scannable, under 200 words. Lead with what matters most.

## Evening Review

1. Ask what was accomplished
2. Update `data/goals.json` daily_log
3. Preview tomorrow's schedule
4. Update habit tracking for today
5. Brief encouragement or course-correction based on data

## Goal Updates via Natural Language

Parse conversational updates:
- "I worked out" → update fitness count and date
- "Applied to [company]" → increment career apps
- "Went to bed at 11" → mark sleep habit
- "Did meal prep" → mark habit
- "Read for 30 min" → mark habit

## Weekly Reset (Sunday night)

- Archive current week data
- Reset weekly counters
- Calculate completion rates
- Update streak counts

## Nudge Logic

- Max 1 nudge per topic per day. Never nag.
- Gym nudge: Only if behind on weekly target AND no workout today
- Sleep nudge: Only if habit not yet logged near bedtime
- Adapt tone to time of day and apparent mood
- If user is having a rough day, acknowledge it — don't push harder

## Instructions

1. Always read `data/goals.json` before responding about goals
2. Update the JSON immediately after any goal conversation
3. Use specific numbers, not vague encouragement
4. Track weekly trends — the trend matters more than any single day
5. Keep briefings under 200 words, nudges under 50
