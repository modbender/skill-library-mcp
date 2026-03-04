---
name: garmin-skill
description: Talk to your Garmin data — ask questions about your activities, training load, VO2 Max, heart rate zones, and more using AI.
homepage: https://www.transition.fun
---

# Garmin Skill

Chat with your Garmin Connect data using AI. Ask about your runs, rides, swims, training load, VO2 Max, heart rate zones, and performance trends. Powered by [Transition](https://www.transition.fun), which syncs with Garmin Connect to give AI agents access to your training data.

## Setup

1. Download [Transition](https://www.transition.fun) and connect your Garmin account
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

Ask questions about your Garmin data. The AI coach has full context on your activities, training load, and performance.

```bash
curl -X POST -H "X-API-Key: $TRANSITION_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "How has my running volume changed this month compared to last?"}' \
  "https://api.transition.fun/api/v1/coach/chat"
```

Example questions:
- "What was my longest run this week?"
- "How is my VO2 Max trending?"
- "Am I overtraining based on my recent Garmin data?"
- "Compare my cycling power this month vs last month"
- "What does my heart rate data say about my fitness?"

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

Get CTL (fitness), ATL (fatigue), and TSB (form) calculated from your Garmin activities.

```bash
curl -H "X-API-Key: $TRANSITION_API_KEY" \
  "https://api.transition.fun/api/v1/performance/pmc"
```

### Performance Stats

Get FTP, threshold paces, heart rate zones, and other metrics derived from your Garmin data.

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

### Push Workout to Garmin

Send a scheduled workout directly to your Garmin device.

```bash
curl -X POST -H "X-API-Key: $TRANSITION_API_KEY" \
  "https://api.transition.fun/api/v1/workouts/123/push-garmin"
```

## Rate Limits

| Tier | Read Endpoints | AI Endpoints |
|------|---------------|-------------|
| Free | 100/day | 3/day |
| Paid | 10,000/day | 100/day |

## Tips for Agents

1. **Use coach chat as the primary interface.** It has full context on the user's Garmin activities, training load, and performance — just ask natural questions.

2. **Check fatigue before recommending hard workouts.** Call `GET /api/v1/performance/pmc` and look at TSB. If TSB is below -20, the athlete is fatigued.

3. **Use the free WOD endpoint for quick workouts.** No auth needed — great for users who just want a workout suggestion.

4. **Date format is always YYYY-MM-DD** for all date parameters.
