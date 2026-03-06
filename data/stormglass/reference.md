# Stormglass Surf Skill Reference

## External APIs

- Stormglass docs: [https://docs.stormglass.io/#/](https://docs.stormglass.io/#/)
- Weather point endpoint: `GET https://api.stormglass.io/v2/weather/point`
- Tide extremes endpoint (preferred): `GET https://api.stormglass.io/v2/tide/extremes/point`
- Tide extremes fallback: `GET https://api.stormglass.io/v2/tide/extremes`
- Google geocoding endpoint: `GET https://maps.googleapis.com/maps/api/geocode/json`
- OpenStreetMap fallback geocoding endpoint: `GET https://nominatim.openstreetmap.org/search`

## Authentication

- Stormglass: send `Authorization: <STORMGLASS_API_KEY>`
- Google Geocoding: query parameter `key=<GOOGLE_GEOCODING_API_KEY>`

## Geocoding Flow (`--location`)

1. Request:
   - If `GOOGLE_GEOCODING_API_KEY` is set, use Google:
     - `address=<user location string>`
     - `key=<google key>`
   - Else fallback to OpenStreetMap Nominatim:
     - `q=<user location string>`
     - `format=jsonv2`
     - `limit=5`
2. Validate response and parse top match.
3. Capture:
   - `formatted_address`
   - `geometry.location.lat`
   - `geometry.location.lng`
   - `place_id` (if present)
   - For OSM fallback, use:
     - `display_name`
     - `lat`
     - `lon`
4. If multiple candidates exist, return warning in `meta.warnings`.

## Stormglass Weather Request

Query params:

- `lat`, `lng`
- `params=waveHeight,swellHeight,swellPeriod,swellDirection,windSpeed,windDirection,gust,waterTemperature`
- `start=<unix-utc-seconds>`
- `end=<unix-utc-seconds>`
- optional `source=<provider1,provider2>`

Response handling:

- Read `hours[]`.
- For each metric, values may be:
  - a number, or
  - an object of per-source values.
- If per-source object, choose first non-null value by precedence:
  - user-selected source order (if provided)
  - else default order: `sg`, `icon`, `gfs`, `ecmwf`, `dwd`, `noaa`, then first available key

## Stormglass Tide Request

Query params:

- `lat`, `lng`
- `start=<YYYY-MM-DD>`
- `end=<YYYY-MM-DD>`

Response handling:

- Read `data[]` from tide endpoint.
- Normalize each extreme into:
  - `time` (ISO UTC)
  - `height` (meters, nullable)
  - `type` (`high` or `low`)
- If `/v2/tide/extremes/point` fails with 404/400, retry `/v2/tide/extremes`.

## JSON Output Schema (Stable)

```json
{
  "meta": {
    "generatedAt": "2026-02-22T12:00:00Z",
    "horizon": "72h",
    "inputMode": "location|coordinates",
    "sourcesRequested": ["sg"],
    "warnings": []
  },
  "location": {
    "query": "Highcliffe Beach",
    "resolvedName": "Highcliffe, Christchurch, UK",
    "lat": 50.735,
    "lon": -1.705,
    "googlePlaceId": "..."
  },
  "now": {
    "time": "2026-02-22T12:00:00Z",
    "waveHeightM": 1.2,
    "swellHeightM": 0.8,
    "swellPeriodS": 9.4,
    "swellDirectionDeg": 245,
    "windSpeedMps": 5.1,
    "windDirectionDeg": 215,
    "windGustMps": 7.8,
    "waterTemperatureC": 10.9
  },
  "forecast": {
    "windows": {
      "24h": { "start": "...", "end": "...", "bestHours": [] },
      "48h": { "start": "...", "end": "...", "bestHours": [] },
      "72h": { "start": "...", "end": "...", "bestHours": [] }
    }
  },
  "tides": {
    "trendNow": "rising|falling|unknown",
    "extremes": []
  }
}
```

## Null / Missing Data Rules

- If upstream omits a metric, emit `null` for that field.
- Do not substitute `0` for missing values.
- Keep key names stable even when values are null.

## Cron and Downstream Agent Notes

- Use JSON mode in cron (`--output json`) and parse stdout only.
- Treat non-zero exit code as failure; parse stderr for diagnostics.
- Persist raw JSON for observability and replay.
- Optional post-processing: pipe through `scripts/normalize_surf_data.py` to enforce stable null/field defaults.
