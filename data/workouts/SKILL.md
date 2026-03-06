---
name: Workouts
description: Build a personal workout tracking system with exercises, routines, progression, and PRs.
metadata: {"clawdbot":{"emoji":"💪","os":["linux","darwin","win32"]}}
---

## Core Behavior
- User logs a workout → record exercises, sets, reps, weight
- Track progression → surface PRs, trends, plateaus
- Suggest based on history → "last time you did 3x8 at 60kg"
- Create `~/workouts/` as workspace

## When User Logs a Workout
- Date and type: strength, cardio, flexibility, sport
- Exercises performed with details
- How it felt: easy, moderate, hard, failed
- Duration if relevant
- Notes: energy, sleep, soreness

## Strength Training Log
- Exercise name (standardized)
- Sets x reps x weight: "3x8 @ 60kg"
- Rest periods if tracking
- RPE (rate of perceived exertion) optional
- Note failed reps: "3x8, failed last rep set 3"

## Cardio Log
- Activity: running, cycling, swimming, rowing
- Duration and distance
- Pace or heart rate if tracking
- Route or location optional
- Conditions: weather, terrain

## Exercise Database
Build personal exercise list over time:
- Name (consistent spelling matters for tracking)
- Category: push, pull, legs, core, cardio
- Equipment needed
- Notes: cues, form reminders, variations

## Routine/Program Structure
```
~/workouts/
├── logs/
│   ├── 2024-03-15.md
│   └── 2024-03-17.md
├── routines/
│   ├── push-day.md
│   └── pull-day.md
├── exercises.md
└── prs.md
```

## Personal Records
- Track PRs automatically by exercise
- 1RM, 3RM, 5RM for lifts
- Distance/time PRs for cardio
- Surface when broken: "New squat PR: 100kg!"
- Historical PR list with dates

## Progression Tracking
- Compare to last session: "Bench: last time 3x8@55kg"
- Suggest next weight: "Try 57.5kg or add a rep"
- Weekly volume trends: total sets, reps, tonnage
- Spot plateaus: "Squat hasn't progressed in 4 weeks"

## Rest and Recovery
- Track rest days between muscle groups
- Flag overtraining signs: same muscle group too frequent
- Note recovery quality: sleep, soreness, energy
- "You've done 5 leg days in 8 days — consider rest"

## Progressive Enhancement
- Week 1: simple log of what you did
- Week 2: standardize exercise names
- Month 2: add routines/programs
- Month 3: PR tracking and progression analysis
- Ongoing: adjust based on patterns

## Routine Templates
- Define standard workout: exercises, sets, reps
- Log actual vs planned: what you intended vs did
- Modify routines based on what works
- Multiple routines: PPL, upper/lower, full body

## What To Surface Proactively
- "Leg day? Last time: squats 3x5@90kg, RDL 3x10@60kg"
- "Bench PR incoming — you did 3x5@80kg last time"
- "Haven't done deadlifts in 3 weeks"
- "Volume is up 20% this month — watch for fatigue"

## Common Metrics
- Volume: sets × reps × weight per muscle/week
- Frequency: sessions per week, per muscle group
- Progression: weight/reps increase over time
- Consistency: workouts per week/month

## What NOT To Suggest
- Complex periodization before basics are consistent
- Calorie/macro tracking in workout log — separate concern
- App with features they won't use
- Comparing to others — track personal progress only

## Injury and Deload Notes
- Log injuries with date, severity, affected exercises
- Track modified exercises during recovery
- Deload weeks: intentional reduced volume
- "Left shoulder tweak March 2024 — avoided overhead pressing 3 weeks"

## Integration Points
- Habits: "workout 4x/week" as habit
- Calendar: schedule workout days
- Health: weight, measurements if tracking body composition
