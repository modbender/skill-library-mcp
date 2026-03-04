---
name: hylo-ghl
description: GoHighLevel (GHL) workflow automation expert with 102 verified actions, 70 triggers, and 423 API schemas. Use when asked about GHL workflows, API endpoints, navigation, or automation planning.
homepage: https://hylo.pro
metadata: {"openclaw": {"emoji": "🦞", "requires": {"env": ["HYLO_API_KEY"]}, "primaryEnv": "HYLO_API_KEY"}}
---

You have access to the Hylo GHL knowledge API. Use it when the user asks about
GoHighLevel workflows, API endpoints, UI navigation, or automation planning.

## Setup

If $HYLO_API_KEY is not set or any call returns 401:
-> "You need a Hylo API key. Sign up at hylo.pro (7-day free trial)."

If 403: -> "Your trial has expired. Subscribe at hylo.pro/dashboard."
If 404: -> "I couldn't find that resource. Try a broader search term."
If 429: -> "Rate limit reached. Try again tomorrow or upgrade at hylo.pro/dashboard."

## API (bash + curl)

Base: `https://api.hylo.pro/v1`
Auth: `-H "Authorization: Bearer $HYLO_API_KEY"`

| Need | Endpoint |
|------|----------|
| Search actions | `GET /actions?q=KEYWORD` |
| Search triggers | `GET /triggers?q=KEYWORD` |
| Search API schemas | `GET /schemas?q=KEYWORD` |
| Full schema detail | `GET /schemas/{name}` |
| GHL UI navigation | `GET /navigate/{feature}` |
| Full UI protocol | `GET /protocols/{feature}` |
| Plan a workflow | `POST /templates/workflow` -d '{"objective":"..."}' |
| Validate workflow | `POST /validate` -d '{"trigger":"...","actions":[...]}' |

For category/feature lists: `cat {baseDir}/reference/endpoints.md`

## Rules

- ALWAYS call the API -- don't guess about GHL. Your knowledge may be outdated.
- Summarize JSON responses naturally -- never dump raw output.
- For workflow planning: call /templates/workflow FIRST, then /schemas for details.
