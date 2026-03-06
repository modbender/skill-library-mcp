---
name: opencal
description: Log meals, check nutrition progress, and manage calorie goals in the OpenCal app — hands-free via your AI agent. Use when the user mentions eating, food, calories, macros, or nutrition.
homepage: https://opencal.ai
metadata: {"openclaw":{"emoji":"🥗","requires":{"bins":["curl","jq"],"env":["OPENCAL_API_KEY"]},"primaryEnv":"OPENCAL_API_KEY"}}
---

# OpenCal

OpenCal is a calorie & nutrition tracker with a beautiful iOS app. This skill lets your AI agent log meals, check progress, and update goals — so the user never has to open the app to track what they eat.

"I just had a burrito for lunch" → agent searches, scales, logs it → it shows up in the app instantly.

## Setup

1. Download OpenCal from the App Store
2. Sign in and set your calorie/macro goals
3. Go to Profile → API Keys → Generate
4. Set the key:
   ```bash
   export OPENCAL_API_KEY="sk_your-key-here"
   ```

## When to use this skill

| User says | What to do |
| --- | --- |
| "I had a chicken sandwich for lunch" | Search food → scale nutrition → log it |
| "What did I eat today?" | Fetch today's log and summarize |
| "How much protein do I have left?" | Fetch log totals and compare to goals |
| "I want to cut to 1800 calories" | Update their calorie goal |
| "That last entry was wrong, remove it" | Delete the log entry |
| "What's in a banana?" | Search and show nutrition info (don't log) |

## Log a meal

The most common flow. User says something like "I had 200g chicken breast for lunch":

**1. Search for the food:**
```bash
curl -s "${OPENCAL_BASE_URL:-https://api.opencal.ai}/api/v1/food/search?q=chicken+breast&limit=5" \
  -H "Authorization: Bearer $OPENCAL_API_KEY" | jq '.results[] | {name, calories, protein, carbs, fat}'
```

Results are **per 100g**. Pick the best match.

**2. Scale to the actual amount and log:**
```bash
curl -s -X POST "${OPENCAL_BASE_URL:-https://api.opencal.ai}/api/v1/food/log" \
  -H "Authorization: Bearer $OPENCAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Chicken Breast",
    "amount": 200, "unit": "g",
    "calories": 330, "protein": 62, "carbs": 0, "fat": 7.2,
    "mealType": "lunch"
  }'
```

Multiply all nutrition values by `amount / 100`. The entry appears in the app immediately.

Use `mealType`: `breakfast`, `lunch`, `dinner`, or `snack`.
Add `"loggedAt": "2026-02-18T12:00:00Z"` to backfill a past meal (defaults to now).

**3. Confirm with the user:** "Logged 200g chicken breast for lunch — 330 kcal, 62g protein."

## Check daily progress

```bash
curl -s "${OPENCAL_BASE_URL:-https://api.opencal.ai}/api/v1/food/log?date=2026-02-18" \
  -H "Authorization: Bearer $OPENCAL_API_KEY" | jq '{totals, entries: [.entries[] | {name, calories, mealType}]}'
```

Omit `?date=` for today. Returns each entry plus totals (calories, protein, carbs, fat).

## Check and update goals

```bash
# Current goals
curl -s "${OPENCAL_BASE_URL:-https://api.opencal.ai}/api/v1/goals" \
  -H "Authorization: Bearer $OPENCAL_API_KEY" | jq

# Update (only include fields to change)
curl -s -X PUT "${OPENCAL_BASE_URL:-https://api.opencal.ai}/api/v1/goals" \
  -H "Authorization: Bearer $OPENCAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"calorieGoal": 1800, "proteinGrams": 160}'
```

## Delete a log entry

Get the entry ID from the daily log, then:

```bash
curl -s -X DELETE "${OPENCAL_BASE_URL:-https://api.opencal.ai}/api/v1/food/log/{id}" \
  -H "Authorization: Bearer $OPENCAL_API_KEY"
```

## Important notes

- Search results are **per 100g** — always scale before logging
- If the user doesn't mention an amount, ask — don't guess
- If search returns nothing, try shorter/simpler terms (e.g. "rice" instead of "steamed jasmine rice")
- Always confirm what you logged so the user can correct mistakes
- Rate limit: 100 requests/min
