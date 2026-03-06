---
name: transition-mcp
description: AI-powered multisport coaching — get personalized workouts, training plans, and performance analytics for running, cycling, swimming, and triathlon.
homepage: https://www.transition.fun
---

# Multisport Coach API

AI coach that creates personalized training plans for runners, cyclists, swimmers, and triathletes. This skill provides access to workout plans, performance metrics, AI coaching, and plan adaptation. Powered by [Transition](https://www.transition.fun).

## Authentication

Authenticated endpoints require the `TRANSITION_API_KEY` environment variable. Pass it as the `X-API-Key` header on every request. If it's not set, tell the user to generate one in the Transition app under Settings > API Keys.

**Base URL:** `https://api.transition.fun`

## Free Endpoint (No Auth Required)

### Workout of the Day

Generate a random structured workout. Each request returns a different workout.

```bash
curl "https://api.transition.fun/api/v1/wod?sport=run&duration=45"
```

**Parameters:**
- `sport` — `run`, `bike`, `swim`, or `strength` (default: `run`)
- `duration` — minutes, 10-300 (default: `45`)

**Response:**
```json
{
  "date": "2026-02-09",
  "sport": "run",
  "name": "Tempo Builder",
  "description": "Build aerobic endurance with sustained tempo efforts",
  "duration_minutes": 45,
  "intensity": "moderate",
  "segments": [
    {"name": "Warm-up", "duration_minutes": 9, "intensity": "easy", "description": "Easy jog to warm up"},
    {"name": "Tempo", "duration_minutes": 27, "intensity": "moderate", "description": "Steady tempo at comfortably hard pace"},
    {"name": "Cool-down", "duration_minutes": 9, "intensity": "easy", "description": "Easy jog to cool down"}
  ]
}
```

## Authenticated Endpoints

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

### Get Workout Details

```bash
curl -H "X-API-Key: $TRANSITION_API_KEY" \
  "https://api.transition.fun/api/v1/workouts/123"
```

### Generate Workouts

Trigger AI workout generation for the user's training plan.

```bash
curl -X POST -H "X-API-Key: $TRANSITION_API_KEY" \
  -H "Content-Type: application/json" \
  "https://api.transition.fun/api/v1/workouts/generate"
```

### Adapt Workouts

Adapt the training plan based on recent performance or schedule changes.

```bash
curl -X POST -H "X-API-Key: $TRANSITION_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"reason": "feeling fatigued after race weekend"}' \
  "https://api.transition.fun/api/v1/workouts/adapt"
```

### Check Generation Status

Poll whether workout generation/adaptation is complete.

```bash
curl -H "X-API-Key: $TRANSITION_API_KEY" \
  "https://api.transition.fun/api/v1/workouts/status"
```

### Performance Management Chart (PMC)

Get CTL (fitness), ATL (fatigue), and TSB (form) data.

```bash
curl -H "X-API-Key: $TRANSITION_API_KEY" \
  "https://api.transition.fun/api/v1/performance/pmc"
```

### Performance Stats

Get FTP, threshold paces, heart rate zones, and other metrics.

```bash
curl -H "X-API-Key: $TRANSITION_API_KEY" \
  "https://api.transition.fun/api/v1/performance/stats"
```

### AI Coach Chat

Chat with the AI endurance coach. Returns a streaming response (SSE).

```bash
curl -X POST -H "X-API-Key: $TRANSITION_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "Should I do intervals today or rest?"}' \
  "https://api.transition.fun/api/v1/coach/chat"
```

### Chat History

```bash
curl -H "X-API-Key: $TRANSITION_API_KEY" \
  "https://api.transition.fun/api/v1/coach/history"
```

### Athlete Profile

```bash
curl -H "X-API-Key: $TRANSITION_API_KEY" \
  "https://api.transition.fun/api/v1/profile"
```

### Push Workout to Garmin

```bash
curl -X POST -H "X-API-Key: $TRANSITION_API_KEY" \
  "https://api.transition.fun/api/v1/workouts/123/push-garmin"
```

## Rate Limits

| Tier | Read Endpoints | AI Endpoints |
|------|---------------|-------------|
| Free | 100/day | 3/day |
| Paid | 10,000/day | 100/day |

**Read endpoints:** workouts, metrics, profile, history
**AI endpoints:** coach chat, adapt, generate

Rate limit errors return HTTP 429 with a message indicating which limit was exceeded.

## Tips for Agents

1. **Check fatigue before recommending hard workouts.** Call `GET /api/v1/performance/pmc` and look at TSB (Training Stress Balance). If TSB is below -20, the athlete is likely fatigued — suggest easier workouts or rest.

2. **Use adapt sparingly.** Plan adaptation regenerates the entire training plan using AI. Only trigger it when the athlete explicitly asks for changes or when there's a significant reason (injury, schedule change, race date change).

3. **Use the free WOD endpoint for casual users.** If someone just wants a quick workout without signing up, use `GET /api/v1/wod`. No API key needed.

4. **Workout generation is async.** After calling `POST /workouts/generate` or `POST /workouts/adapt`, poll `GET /workouts/status` until it returns ready, then fetch the workouts.

5. **Date format is always YYYY-MM-DD** for all date parameters.
