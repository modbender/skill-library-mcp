# API Reference

Full request/response documentation for all Haver API endpoints. All authenticated endpoints require `Authorization: Bearer hv_...` header.

## Registration

```http
POST {HAVER_API_URL}/api/register
Content-Type: application/json

{ "provider": "openclaw", "externalId": "<user's unique ID>" }
```

Response:
```json
{
  "user": { "id": "..." },
  "apiKey": "hv_...",
  "created": true
}
```

- **`apiKey`**: Always returned, even on re-register. Save immediately.
- **`created`**: `true` for new users, `false` for re-registration (key rotated, old key invalidated).

## User Profile

```http
GET {HAVER_API_URL}/api/me
Authorization: Bearer hv_...
```

Response: `{ "user": { "id": "...", "language": "en", "timezone": "America/New_York", ... } }`

## Logging Food

```http
POST {HAVER_API_URL}/api/me/nutrition/log
Authorization: Bearer hv_...
Content-Type: application/json

{ "text": "chicken salad with olive oil dressing and orange juice" }
```

Optional: include `"images": ["<base64 or URL>"]` for food photos.

Response:
```json
{
  "text": "Logged: Chicken salad with olive oil dressing (~450 cal)...",
  "foodLogged": true,
  "sideEffectMessages": ["🔥 3-day streak! +15 XP"]
}
```

- **`text`**: Human-readable summary with calorie/macro estimates
- **`foodLogged`**: Whether food was actually logged. Can be `false` if the AI couldn't parse the input as food.
- **`sideEffectMessages`**: XP awards, streaks, achievements. Always relay these to the user.

**Tips:** Be specific about portions ("2 scrambled eggs"), mention cooking methods ("grilled" vs "fried"), include drinks and snacks. Rough estimates are fine.

## Nutrition Summary

```http
GET {HAVER_API_URL}/api/me/nutrition/summary
Authorization: Bearer hv_...
```

Query params (all optional):
- `date=2026-02-19` -- specific date
- `from=2026-02-17&to=2026-02-19` -- date range

Response:
```json
{
  "text": "Today's intake: 1,450 cal (725 remaining)...",
  "date": "2026-02-21"
}
```

The `text` field is already well-formatted -- present it to the user directly.

## Nutrition Profile

```http
GET {HAVER_API_URL}/api/me/nutrition/profile
Authorization: Bearer hv_...
```

Response:
```json
{
  "userId": "...",
  "hasProfile": true,
  "profile": {
    "height": 180,
    "weight": 80,
    "age": 30,
    "sex": "male",
    "activityLevel": "moderately_active",
    "metrics": { "bmi": 24.7, "bmr": 1800, "tdee": 2790 },
    "nutritionGoals": {
      "goalType": "weight_loss",
      "targetWeightKg": 75,
      "weeklyGoalKg": 0.5,
      "dailyCalorieTarget": 2290
    }
  }
}
```

## Weight Tracking

### Log Weight
```http
POST {HAVER_API_URL}/api/me/weight
Authorization: Bearer hv_...
Content-Type: application/json

{ "weightKg": 79.5 }
```

**weightKg range:** 10-500.

Response includes `updatedWeight` and recalculated `metrics` (BMI, BMR, TDEE update with new weight).

### Weight History
```http
GET {HAVER_API_URL}/api/me/weight
Authorization: Bearer hv_...
```

Query params: `from`, `to` (YYYY-MM-DD), `limit` (number).

Response:
```json
{
  "userId": "...",
  "entries": [
    { "date": "2026-02-21", "weightKg": 79.5, "source": "api" },
    { "date": "2026-02-14", "weightKg": 80.0, "source": "api" }
  ]
}
```

## AI Coaching Chat

```http
POST {HAVER_API_URL}/api/me/chat
Authorization: Bearer hv_...
Content-Type: application/json

{ "text": "What are some high-protein breakfast ideas under 400 calories?" }
```

Optional: include `"images": ["<base64 or URL>"]` for context images.

Response:
```json
{
  "text": "Here are some great options...",
  "metadata": {
    "foodLogged": false,
    "profileUpdated": false,
    "nutritionSummaryGenerated": false,
    "sideEffectMessages": []
  }
}
```

- **`text`**: The AI coach's response
- **`metadata.foodLogged`**: The chat AI can detect and log food mentioned in conversation
- **`metadata.sideEffectMessages`**: Same as nutrition/log -- relay any messages to the user

## XP and Levels

```http
GET {HAVER_API_URL}/api/me/xp
Authorization: Bearer hv_...
```

Response:
```json
{
  "userId": "...",
  "state": {
    "totalXp": 450,
    "level": 3,
    "currentStreak": 5,
    "longestStreak": 12,
    "lastLogDate": "2026-02-21"
  },
  "levelInfo": {
    "currentLevel": 3,
    "currentXp": 450,
    "xpForCurrentLevel": 300,
    "xpForNextLevel": 600,
    "xpProgress": 150,
    "xpNeeded": 150,
    "progressPercentage": 50
  },
  "unclaimedEntries": [
    { "id": "...", "amount": 15, "source": "food_log", "eventDescription": "Logged food", "createdAt": "..." }
  ]
}
```

## Brain Snacks

```http
GET {HAVER_API_URL}/api/me/brain-snacks
Authorization: Bearer hv_...
```

Response:
```json
{
  "userId": "...",
  "totalCollected": 12,
  "totalAvailable": 50,
  "progressPercentage": 24,
  "categoryProgress": {
    "macronutrients": { "collected": 3, "available": 10, "percentage": 30 }
  }
}
```

Educational nutrition facts earned through engagement.

## Milestones

```http
GET {HAVER_API_URL}/api/me/milestones
Authorization: Bearer hv_...
```

Response:
```json
{
  "userId": "...",
  "milestones": [
    { "milestoneType": "first_food_log", "achievedAt": "2026-02-18T...", "createdAt": "..." }
  ]
}
```

## Memory

```http
GET {HAVER_API_URL}/api/me/memory
Authorization: Bearer hv_...
```

Response: `{ "userId": "...", "formattedMemory": "Prefers Mediterranean diet, dislikes raw tomatoes..." }`

What Haver remembers about the user from past conversations. Useful for personalizing coaching.

## Account Status

```http
GET {HAVER_API_URL}/api/me/status
Authorization: Bearer hv_...
```

Response (free user):
```json
{
  "userId": "...",
  "totalMessages": 23,
  "currentMonthMessages": 15,
  "subscription": {
    "tier": "free",
    "unlimited": false
  },
  "remainingTrialMessages": 35
}
```

Response (premium user):
```json
{
  "userId": "...",
  "totalMessages": 142,
  "currentMonthMessages": 37,
  "subscription": {
    "tier": "premium",
    "endDate": "2026-03-15T00:00:00.000Z",
    "unlimited": true
  },
  "remainingTrialMessages": null
}
```

## Subscription & Usage Limits

```http
GET {HAVER_API_URL}/api/me/subscription
Authorization: Bearer hv_...
```

Response (free user):
```json
{
  "userId": "...",
  "subscription": {
    "tier": "free",
    "unlimited": false
  },
  "dailyUsage": {
    "foodLogs": { "used": 3, "limit": 10, "remaining": 7 },
    "chat": { "used": 1, "limit": 3, "remaining": 2 },
    "images": { "used": 0, "limit": 2, "remaining": 2 }
  },
  "monthlyUsage": {
    "messagesUsed": 15,
    "limit": 50,
    "remaining": 35
  }
}
```

Response (premium user):
```json
{
  "userId": "...",
  "subscription": {
    "tier": "premium",
    "endDate": "2026-03-15T00:00:00.000Z",
    "unlimited": true
  },
  "dailyUsage": null,
  "monthlyUsage": null
}
```

Check `subscription.unlimited` -- if `true`, limits don't apply. Each usage limit has `used`, `limit`, and `remaining` so the agent doesn't need to do math.

## Settings

```http
PATCH {HAVER_API_URL}/api/me/settings
Authorization: Bearer hv_...
Content-Type: application/json

{ "language": "en", "timezone": "Europe/London" }
```

At least one field required. Response: `{ "user": { ... } }`.

## Connect Code

```http
POST {HAVER_API_URL}/api/me/connect-code
Authorization: Bearer hv_...
```

Response: `{ "code": "ABC123", "expiresAt": "2026-02-21T01:15:00Z" }`

Tell user: open Telegram, search **@haver_sheli_bot**, send `/connect ABC123`. Once connected, they can subscribe for premium access.

## Error Responses

### 400 -- Validation Error
```json
{
  "error": "Validation Error",
  "message": "Request validation failed",
  "statusCode": 400,
  "details": { "fields": [{ "path": "weightKg", "message": "Number must be >= 10" }] }
}
```
Tell the user what's wrong in plain language: "The weight needs to be at least 10 kg. Did you mean to enter it in kg?"

### 401 -- Unauthorized
API key is invalid or missing. Re-register to get a fresh key.

### 404 -- Not Found
User not found for the given key. Register first.

### 429 -- Rate Limited
```json
{
  "error": "LimitExceeded",
  "message": "Daily nutrition log limit reached",
  "statusCode": 429,
  "details": {
    "limitType": "daily_nutrition_log",
    "limit": 10,
    "used": 10,
    "resetsAt": "2026-02-22T00:00:00Z",
    "upgradeInstructions": "Connect your Telegram account and subscribe for unlimited access"
  }
}
```

1. Tell the user which limit was hit and when it resets
2. Offer to upgrade via Telegram connection
3. If they decline, help with what's still available

### 500 -- Server Error
Backend error (often LLM timeout). Tell the user to try again in a moment. Retry once after a brief pause.
