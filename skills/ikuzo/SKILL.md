---
name: ikuzo
description: Manage maps, spots, and travel plans on Ikuzo (ikuzo.app) — a location-based exploration app. Use when creating/editing maps, adding/searching spots, planning trips with day-by-day itineraries, finding nearby places, or managing travel logistics. Triggers on map management, spot tracking, trip planning, location discovery, and "where should I go" questions.
---

# Ikuzo

Ikuzo is a map & travel planning app. Access via MCP (JSON-RPC 2.0 over HTTP POST).

## Connection

```
Endpoint: https://ikuzo.app/api/mcp
Auth: Bearer token (from TOOLS.md or user config)
Protocol: JSON-RPC 2.0 — POST with {"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"<tool>","arguments":{...}}}
```

## Tools

### Maps
- `maps_list` — list all maps (owned + shared)
- `maps_get(mapId)` — get map details
- `maps_create(title)` — create a new empty map, returns map with ID

### Spots
- `spots_list(mapId, ...)` — list/filter spots in a map. Filters: `status[]`, `type[]`, `period[]`, `momentFrom/To`, `text`, `limit`, `offset`, `fields[]`
- `spots_get(spotId)` — get spot details
- `spots_create(mapId, title, gps{lat,lng}, ...)` — create spot. Optional: `description`, `type`, `status`, `period[]`, `moment{date, repeat, reminder[]}`
- `spots_update(spotId, ...)` — update any field (including `moment`, `rating`)
- `spots_delete(spotId)` — soft delete (recoverable)
- **`spots_nearby(lat, lng, ...)`** — find spots near a point across ALL accessible maps. Optional: `radius` (km, default 10, max 500), `mapIds[]`, all spot filters. Returns sorted by distance.
- `spots_box(north, south, east, west, ...)` — find spots in bounding box. Same filters as nearby.

### Travel Plans
- `travels_list` — list all travel plans
- `travels_get(travelId)` — get plan with steps
- `travels_create(title)` — create plan
- `travels_update(travelId, title)` — rename plan
- `travels_delete(travelId)` — delete plan

### Steps (within a travel plan)
- `steps_add(travelId, type, ...)` — add step. `type="spot"` requires `spotId`, `type="day"` requires `title`. Optional: `orderKey`
- `steps_update(stepId, ...)` — update position or title
- `steps_delete(stepId)` — remove step

### Utility
- `ping` — test connection
- `schema` — get valid values for `type`, `status`, `period`
- `quota` — check API usage (doesn't count against quota)

## Schema Reference

See `references/schema.md` for valid spot types, statuses, and periods. Call `schema` tool at runtime if unsure.

## Key Patterns

### Find spots to visit nearby
```
spots_nearby(lat, lng, radius=20, status=["a","b"])
```
Status `a` = "Ikuzo!" (priority), `b` = "To Visit"

### Seasonal spots with upcoming moments
```
spots_list(mapId, momentFrom="2026-03-01", momentTo="2026-04-30")
```

### Create a trip itinerary
1. `travels_create(title)` → get travelId
2. `steps_add(travelId, type="day", title="Day 1 - Arrival")`
3. `steps_add(travelId, type="spot", spotId="...")` for each spot
4. Repeat day dividers + spots for each day

### Efficient listing (reduce tokens)
Use `fields` to request only what you need:
```
spots_list(mapId, fields=["_id","title","gps","status","type"])
```

### Image URLs
Spot images use Ikuzo's CDN:
```
https://ik.offbeatjapan.org/ikuzo/{imageId}.{ext}?tr=h-{height},w-{width}
```
Where `imageId` and `ext` come from the spot's `image[]` array.
