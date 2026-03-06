---
name: lofy-fitness
description: Fitness accountability for the Lofy AI assistant — workout logging from natural language, meal tracking with calorie/protein estimates, PR detection with Epley formula, gym reminders based on weekly targets, and progress reports. Use when logging workouts, meals, tracking fitness PRs, or generating weekly fitness summaries.
---

# Fitness Tracker — Workout & Health Accountability

Tracks workouts, meals, PRs, and fitness consistency. An accountability layer that keeps the user honest through natural conversation.

## Data File: `data/fitness.json`

```json
{
  "profile": { "goal": "", "weight_log": [], "start_date": null },
  "workouts": [],
  "meals": [],
  "prs": {},
  "weekly_summary": [],
  "current_week": { "workout_count": 0, "target": 0, "workouts": [] }
}
```

### Workout Entry Format
```json
{
  "date": "2026-02-07",
  "type": "strength",
  "muscle_groups": ["chest", "triceps"],
  "exercises": [
    { "name": "Bench Press", "sets": [{"weight": 185, "reps": 5}] }
  ],
  "duration_min": 60,
  "notes": ""
}
```

### Meal Entry Format
```json
{
  "date": "2026-02-07",
  "meal": "lunch",
  "description": "Chicken bowl with rice",
  "estimated_calories": 650,
  "estimated_protein_g": 45,
  "time": "12:30"
}
```

## Parsing Natural Language

### Workouts
- "bench 185x5 185x4" → Bench Press, 2 sets: 185×5, 185×4
- "tricep pushdowns 50x12 x3" → 3 sets of 50×12
- "went for a 5k run, 28 minutes" → cardio, running, 5km, 28min
- "did legs" (no details) → log muscle group, note "details not provided", still counts

### Meals
- "had chipotle for lunch" → estimate ~650 cal, ~40g protein
- "protein shake after gym" → estimate ~200 cal, ~30g protein
- "skipped breakfast" → note it; if 3+ day pattern, gently mention

### PR Detection
After parsing workouts, check each exercise against stored PRs:
- Epley 1RM = weight × (1 + reps/30)
- If new 1RM exceeds stored PR: update and celebrate
- Only celebrate PRs, not every workout

## Instructions

1. Always read `data/fitness.json` before responding about fitness
2. Update the JSON immediately after any fitness conversation
3. Keep responses short — log confirmation + one comment
4. Nudge logic: max 1 gym reminder per day, only if behind weekly target
5. Track consistency over intensity — showing up matters more
6. If user mentions injury or pain, suggest rest. Never push through pain
7. Weekly report: show trends (improving? plateauing? declining?) with data
