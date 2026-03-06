# Umami read endpoints (GET)

Path rule:
- Umami Cloud: `/v1/...`
- Self-hosted Umami: `/api/...` (same suffix)

Source basis: Umami route tree (`src/app/api/**/route.ts`) from upstream repository.
Use this as a practical map; verify details/params in official docs: `https://v2.umami.is/docs/api`.

## Core discovery

- `/v1/me`
- `/v1/me/teams`
- `/v1/me/websites`
- `/v1/websites`
- `/v1/websites/[websiteId]`
- `/v1/teams`
- `/v1/teams/[teamId]`
- `/v1/users/[userId]`

## Website analytics

- `/v1/websites/[websiteId]/stats`
- `/v1/websites/[websiteId]/metrics`
- `/v1/websites/[websiteId]/metrics/expanded`
- `/v1/websites/[websiteId]/pageviews`
- `/v1/websites/[websiteId]/values`
- `/v1/websites/[websiteId]/active`
- `/v1/websites/[websiteId]/daterange`

## Events and event-data

- `/v1/websites/[websiteId]/events`
- `/v1/websites/[websiteId]/events/series`
- `/v1/websites/[websiteId]/event-data/events`
- `/v1/websites/[websiteId]/event-data/fields`
- `/v1/websites/[websiteId]/event-data/properties`
- `/v1/websites/[websiteId]/event-data/values`
- `/v1/websites/[websiteId]/event-data/stats`
- `/v1/websites/[websiteId]/event-data/[eventId]`

## Sessions

- `/v1/websites/[websiteId]/sessions`
- `/v1/websites/[websiteId]/sessions/stats`
- `/v1/websites/[websiteId]/sessions/weekly`
- `/v1/websites/[websiteId]/sessions/[sessionId]`
- `/v1/websites/[websiteId]/sessions/[sessionId]/activity`
- `/v1/websites/[websiteId]/sessions/[sessionId]/properties`
- `/v1/websites/[websiteId]/session-data/properties`
- `/v1/websites/[websiteId]/session-data/values`

## Reports / advanced analytics

- `/v1/reports`
- `/v1/reports/[reportId]`
- `/v1/reports/attribution`
- `/v1/reports/breakdown`
- `/v1/reports/funnel`
- `/v1/reports/goal`
- `/v1/reports/journey`
- `/v1/reports/retention`
- `/v1/reports/revenue`
- `/v1/reports/utm`
- `/v1/websites/[websiteId]/reports`

## Realtime and share

- `/v1/realtime/[websiteId]`
- `/v1/share/[shareId]`

## Team/website linked resources (read)

- `/v1/teams/[teamId]/websites`
- `/v1/teams/[teamId]/users`
- `/v1/teams/[teamId]/users/[userId]`
- `/v1/teams/[teamId]/links`
- `/v1/teams/[teamId]/pixels`
- `/v1/users/[userId]/teams`
- `/v1/users/[userId]/websites`

## Admin read endpoints (requires admin permissions)

- `/v1/admin/teams`
- `/v1/admin/users`
- `/v1/admin/websites`

## Common time presets for script

- `today`
- `yesterday`
- `last24h`
- `last7d`
- `last30d`
- `monthToDate`
- `previousMonth`
- `yearToDate`

These presets map to `startAt` and `endAt` epoch milliseconds.

## Practical requirements / gotchas

- `.../metrics` and `.../metrics/expanded` require `type` (e.g. `url`, `referrer`, `browser`, `os`, `device`, `country`, `city`).
  - The helper script auto-defaults to `type=url`.
- `.../reports/*` endpoints often require `websiteId` + time range (`startAt`, `endAt`).
  - The helper auto-adds `websiteId` when available.
- Endpoints with path IDs (`teamId`, `sessionId`, `eventId`, `reportId`) require **real IDs**; placeholders often produce 500s.
- On Umami Cloud, `/v1/users/*` can return 403 for non-admin user API keys (this is expected for many accounts).
