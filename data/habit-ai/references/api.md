# Habit AI API Reference

Base URL: `https://habitapp.ai/api/v1`
Auth: `Authorization: Bearer hab_...`

## Table of Contents

- [Profile](#profile)
- [Meals](#meals)
- [Nutrition](#nutrition)
- [Water](#water)
- [Steps](#steps)
- [Weight](#weight)
- [Meditation](#meditation)
- [Journal](#journal)
- [Saved Meals](#saved-meals)
- [AI Analysis](#ai-analysis)
- [AI Coaches](#ai-coaches)
- [API Keys](#api-keys)

## Profile

### GET /profile

Returns user profile with nutrition goals.

Response fields: `displayName`, `timezone`, `heightInCm`, `weightInKg`, `gender`, `birthDate`, `caloriesGoal`, `proteinGoal`, `carbsGoal`, `fatGoal`, `fiberGoal`, `sugarGoal`, `sodiumGoal`, `weightGoal`, `desiredWeightInKg`, `diet`, `activityLevel`, `obstacles`, `foodSensitivities`

### PUT /profile

Update profile fields. Body: any subset of the fields above.

## Meals

### GET /meals

Query params: `date` (YYYY-MM-DD), `limit` (default 20, max 100), `offset`

Returns: `{meals: [...], count}`

### POST /meals

Required: `calories` (number)

Optional: `mealName` (string — display name, e.g. "Croissant and Orange Juice"), `protein`, `carbs`, `fat`, `fiber`, `sodium`, `sugar` (numbers), `ingredients` (array of objects), `mealType` (breakfast|lunch|dinner|snack), `healthScore` (1-10), `imageUrl`, `analysisConfidenceLevel` (1-10), `dateScanned` (ISO string)

Alias: `name` is also accepted for `mealName`.

Returns: `{meal: {...}}` with 201 status

### GET /meals/:id

Returns single meal.

### PUT /meals/:id

Update meal fields: `mealName`, `calories`, `protein`, `carbs`, `fat`, `fiber`, `sodium`, `sugar`, `ingredients`, `mealType`, `healthScore`, `imageUrl`, `analysisConfidenceLevel`.

### DELETE /meals/:id

Delete a meal.

## Nutrition

### GET /nutrition/daily

Query: `date` (YYYY-MM-DD, default today)

Returns: `{daily: {totalCalories, totalProtein, totalCarbs, totalFat, totalFiber, totalSodium, totalSugar, waterIntake, stepsCount, mealLog}}`

### GET /nutrition/weekly

Query: `date` (YYYY-MM-DD, end of 7-day window, default today)

Returns: `{weekly: {startDate, endDate, totals: {totalCalories, totalProtein, totalCarbs, totalFat, totalFiber, totalSodium, totalSugar, totalWaterIntake, daysTracked}, dailyBreakdown: [...]}}`

## Water

### POST /water

Required: `amount` (number, milliliters)
Optional: `date` (ISO string), `timezone`

Increments water intake for the day.

## Steps

### GET /steps

Query: `days` (default 7, max 90)

### POST /steps

Required: `steps` (number)
Optional: `date` (ISO string)

Auto-calculates `caloriesBurned` if profile has height/weight/gender. Upserts (one entry per day).

## Weight

### GET /weight

Query: `days` (default 30, max 365)

### POST /weight

Required: `weightInKg` (number)
Optional: `date` (ISO string)

Upserts per day. Also updates profile `weightInKg`.

### DELETE /weight/:id

## Meditation

### GET /meditation

Query: `limit` (default 20, max 100), `offset`

### POST /meditation

Required: `durationInMinutes` (number)
Optional: `type`, `notes`

### DELETE /meditation/:id

## Journal

### GET /journal

Query: `limit` (default 20, max 100), `offset`

### POST /journal

Required: `content` (string)
Optional: `topic`, `mood`

### DELETE /journal/:id

## Saved Meals

### GET /saved-meals

Query: `limit` (default 20, max 100), `offset`

### POST /saved-meals

Required: `name` (string)
Optional: `calories`, `protein`, `carbs`, `fat`, `fiber`, `sodium`, `sugar`, `ingredients`, `mealType`, `imageUrl`

### DELETE /saved-meals/:id

## AI Analysis

### POST /analyze/food-image

Required: `imageBase64` (base64 string, with or without data: prefix)
Optional: `mealType`

Returns: `{analysis: {name, calories, protein, carbs, fat, fiber, sodium, sugar, healthScore, mealType, analysisConfidenceLevel, ingredients: [{name, amount, unit, calories, protein, carbs, fat}]}}`

### POST /analyze/meal-description

Required: `description` (string)
Optional: `mealType`

Returns same schema as food-image analysis.

## AI Coaches

All coach endpoints accept:
- Required: `message` (string)
- Optional: `conversationHistory` (array of `{role: "user"|"assistant", content}`)

### POST /coaches/eating

Nutrition coaching with access to user's meal history, goals, and patterns.

### POST /coaches/mindfulness

Mindfulness and stress management guidance.

### POST /coaches/meditation

Meditation coaching with access to recent session history.

## API Keys

### POST /keys

Create a new API key. Body: `{name}` (optional). Max 5 active keys.
Returns: `{apiKey: "hab_...", name, prefix}` — **store securely, shown only once**.

### GET /keys

List active keys (prefix only, not full key).

### DELETE /keys/:id

Revoke an API key.
