# TripGo API - Routing

The Routing section provides endpoints for calculating door-to-door trips using public and private transport modes.

## Base URL

```
https://api.tripgo.com/v1
```

## Authentication

All requests require an API key passed in the `X-TripGo-Key` header:

```
X-TripGo-Key: YOUR_API_KEY
```

## Endpoints

### 1. A-to-B Trips

**Endpoint:** `GET /routing.json`

Calculates door-to-door trips for the specified mode(s).

**URL:** `https://api.tripgo.com/v1/routing.json`

**Required Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `v` | integer | Requested version number of output. Must be 11. |
| `from` | string | Origin coordinate as `(lat,lng)"name"` string (the `"name"` part is optional). |
| `to` | string | Destination coordinate as `(lat,lng)"name"` string (the `"name"` part is optional). |
| `modes` | array | Modes for which results should be returned (e.g., `pt_pub`, `wa_wal`, `me_car`). |

**Optional Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `fromStreetName` | string | The street name of `from` to ensure correct street selection. |
| `toStreetName` | string | The street name of `to` to ensure correct street selection. |
| `departAfter` | integer | Departure time in seconds since 1970. |
| `arriveBefore` | integer | Arrival time in seconds since 1970. |
| `allModes` | boolean | Set to `true` to return all trips regardless of mode count. |
| `neverAllowModes` | array | Modes to exclude from results. |
| `onlyAllowModes` | array | Only allow specific modes. |
| `avoidModes` | array | Public transport modes to avoid. |
| `tt` | number | Preferred minimum transfer time in minutes (default: 3.0). |
| `wm` | integer | Maximum walking duration in minutes. |
| `ws` | string | Walking speed: `0` (slow, 2.5 km/h), `1` (medium, 4 km/h), `2` (fast, 4.5 km/h). |
| `cs` | string | Cycling speed: `0` (slow, 12 km/h), `1` (medium, 18 km/h), `2` (fast, 25 km/h). |
| `wp` | string | User weighting profile `(price, environmental, duration, convenience)`. |
| `wheelchair` | boolean | Include wheelchair information in results. |
| `bestOnly` | boolean | Return only the best trip found. |

---

### 2. A-to-B-to-C Trip

**Endpoint:** `POST /waypoint.json`

Calculates a single A-to-B-to-C trip where transport modes can be customized per segment.

**URL:** `https://api.tripgo.com/v1/waypoint.json`

**Request Body:**

```json
{
  "from": "(lat,lng)\"name\"",
  "to": "(lat,lng)\"name\"",
  "via": "(lat,lng)\"name\"",
  "modes": ["pt_pub", "wa_wal"],
  "departAfter": 1532799914
}
```

**Required Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `from` | string | Origin coordinate as `(lat,lng)"name"` string. |
| `to` | string | Destination coordinate as `(lat,lng)"name"` string. |
| `via` | string | Waypoint coordinate as `(lat,lng)"name"` string. |

**Optional Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `modes` | array | Modes for each segment. |
| `departAfter` | integer | Departure time in seconds since 1970. |
| `arriveBefore` | integer | Arrival time in seconds since 1970. |

---

### 3. All-Day Routing Between Events

**Endpoint:** `POST /agenda/run`

Calculates itineraries for a complete time period considering a sequence of calendar events and habitual events (such as home, work, or a hotel stay). Handles vehicle parking/returning and event clashes.

**URL:** `https://api.tripgo.com/v1/agenda/run`

**Request Body:**

```json
{
  "config": {
    "modes": ["pt_pub", "me_car"]
  },
  "frame": {
    "startTime": 1532793600,
    "endTime": 1532822400
  },
  "items": [
    {
      "location": "(lat,lng)\"Home\"",
      "event": "home"
    },
    {
      "location": "(lat,lng)\"Office\"",
      "event": "work",
      "startTime": 1532800800,
      "endTime": 1532811600
    }
  ]
}
```

---

### 4. All-Day Routing Between Events (Deprecated)

> ⚠️ **DEPRECATED:** This endpoint is deprecated. Use `/agenda/run` instead.

**Endpoint:** `POST /skedgoify.json`

**URL:** `https://api.tripgo.com/v1/skedgoify.json`

This endpoint has the same functionality as `/agenda/run` but uses a different URL. It is maintained for backward compatibility but should not be used for new implementations.

**Request Body:** Same as `/agenda/run`.

---

## Response Format

All routing endpoints return a `RoutingResponse` object containing:

- `groups`: Array of trip groups
- `segments`: Segment templates for building complete trip details
- `trip`: Array of trip objects

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad request - missing or invalid parameters |
| 401 | Server doesn't have the specified region |
| 1001 | Routing between these locations is not supported |
| 1002 | Origin lies outside covered area |
| 1003 | Destination lies outside covered area |
| 1101 | Destination equals origin |

## Example cURL

```bash
curl 'https://api.tripgo.com/v1/routing.json?from=(-33.859,151.207)&to=(-33.863,151.208)&departAfter=1532799914&modes=wa_wal&v=11&locale=en' \
  -H 'Accept: application/json' \
  -H 'X-TripGo-Key: YOUR_API_KEY'
```

## See Also

- [TripGo Developer Docs](https://developer.tripgo.com/)
- [Mode Identifiers](https://developer.tripgo.com/faq/#mode-identifiers)
- [OpenAPI Spec](https://github.com/skedgo/tripgo-api)
