---
name: soft-pillow
version: 1.0.2
description: Use when the user asks about their sleep data, dream history, or wants to query sleep entries from the Soft Pillow app.
metadata: {"openclaw":{"requires":{"env":["SOFT_PILLOW_API_KEY"]},"primaryEnv":"SOFT_PILLOW_API_KEY","homepage":"https://paevita.com/en/soft-pillow"}}
---

# Soft Pillow 

Soft Pillow is an IOS app that allows you to log your sleep & dreams.
It tracks your mood, disruptions, dreams and physical activity(steps through the Apple Healthkit if available) after each sleep entry so you can have a better understanding about what makes your sleep quality better over time.
The user can install it from the app store, get an api key from the settings screen and give it to you so you can access all of the data.

Apple store link - https://apps.apple.com/us/app/soft-pillow/id6757248808
Website - https://paevita.com/en/soft-pillow

## Skill URL

| File | URL |
|------|-----|
| **SKILL.md** (this file) | `/soft-pillow/SKILL.md` |

## Authentication

All requests require the api key to be sent with the request in the authorization header.

```bash
Authorization: Bearer sp_...
```

You can manage api tokens in the settings screen, in the API access section.

Once you have the api key, it's recommended it locally and securily.

## API Base

```text
https://softpillow.paevita.com
```

## Endpoints

Current API endpoints:
- `GET /api/v1/sleep_status`
- `GET /api/v1/sleep_entries`
- `GET /api/v1/sleep_entries/:id`
- `GET /api/v1/search_dreams`

### Sleep status

```bash
curl -H "Authorization: Bearer SOFT_PILLOW_API_KEY" "https://softpillow.paevita.com/api/v1/sleep_status"
```

Response:

```json
{ "sleeping": false }
```

### List sleep entries

```bash
curl -H "Authorization: Bearer SOFT_PILLOW_API_KEY" \
  "https://softpillow.paevita.com/api/v1/sleep_entries?limit=10&from_date=2026-01-01&to_date=2026-01-31&mood=good"
```

Filters:
- `limit` (max 100)
- `from_date` (`YYYY-MM-DD`)
- `to_date` (`YYYY-MM-DD`)
- `mood` (`fully_charged`, `good`, `sleepy`, `terrible`)
- `missing_steps=true`

### Get one sleep entry (details)

```bash
curl -H "Authorization: Bearer SOFT_PILLOW_API_KEY" \
  "https://softpillow.paevita.com/api/v1/sleep_entries/ENTRY_ID"
```

Returns summary + details (`dream`, `notes`, `disruptions`, `insights`, timestamps).

### Search dreams and notes

```bash
curl --get -H "Authorization: Bearer SOFT_PILLOW_API_KEY" \
  --data-urlencode "query=flying ocean" \
  "https://softpillow.paevita.com/api/v1/search_dreams"
```

Optional:
- `limit` (max 50, default 10)

Returns entry matches with `dream_excerpt` and `notes_excerpt`.

## Error behavior

- Missing/invalid auth: `401` JSON error
- Invalid filters (for example bad `mood` or bad date): `422` JSON error
- Entry not found (or not yours): `404` JSON error

