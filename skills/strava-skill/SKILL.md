---
name: strava-skill
description: Talk to your Strava data — ask questions about your activities, fitness trends, PRs, and training load using AI.
homepage: https://www.transition.fun
---

# Strava Skill

Chat with your Strava data using AI. Ask about your activities, fitness trends, personal records, training load, and more. Powered by [Transition](https://www.transition.fun), which syncs with Strava to give AI agents access to your training data.

## Setup

1. Download [Transition](https://www.transition.fun) and connect your Strava account
2. Go to **Settings > API Keys** and tap **Generate New Key**
3. Set the environment variable:

```bash
export TRANSITION_API_KEY="tr_live_xxxxxxxxxxxxxxxxxxxxx"
```

## No Auth Required

### Workout of the Day

Generate a random structured workout — no account needed.

```bash
curl "https://api.transition.fun/api/v1/wod?sport=run&duration=45"
```

**Parameters:**
- `sport` — `run`, `bike`, `swim`, or `strength` (default: `run`)
- `duration` — minutes, 10-300 (default: `45`)

## Authenticated Endpoints

**Base URL:** `https://api.transition.fun`
**Auth:** Pass `X-API-Key` header on every request.

### AI Coach Chat

Ask questions about your Strava data. The AI coach has full context on your activities and performance.

```bash
curl -X POST -H "X-API-Key: $TRANSITION_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "How did my long run this week compare to last week?"}' \
  "https://api.transition.fun/api/v1/coach/chat"
```

Example questions:
- "What's my weekly mileage trend over the last month?"
- "How is my cycling FTP progressing?"
- "Am I running more or less than usual this week?"
- "What was my fastest 5K effort recently?"
- "Should I rest or train today based on my recent activity?"

### Get Workouts

Retrieve scheduled workouts for a date range.

```bash
curl -H "X-API-Key: $TRANSITION_API_KEY" \
  "https://api.transition.fun/api/v1/workouts?start=2026-02-09&end=2026-02-15"
```

**Parameters:**
- `start` — Start date (YYYY-MM-DD, required)
- `end` — End date (YYYY-MM-DD, required)
- Maximum range between `start` and `end` is 90 days.

### Performance Management Chart (PMC)

Get CTL (fitness), ATL (fatigue), and TSB (form) calculated from your Strava activities.

```bash
curl -H "X-API-Key: $TRANSITION_API_KEY" \
  "https://api.transition.fun/api/v1/performance/pmc"
```

### Performance Stats

Get FTP, threshold paces, heart rate zones, and other metrics derived from your Strava data.

```bash
curl -H "X-API-Key: $TRANSITION_API_KEY" \
  "https://api.transition.fun/api/v1/performance/stats"
```

### Athlete Profile

```bash
curl -H "X-API-Key: $TRANSITION_API_KEY" \
  "https://api.transition.fun/api/v1/profile"
```

### Chat History

```bash
curl -H "X-API-Key: $TRANSITION_API_KEY" \
  "https://api.transition.fun/api/v1/coach/history"
```

## Rate Limits

| Tier | Read Endpoints | AI Endpoints |
|------|---------------|-------------|
| Free | 100/day | 3/day |
| Paid | 10,000/day | 100/day |

## Tips for Agents

1. **Use coach chat as the primary interface.** It has full context on the user's Strava activities, training load, and performance — just ask natural questions.

2. **Check fatigue before recommending hard workouts.** Call `GET /api/v1/performance/pmc` and look at TSB. If TSB is below -20, the athlete is fatigued.

3. **Use the free WOD endpoint for quick workouts.** No auth needed — great for users who just want a workout suggestion.

4. **Date format is always YYYY-MM-DD** for all date parameters.
