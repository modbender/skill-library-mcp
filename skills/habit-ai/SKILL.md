---
name: habit-ai
description: Track nutrition, meals, water, weight, steps, meditation, and journal entries via the Habit AI API. Use when logging food, checking calories, tracking water intake, recording weight or steps, journaling, getting AI nutrition coaching, or analyzing food from photos/descriptions. Requires a Habit AI account and API key (hab_*).
---

# Habit AI

Track health and nutrition through the Habit AI REST API.

## Setup

1. Create account at https://habitapp.ai (or iOS app)
2. Go to Settings → API Keys → Create Key
3. Store key in environment: `export HABITAI_API_KEY="hab_..."`

All requests use:
- Base URL: `https://habitapp.ai/api/v1`
- Auth header: `Authorization: Bearer $HABITAI_API_KEY`
- Content-Type: `application/json`

## Quick Reference

| Action | Method | Endpoint |
|--------|--------|----------|
| Log a meal | POST | `/meals` |
| Today's meals | GET | `/meals?date=YYYY-MM-DD` |
| Daily nutrition | GET | `/nutrition/daily?date=YYYY-MM-DD` |
| Weekly nutrition | GET | `/nutrition/weekly?date=YYYY-MM-DD` |
| Log water (ml) | POST | `/water` |
| Log weight (kg) | POST | `/weight` |
| Log steps | POST | `/steps` |
| Log meditation | POST | `/meditation` |
| Journal entry | POST | `/journal` |
| AI eating coach | POST | `/coaches/eating` |
| AI mindfulness coach | POST | `/coaches/mindfulness` |
| AI meditation coach | POST | `/coaches/meditation` |
| Get profile | GET | `/profile` |
| Update profile | PUT | `/profile` |

For full endpoint details (request/response schemas, all parameters), see [references/api.md](references/api.md).

## Logging Meals — The Right Way

### ⚠️ CRITICAL: Use the AI model to analyze food, then POST /meals with the EXACT structure below

Do NOT call `/analyze/food-image` or `/analyze/meal-description` — instead, use your own vision/language capabilities to analyze the food, then construct the exact JSON structure below and POST it to `/meals`.

### Step 0: Check user profile for allergens/diet

Before analyzing, call `GET /profile` to check `foodSensitivities` and `diet` fields. Factor these into:
- **healthScore** — lower the score if the meal contains ingredients the user is sensitive to
- **healthScoreExplanation** — mention the general nutritional pros/cons
- **healthSensitivityExplanation** — if the meal contains any of the user's allergens/sensitivities, explain which ingredients are problematic and why. Leave empty string if no sensitivities match.

### Step 1: Analyze the food yourself

For **photos**: Look at the image and identify each ingredient, estimate portions, and calculate nutrition using USDA data.

For **descriptions**: Parse the meal description and calculate nutrition the same way.

### Step 2: POST /meals with the EXACT structure

Every field matters. iOS reads from `nutritionalSummary` (nested object) — if it's missing, meals show as 0 calories.

```json
{
  "mealName": "Grilled Chicken Salad with Ranch",
  "calories": 520,
  "protein": 42,
  "carbs": 18,
  "fat": 32,
  "fiber": 4,
  "sodium": 890,
  "sugar": 6,
  "healthScore": 7,
  "healthScoreExplanation": "Lean protein from grilled chicken and fiber from greens, but ranch dressing adds significant fat and sodium.",
  "mealType": "lunch",
  "analysisConfidenceLevel": 8,
  "ingredients": [
    {
      "name": "grilled chicken breast",
      "calories": 280,
      "protein": 35,
      "carbs": 0,
      "fat": 14,
      "sugar": 0,
      "fiber": 0,
      "sodium": 400,
      "healthScore": 8,
      "measurementType": "grams",
      "measurementValue": 200
    },
    {
      "name": "mixed salad greens",
      "calories": 20,
      "protein": 2,
      "carbs": 4,
      "fat": 0,
      "sugar": 1,
      "fiber": 2,
      "sodium": 30,
      "healthScore": 9,
      "measurementType": "cups",
      "measurementValue": 2
    },
    {
      "name": "ranch dressing",
      "calories": 220,
      "protein": 5,
      "carbs": 14,
      "fat": 18,
      "sugar": 5,
      "fiber": 2,
      "sodium": 460,
      "healthScore": 3,
      "measurementType": "spoons",
      "measurementValue": 3
    }
  ]
}
```

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mealName` | string | **Yes** | Display name (e.g. "Chicken Caesar Salad"). Without this, the meal has no name in the app. |
| `calories` | number | **Yes** | Total calories (kcal). Must be > 0. |
| `protein` | number | Yes | Total protein in grams |
| `carbs` | number | Yes | Total carbohydrates in grams |
| `fat` | number | Yes | Total fat in grams |
| `fiber` | number | Yes | Total fiber in grams |
| `sodium` | number | Yes | Total sodium in milligrams |
| `sugar` | number | Yes | Total sugar in grams |
| `healthScore` | integer | Yes | 1-10. How healthy is this meal overall? (1=very unhealthy, 10=very healthy) |
| `mealType` | string | Yes | One of: `breakfast`, `lunch`, `dinner`, `snack` |
| `analysisConfidenceLevel` | integer | Yes | 1-10. How confident are you in the nutrition estimates? (1=wild guess, 10=exact data from packaging). For photo analysis use 6-8, for descriptions use 5-7. |
| `healthScoreExplanation` | string | Yes | 1-2 sentence explanation of the nutritional pros/cons (e.g. "Good protein from chicken but high sodium from the sausage and dressing.") |
| `healthSensitivityExplanation` | string | Yes | If the meal contains any of the user's allergens/food sensitivities (from profile), explain which ingredients are problematic. Empty string `""` if no sensitivities match or user has none set. |
| `ingredients` | array | Yes | Array of ingredient objects (see below) |
| `imageUrl` | string | No | URL of the food photo. Get this from `POST /meals/upload-image` first (see below). |
| `dateScanned` | string | No | ISO 8601 timestamp. Defaults to now if omitted. |
| `serving` | number | No | Serving multiplier (defaults to 1.0) |

### Ingredient Object

Each ingredient in the `ingredients` array must have:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Ingredient name (e.g. "grilled chicken breast") |
| `calories` | number | Calories for this ingredient's portion (kcal) |
| `protein` | number | Protein in grams |
| `carbs` | number | Carbs in grams |
| `fat` | number | Fat in grams |
| `sugar` | number | Sugar in grams |
| `fiber` | number | Fiber in grams |
| `sodium` | number | Sodium in milligrams |
| `healthScore` | integer | 1-10 health score for this specific ingredient |
| `measurementType` | string | **Must be one of:** `grams`, `ounces`, `cups`, `spoons`, `servings`. Use `servings` for pieces/slices/bowls/items. Use `spoons` for tablespoons/teaspoons. |
| `measurementValue` | number | Amount in the specified unit |

### Important Rules

1. **All nutrition values must be numbers, not strings.** `"calories": 520` not `"calories": "520"`
2. **Ingredient calories should sum to the total calories** (approximately — within 5%)
3. **`mealName` is mandatory** — without it, the meal is invisible on iOS
4. **`healthScore` is 1-10 integer** — use your judgment (fast food = 2-4, home-cooked balanced = 6-8, raw salad = 9-10)
5. **`analysisConfidenceLevel` is 1-10 integer** — be honest about uncertainty
6. **Sodium is in milligrams**, everything else is in grams (except calories in kcal)

### Uploading a meal photo (thumbnail)

If you have a food photo, upload it first to get a URL:

```bash
curl -X POST https://habitapp.ai/api/v1/meals/upload-image \
  -H "Authorization: Bearer $HABITAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"imageBase64": "<base64-encoded-image>"}'
```

Returns: `{"success": true, "imageUrl": "https://firebasestorage.googleapis.com/..."}`

Then pass `imageUrl` in your POST /meals call. You can also attach to an existing meal:

```json
{"imageBase64": "<base64>", "mealId": "<existing-meal-id>"}
```

**Full flow with photo:**
1. `POST /meals/upload-image` with base64 photo → get `imageUrl`
2. `POST /meals` with nutrition data + `imageUrl`

## Other Workflows

### Check remaining calories

1. GET `/nutrition/daily` for today's totals
2. GET `/profile` for calorie goal
3. Subtract: `caloriesGoal - totalCalories`

### Quick water log

```bash
curl -X POST https://habitapp.ai/api/v1/water \
  -H "Authorization: Bearer $HABITAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"amount": 500}'
```

Amount is in milliliters. 1 cup ≈ 237ml, 1 glass ≈ 250ml.

## Notes

- Dates default to today if omitted (uses user's timezone from profile)
- Water amount is in **milliliters**
- Weight is in **kilograms** (1 lb ≈ 0.4536 kg)
- Steps auto-calculate calories burned if profile has height/weight/gender
- Max 5 API keys per account
