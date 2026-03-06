---
name: fitbit
description: Fitbit fitness data integration. Use when the user wants fitness insights, workout summaries, step counts, heart rate data, sleep analysis, or to ask questions about their Fitbit activity data. Provides AI-powered analysis of fitness metrics.
---

# Fitbit Fitness Insights

Get AI-powered insights from your Fitbit data. Query your fitness metrics, analyze trends, and ask questions about your activity.

## Features

- 📊 Daily activity summaries (steps, calories, distance, active minutes)
- 💓 Heart rate data and zones
- 😴 Sleep tracking and analysis
- 🏃 Workout/activity logs
- 📈 Weekly and trend analysis
- 🤖 AI-powered insights and Q&A

## Prerequisites

**Requires:** Fitbit OAuth access token

Setup steps in `references/fitbit-oauth-setup.md`

## Commands

### Get Profile
```bash
FITBIT_ACCESS_TOKEN="..." python3 scripts/fitbit_api.py profile
```

### Daily Activity
```bash
python3 scripts/fitbit_api.py daily [date]
# Examples:
python3 scripts/fitbit_api.py daily              # Today
python3 scripts/fitbit_api.py daily 2026-02-08   # Specific date
```

Returns: steps, distance, calories, active minutes (very/fairly/lightly/sedentary), floors

### Steps Range
```bash
python3 scripts/fitbit_api.py steps <start_date> <end_date>
```

Example:
```bash
python3 scripts/fitbit_api.py steps 2026-02-01 2026-02-07
```

Returns: total steps, average steps, daily breakdown

### Heart Rate
```bash
python3 scripts/fitbit_api.py heart [date]
```

Returns: resting heart rate, heart rate zones with minutes in each zone

### Sleep Data
```bash
python3 scripts/fitbit_api.py sleep [date]
```

Returns: duration, efficiency, start/end times, sleep stages

### Logged Activities
```bash
python3 scripts/fitbit_api.py activities [date]
```

Returns: workouts/activities logged (name, duration, calories, distance)

### Weekly Summary
```bash
python3 scripts/fitbit_api.py weekly
```

Returns: 7-day summary of steps and key metrics

## AI Insights Usage

When user asks fitness questions, use the API to fetch relevant data, then provide insights:

**Example queries:**
- "How did I sleep last night?" → fetch sleep data, analyze quality
- "Did I hit my step goal this week?" → fetch weekly summary, compare to goals
- "What was my average heart rate during workouts?" → fetch heart + activities, analyze
- "Am I more active on weekdays or weekends?" → fetch range data, compare patterns

**Analysis approach:**
1. Identify what data is needed
2. Fetch via appropriate API command
3. Analyze the data
4. Provide insights in conversational format

## Example Responses

**User:** "How did I do this week?"

**Agent:**
1. Fetch weekly summary
2. Fetch recent sleep data
3. Respond: "You had a solid week! Averaged 8,234 steps/day (up 12% from last week). Hit your 10k step goal 4 out of 7 days. Sleep averaged 7.2 hours with 85% efficiency. CrossFit sessions on Mon/Wed/Fri looking consistent!"

**User:** "Did I exercise today?"

**Agent:**
1. Fetch daily activities
2. Fetch daily activity summary (active minutes)
3. Respond: "Yes! You logged a CrossFit session this morning (45 min, 312 calories). Plus 28 very active minutes total for the day."

## Data Insights to Look For

- **Trends:** Week-over-week changes, consistency patterns
- **Goals:** Compare to 10k steps, exercise frequency, sleep targets
- **Correlations:** Sleep quality vs activity, rest days vs performance
- **Anomalies:** Unusual spikes or drops
- **Achievements:** Personal bests, streaks, milestones

## Token Management

The skill automatically loads tokens from `/root/clawd/fitbit-config.json` and refreshes them when expired (every 8 hours).

**Auto-refresh:** Tokens are refreshed automatically - no manual intervention needed!

**Manual refresh (if needed):**
```bash
python3 scripts/refresh_token.py force
```

**Override with environment variable:**
```bash
export FITBIT_ACCESS_TOKEN="manual_token"
```

## Error Handling

- **Missing token:** Prompt user to set FITBIT_ACCESS_TOKEN
- **API errors:** Check token validity, may need refresh
- **No data:** Some days may have no logged activities or missing metrics

See `references/fitbit-oauth-setup.md` for token management.
