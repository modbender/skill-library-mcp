---
name: geomanic
description: Query and manage GPS travel data from Geomanic — your privacy-first GPS tracking platform.
metadata: {"clawdbot":{"emoji":"🌍","requires":{"env":["GEOMANIC_TOKEN"]},"primaryEnv":"GEOMANIC_TOKEN","homepage":"https://geomanic.com","source":"https://github.com/monswyk/geomanic-mcp"}}
---

# Geomanic Skill

This skill connects to the Geomanic MCP API to query travel statistics, manage waypoints, and analyze journeys.

## Authentication

The API key is stored in the environment variable `GEOMANIC_TOKEN`. All requests must include it as a Bearer token.

## How to call the API

Use `curl` via the exec tool to send JSON-RPC requests to `https://geomanic.com/api/v1/mcp`:

```bash
curl -s -X POST https://geomanic.com/api/v1/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GEOMANIC_TOKEN" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"TOOL_NAME","arguments":{...}}}'
```

## Available tools

### get_statistics
Get aggregated travel statistics for a time period. Returns total distance (km), average/max speed (km/h), altitude, waypoint count, active days, and country breakdown with full/part days.

Required parameters: `from` (ISO 8601), `to` (ISO 8601).
Optional: `suppress_flights` (boolean, default true).

Example:
```bash
curl -s -X POST https://geomanic.com/api/v1/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GEOMANIC_TOKEN" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_statistics","arguments":{"from":"2026-02-22T00:00:00Z","to":"2026-02-22T23:59:59Z"}}}'
```

### get_date_range
Get the earliest and latest waypoint dates for the user. No parameters required.

```bash
curl -s -X POST https://geomanic.com/api/v1/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GEOMANIC_TOKEN" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_date_range","arguments":{}}}'
```

### list_waypoints
List waypoints with optional time range, pagination, and sorting.

Optional parameters: `from`, `to` (ISO 8601), `limit` (default 50, max 200), `offset` (default 0), `order` ("asc" or "desc", default "desc").

```bash
curl -s -X POST https://geomanic.com/api/v1/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $GEOMANIC_TOKEN" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list_waypoints","arguments":{"from":"2026-02-22T00:00:00Z","to":"2026-02-22T23:59:59Z","limit":10}}}'
```

### get_waypoint
Get a single waypoint by UUID.

Required: `id` (string, UUID).

### create_waypoint
Create a new GPS waypoint.

Required: `timestamp_utc` (ISO 8601), `latitude` (number), `longitude` (number).
Optional: `speed_kmh`, `altitude`, `heading_deg`, `device_id`.

### update_waypoint
Update an existing waypoint by UUID.

Required: `id` (string, UUID).
Optional: `latitude`, `longitude`, `speed_kmh`, `altitude`, `heading_deg`, `country_iso`, `place`, `device_id`.

### delete_waypoint
Delete a waypoint by UUID.

Required: `id` (string, UUID).

## Important notes

- All dates must be in ISO 8601 format with timezone (use UTC with Z suffix).
- For "today" queries, use the current date with T00:00:00Z to T23:59:59Z.
- The response is JSON-RPC. The actual data is inside `result.content[0].text` as a JSON string.
- Distance is in kilometers, speed in km/h, altitude in meters.
