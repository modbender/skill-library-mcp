---
name: gamification
version: 1.1.0
description: XP system for productivity gamification via ClawdBot - track levels, badges, streaks, and achievements
author: ClawdBot
category: productivity
tags:
  - gamification
  - xp
  - levels
  - badges
  - streaks
  - habits
  - productivity
  - motivation
  - achievements
  - goals
env:
  - name: SUPABASE_URL
    description: Supabase project URL for gamification data storage
    required: true
  - name: SUPABASE_SERVICE_KEY
    description: Supabase service role key for database access
    required: true
keywords:
  - earn xp
  - level up
  - streak bonus
  - habit tracking
  - goal milestones
  - leaderboard
  - accountability
triggers:
  - my xp
  - what level am I
  - my badges
  - leaderboard
  - xp stats
  - gamification stats
---

# Gamification & XP System

Turn productivity into a game with XP, levels, badges, streaks, and achievements. Every completed task, habit, and goal milestone earns XP toward leveling up.

## ClawdBot Integration

This skill is designed for **ClawdBot** - it provides the prompt interface for ClawdBot's gamification API server which stores data in Supabase.

**Architecture:**
```
User → ClawdBot Gateway → ClawdBot API Server → Supabase (Postgres)
                         (Railway)              (user_gamification, xp_transactions tables)
```

The backend implementation lives in `api-server/src/routes/gamification.ts` and `api-server/src/lib/xp-engine.ts`.

## Features

- **XP System**: Earn XP for habits, tasks, and goal milestones
- **Leveling**: Level up with formula `XP = 50 * (level^2)`
- **Streak Bonuses**: Up to 2.0x multiplier for consistent habits
- **Badges**: Earn badges for achievements and milestones
- **Leaderboard**: Compare progress (multi-user support)
- **Accountability**: Track commitment and earn-back system

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Yes | Supabase service role key |

## API Endpoints

All endpoints are relative to the ClawdBot API server (`{CLAWDBOT_API_URL}/api/gamification/`).

### Get User Stats
```
GET /api/gamification/stats/:userId
```

Response:
```json
{
  "totalXp": 2450,
  "currentLevel": 7,
  "weeklyXp": 350,
  "monthlyXp": 1200,
  "progress": {
    "xpInLevel": 150,
    "xpNeeded": 450,
    "percent": 33
  },
  "accountability": {
    "balance": 50,
    "totalSlashed": 10,
    "totalEarnedBack": 60
  }
}
```

### Get Recent Transactions
```
GET /api/gamification/transactions/:userId?limit=20
```

### Get User Badges
```
GET /api/gamification/badges/:userId
```

### Award XP (Internal)
```
POST /api/gamification/award
{
  "userId": "302137836",
  "amount": 50,
  "source": "habit",
  "sourceId": "morning-routine",
  "note": "Completed morning routine"
}
```

### Complete Habit (with streak bonus)
```
POST /api/gamification/habit-complete
{
  "userId": "302137836",
  "habitId": "workout",
  "currentStreak": 7
}
```

### Complete Task
```
POST /api/gamification/task-complete
{
  "userId": "302137836",
  "taskId": "task-123",
  "priority": 8
}
```

### Goal Milestone
```
POST /api/gamification/goal-milestone
{
  "userId": "302137836",
  "goalId": "goal-456",
  "milestonePercent": 50
}
```

### Award Badge
```
POST /api/gamification/badge
{
  "userId": "302137836",
  "badgeType": "early_bird",
  "metadata": { "streak": 30 }
}
```

### Get Leaderboard
```
GET /api/gamification/leaderboard
```

### Get XP Config
```
GET /api/gamification/config
```

## Database Tables

This skill requires the following Supabase tables:
- `user_gamification` - User XP totals, levels, streaks
- `xp_transactions` - XP award history
- `user_badges` - Earned badges

## XP Rewards

| Action | Base XP | Notes |
|--------|---------|-------|
| Habit completion | 10-50 | + streak bonus up to 2x |
| Task completion | 5-50 | Based on priority (1-10) |
| Goal 25% milestone | 100 | First quarter |
| Goal 50% milestone | 200 | Halfway |
| Goal 75% milestone | 300 | Three quarters |
| Goal 100% completion | 500 | Full completion |

## Example Usage

### Check Progress
```
"What's my XP level?"
"How close am I to leveling up?"
"Show my gamification stats"
```

### View Achievements
```
"What badges do I have?"
"Show my recent XP transactions"
"What's my current streak?"
```

### Leaderboard
```
"Show the leaderboard"
"Who has the most XP?"
```

## Related

- `goals` - Set and track goals
- `habits` - Habit tracking system
- `remind` - Reminder system
- `daily-briefing` - Daily progress summary
