---
name: Habits
description: Build a personal habit tracking system with streaks, reviews, and progression.
metadata: {"clawdbot":{"emoji":"✅","os":["linux","darwin","win32"]}}
---

## Core Behavior
- User mentions doing something regularly → offer to track as habit
- Daily check-in prompt if enabled → "Did you do X today?"
- Surface streaks and patterns → motivation through visibility
- Create `~/habits/` as workspace

## When User Mentions Habits
- "I want to exercise more" → create habit, define frequency
- "Did my morning routine" → log completion
- "Skipped meditation today" → log miss, no judgment
- "How am I doing with reading?" → show stats and streak

## Habit Definition
- Name: clear, specific action
- Frequency: daily, weekdays, 3x/week, weekly
- Time of day: morning, evening, anytime (optional)
- Minimum viable version: "at least 10 minutes" beats "1 hour"
- Why: motivation reminder for hard days

## Tracking File Structure
Simple approach — one file per habit:
```
~/habits/
├── exercise.md
├── reading.md
├── meditation.md
└── summary.md
```

Each habit file has log entries:
- Date, done (yes/no), notes
- Keep entries minimal — friction kills tracking

## Streak Tracking
- Current streak: consecutive completions
- Best streak: all-time record
- Show both — current motivates, best sets target
- Streak freezes optional — planned breaks don't reset

## Frequency Types
- Daily: every day, streak breaks on miss
- Weekdays: Mon-Fri only, weekends don't count
- X per week: 3 of 7 days, flexible which days
- Weekly: once per week minimum

## Check-in Prompts
- Offer daily summary prompt at consistent time
- "Quick check: exercise, reading, meditation — which did you do?"
- Batch check-in reduces friction vs individual prompts
- Skip prompt if user already logged today

## Progressive Enhancement
- Week 1: track 1-3 habits max, daily log
- Week 2: add streak visibility
- Month 2: weekly review summaries
- Month 3: pattern analysis, adjustment suggestions

## Weekly Review
- Completion rate per habit
- Which days strongest/weakest
- Streak status and changes
- Prompt: "Any habits to add, remove, or modify?"

## Common Patterns to Surface
- "You never miss on Tuesdays but struggle Fridays"
- "Your streak usually breaks after 14 days"
- "Morning habits have higher completion than evening"
- Insights without judgment — user decides action

## What NOT To Suggest
- Starting with 10 habits — 2-3 max initially
- Complex scoring systems — done/not-done is enough
- Punishment for misses — shame doesn't build habits
- Rigid tracking apps — files give flexibility

## Minimum Viable Habit
- Make habits small enough to always be possible
- "Do one pushup" beats "workout 45 minutes"
- Track the minimum, do more if energy allows
- Consistency beats intensity for habit formation

## Handling Misses
- Log the miss without drama — data, not judgment
- Note reason if helpful: sick, traveling, forgot
- Streak resets but history remains — progress isn't lost
- "Missed yesterday, did today" is still progress

## Habit Graduation
- Some habits become automatic — consider retiring from active tracking
- "I don't need to track brushing teeth anymore"
- Archive to completed habits, celebrate the win
- Make room for new habits to build

## Integration Points
- Calendar: block time for habits
- Morning/evening routine: bundle related habits
- Contacts: accountability partner check-ins if wanted
- Journal: reflect on habit patterns
