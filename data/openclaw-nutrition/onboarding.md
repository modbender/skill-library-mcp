# Onboarding Guide

Full step-by-step onboarding flow for new Haver users. Guide the user conversationally -- ask one step at a time, don't dump all questions at once.

## Check Status

```http
GET {HAVER_API_URL}/api/me/onboarding/status
Authorization: Bearer hv_...
```

Response: `{ "userId": "...", "completed": false, "steps": { "language": false, "timezone": false, "profile": false, "goals": false } }`

Use this to see which steps are done. If a user abandoned onboarding previously, resume from the first incomplete step.

## Step 1: Language

```http
POST {HAVER_API_URL}/api/me/onboarding/language
Authorization: Bearer hv_...
Content-Type: application/json

{ "language": "en" }
```

ISO 639-1 codes. Common: `"en"` (English), `"uk"` (Ukrainian).

**You already know the user's language** -- OpenClaw provides it. Set this automatically without asking. Don't prompt the user for language selection.

## Step 2: Timezone

```http
POST {HAVER_API_URL}/api/me/onboarding/timezone
Authorization: Bearer hv_...
Content-Type: application/json

{ "timezone": "America/New_York" }
```

IANA timezone names (e.g. `"Europe/London"`, `"Asia/Tokyo"`).

## Step 3: Physical Profile

Collect conversationally -- sex, age, height, weight, activity level.

```http
POST {HAVER_API_URL}/api/me/onboarding/profile
Authorization: Bearer hv_...
Content-Type: application/json

{
  "sex": "male",
  "age": 30,
  "heightCm": 180,
  "weightKg": 80,
  "activityLevel": "moderately_active"
}
```

**Validation ranges:** age 1-150, heightCm 30-300, weightKg 10-500.

**Activity levels:**
- `sedentary` -- desk job, little exercise
- `lightly_active` -- light exercise 1-3 days/week
- `moderately_active` -- moderate exercise 3-5 days/week
- `very_active` -- hard exercise 6-7 days/week
- `extremely_active` -- athlete or physical job

The response includes calculated metrics (BMI, BMR, TDEE). Share these with the user!

## Step 4: Goals

```http
POST {HAVER_API_URL}/api/me/onboarding/goals
Authorization: Bearer hv_...
Content-Type: application/json

{ "goalType": "weight_loss", "targetWeightKg": 75, "weeklyGoalKg": 0.5 }
```

**Goal types:** `weight_loss`, `weight_gain`, `weight_maintenance`.
**weeklyGoalKg:** 0.1-2.0 (0.25-1.0 is typical and sustainable).

**Dependency:** Profile MUST be set before goals (the calorie target calculation needs BMR/TDEE).

The response includes `dailyCalorieTarget`. Share it!

## Step 5: Complete

```http
POST {HAVER_API_URL}/api/me/onboarding/complete
Authorization: Bearer hv_...
```

**Prerequisites:** Language, timezone, AND profile must be set. Goals are recommended but the system requires profile at minimum.

Tell the user they're all set. Explain what they can do: log food, chat with you (the AI coach), track weight, and check progress.

## Dependencies

```
language ──┐
timezone ──┤
            ├──> complete
profile ───┤
  └──> goals ─┘
```

- Profile must be set before goals
- Language, timezone, and profile are required before complete
- Goals are recommended but not strictly required
- Steps can be done in any order as long as dependencies are met

## Partial Onboarding

If a user abandons onboarding mid-way, their progress is saved. On return:
1. Call `GET {HAVER_API_URL}/api/me/onboarding/status`
2. Check which `steps` are `false`
3. Resume from the first incomplete step
4. Don't re-ask completed steps
