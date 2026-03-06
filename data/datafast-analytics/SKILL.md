---
name: datafast-analytics
description: Query DataFast website analytics and visitor data via the DataFast API for metrics, time series, realtime stats, breakdowns, visitor details, and goal/payment management.
metadata: {"openclaw":{"homepage":"https://datafa.st"}}
---

# DataFast Analytics Skill

Use this skill to call the DataFast API and summarize results for the user.

## Quick Workflow

1. Confirm the request type (overview, timeseries, realtime, breakdown, visitor, goals/payments create/delete).
2. Gather required inputs:
   - Date range: `startAt` and `endAt` together or neither (overview/timeseries support ranges).
   - `timezone`, `fields`, `interval`, `limit`, `offset`, and any `filter_*` parameters.
3. Build the HTTP request with `Authorization: Bearer $DATAFAST_API_KEY` and `Content-Type: application/json`.
4. Execute with `curl` and parse JSON.
5. Summarize results in a table plus a short narrative (totals + key takeaways). Include pagination info if relevant.

## Setup

1. Get your API key from DataFast (starts with `df_`).
2. Store it:
```bash
mkdir -p ~/.config/datafast
echo "df_your_key_here" > ~/.config/datafast/api_key
```

## Authentication

All requests need:
```bash
DATAFAST_API_KEY=$(cat ~/.config/datafast/api_key)
curl ... \
  -H "Authorization: Bearer $DATAFAST_API_KEY" \
  -H "Content-Type: application/json"
```

If the user hasn't set up the API key, ask them to follow the setup steps above.

## Base URL

`https://datafa.st/api/v1/`

## Reference Docs

Use the full API reference at `{baseDir}/references/datafast-api-docs.md` for endpoint details, response fields, and examples.

## Endpoint Guidance

### Overview
- `GET /analytics/overview`
- Optional: `startAt`, `endAt`, `timezone`, `fields`.

### Time Series
- `GET /analytics/timeseries`
- Typical params: `fields`, `interval` (hour/day/week/month), `startAt`, `endAt`, `timezone`, `limit`, `offset`.
- Accepts `filter_*` query params for segmentation.
- **Note:** `fields` is required (e.g., `fields=visitors,sessions`).

### Realtime
- `GET /analytics/realtime`
- `GET /analytics/realtime/map`

### Breakdowns
- `GET /analytics/devices`
- `GET /analytics/pages`
- `GET /analytics/campaigns`
- `GET /analytics/goals`
- `GET /analytics/referrers`
- `GET /analytics/countries`
- `GET /analytics/regions`
- `GET /analytics/cities`
- `GET /analytics/browsers`
- `GET /analytics/operating-systems`
- `GET /analytics/hostnames`

### Visitor Details
- `GET /visitors/{datafast_visitor_id}`

### Goals
- Create goal: `POST /goals`
- Delete goals: `DELETE /goals` (requires at least one filter or time range; confirm scope)

### Payments
- Create payment: `POST /payments`
- Delete payments: `DELETE /payments` (confirm scope)

## Destructive Actions

For `DELETE /goals` or `DELETE /payments`:
- Always confirm exact filters and time range in plain English before executing.
- If user asks for "all time" deletion, ask for explicit confirmation.
- Echo the final URL that will be called (without the API key).

## Filter Syntax

Use `filter_*` params for segmentation (e.g., `filter_referrer=is:X`).

**Important:** Filter values must match the exact names from breakdown endpoints. For example, X/Twitter is stored as "X" (not "x.com" or "twitter.com"). When in doubt, query the breakdown first:
```bash
curl ... "/analytics/referrers?limit=20"
```
Then use the exact `referrer` value in your filter.

## Example Command Patterns

### GET
```bash
DATAFAST_API_KEY=$(cat ~/.config/datafast/api_key)
curl -sS "https://datafa.st/api/v1/analytics/overview?startAt=2024-01-01&endAt=2024-01-31&timezone=UTC" \
  -H "Authorization: Bearer $DATAFAST_API_KEY" \
  -H "Content-Type: application/json"
```

### POST
```bash
DATAFAST_API_KEY=$(cat ~/.config/datafast/api_key)
curl -sS "https://datafa.st/api/v1/goals" \
  -H "Authorization: Bearer $DATAFAST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"datafast_visitor_id":"...","name":"newsletter_signup","metadata":{"email":"..."}}'
```

### DELETE
```bash
DATAFAST_API_KEY=$(cat ~/.config/datafast/api_key)
curl -sS -X DELETE "https://datafa.st/api/v1/goals?name=signup&startAt=2023-01-01T00:00:00Z&endAt=2023-01-31T23:59:59Z" \
  -H "Authorization: Bearer $DATAFAST_API_KEY"
```

## Output Expectations

- Provide a short summary and a flat table of results.
- Include totals and conversion/revenue metrics when present.
- For time series, include the top-level totals and the first/last timestamps in the selected range.
- If pagination exists, report `limit`, `offset`, and `total`, and ask if the user wants the next page.