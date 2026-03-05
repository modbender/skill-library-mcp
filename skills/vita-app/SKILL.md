---
name: vita
description: Access the user's personal health data from VITA, their longevity platform. Use this when the user asks about their health, how they're feeling today, sleep, recovery, HRV, supplements, protocols, or wants a daily health briefing. Returns today's AI insight, wearable metrics (Oura/WHOOP), and active supplement stack.
---

Use this skill to access VITA health data on behalf of the user.

## Setup

Generate an API key in VITA at **Settings → API Keys → New Key**.

Then set in `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "vita": {
        "enabled": true,
        "env": {
          "VITA_API_KEY": "vita_<your key>",
          "VITA_API_URL": "https://app.vitadao.com/api/vita-api"
        }
      }
    }
  }
}
```

## Calling the API

```bash
curl "$VITA_API_URL?action=<action>" \
  -H "Authorization: Bearer $VITA_API_KEY"
```

## Actions

| Action | Returns |
|---|---|
| `get_daily_insight` | Today's AI-generated summary, outlook (positive/neutral/caution), sleep & training summaries, protocol adherence, recommendations |
| `get_todays_outlook` | Live wearable metrics for today: sleep score, recovery/readiness, HRV, strain from Oura + WHOOP |
| `get_protocols` | Active supplement protocols with compound, dosage, unit, timing, frequency |

## Usage guidance

- Start every health check with `get_daily_insight` — it gives the full picture for today
- Add `get_todays_outlook` for raw wearable numbers (HRV, sleep score, recovery %)
- Add `get_protocols` when the user asks about supplements or what to take
- Call all 3 in parallel for a complete daily briefing
- Interpret data yourself — do not ask the user to explain their metrics
- If you get a 401, the key may have been deleted — ask the user to generate a new one in VITA Settings
