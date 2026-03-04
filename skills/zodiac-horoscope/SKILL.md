---
name: zodiac-horoscope
description: >
  Fetch personalized daily horoscope forecasts from zodiac-today.com API based on natal chart calculations.
  Use when a user wants: (1) daily guidance on what activities to pursue or avoid,
  (2) life planning help — best days for interviews, travel, romance, important decisions,
  (3) energy/focus/luck/romance forecasts to optimize their schedule,
  (4) lucky colors and numbers for the day,
  (5) future date analysis for planning events, trips, or milestones (paid tiers).
  Triggers: horoscope, zodiac, star sign forecast, daily guidance, lucky day, best day to, astrology advice,
  what should I do today, is today a good day for, plan my week astrology.
  Required env: ZODIAC_API_KEY (hsk_ API key), ZODIAC_PROFILE_ID (birth chart profile ID).
  Collects sensitive PII (email, birth date, birth city) for natal chart — requires user consent.
---

# Zodiac Horoscope

Provide personalized, actionable daily guidance powered by planetary transit calculations against the user's natal chart.

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `ZODIAC_API_KEY` | API key from zodiac-today.com (starts with `hsk_`) |
| `ZODIAC_PROFILE_ID` | Profile ID for the user's birth chart |

## Privacy Notice

This skill collects **sensitive PII** (email, birth date, birth city) required for natal chart calculations. Handle with care:
- Ask for explicit user consent before collecting birth information
- Never log or expose PII in public channels or shared contexts
- Store API keys and profile IDs in environment variables, not in plain text files
- Delete `cookies.txt` after registration is complete

## How This Helps People

- **Daily decision-making**: "Should I have that difficult conversation today?" → Check if confrontations are favorable or unfavorable
- **Schedule optimization**: Plan high-energy tasks on high-energy days, rest on low days
- **Life event planning**: Find the best window for job interviews, first dates, travel, or big purchases (paid tiers unlock future dates)
- **Relationship insights**: Romance metrics help users pick ideal date nights
- **Motivation & mindfulness**: Daily summaries provide a moment of reflection and intentional living

## Setup

Everything can be done via API — no browser needed.

### 1. Register & get API key

```bash
# Send verification code (creates account if new)
curl -s -X POST https://zodiac-today.com/api/auth/send-code \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'

# Verify code (check email inbox for 6-digit code)
curl -s -X POST https://zodiac-today.com/api/auth/verify \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email":"user@example.com","code":"123456"}'

# Create API key (use session cookie from verify step)
curl -s -X POST https://zodiac-today.com/api/keys \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"name":"My Agent"}'
# Response: {"id":"...","key":"hsk_...","name":"My Agent"}
```

Store the `hsk_` key as environment variable `ZODIAC_API_KEY`. Delete `cookies.txt` after this step.

### 2. Create birth profile

```bash
curl -s -X POST https://zodiac-today.com/api/profiles \
  -H "Authorization: Bearer hsk_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"name":"John","birthDate":"1990-05-15","birthCity":"London, UK"}'
```

Save the returned `id` as environment variable `ZODIAC_PROFILE_ID`.

## Workflow

### First-time setup for a user
1. Ask for their email, birth date, and birth city (get explicit consent — this is sensitive PII)
2. Send verification code: `POST /api/auth/send-code` with their email
3. **Human-in-the-loop**: Ask the user to check their email and provide the 6-digit code. If the agent has email access (e.g., IMAP), it may retrieve the code automatically from `noreply@zodiac-today.com`
4. Verify code: `POST /api/auth/verify` — save session cookie to a temp file (`-c cookies.txt`)
5. Create API key: `POST /api/keys` (with session cookie) — save the returned `hsk_` key
6. **Clean up**: Delete `cookies.txt` immediately — it is no longer needed
7. Create profile: `POST /api/profiles` (with API key) — save the returned profile `id`
8. Store `ZODIAC_API_KEY` and `ZODIAC_PROFILE_ID` as environment variables

### Daily horoscope fetch
1. Call `GET /api/horoscope/daily?profileId=$ZODIAC_PROFILE_ID&startDate=YYYY-MM-DD&endDate=YYYY-MM-DD` with `Authorization: Bearer $ZODIAC_API_KEY`
2. Parse the response and present actionable insights

### Presenting results to users

Translate raw data into **practical advice**:

- **overallRating** (1-10): Frame as "Great day!" (8+), "Solid day" (6-8), "Take it easy" (<6)
- **favorable/unfavorable**: Present as "Good for:" and "Better to avoid:" lists
- **metrics**: Highlight the standout ones — "Your energy is HIGH today, perfect for tackling that project"
- **luckyColors**: Suggest outfit or decor choices
- **luckyNumbers**: Mention casually, fun touch
- **summary**: Use the astrological narrative to add color, but keep advice grounded and practical

### Planning ahead (paid tiers)

For users with Starter+ tiers, fetch date ranges to help:
- "What's the best day this month for my job interview?"
- "When should I plan our anniversary dinner?"
- Compare overallRating across dates and recommend the highest-rated windows

## API Details

See [references/api.md](references/api.md) for full endpoint docs, parameters, tiers, and response schemas.

## Example curl

```bash
curl "https://zodiac-today.com/api/horoscope/daily?profileId=PROFILE_ID&startDate=2026-02-15&endDate=2026-02-15" \
  -H "Authorization: Bearer hsk_your_api_key"
```
