# TomTom API Response Reference

## Geocoding API

**Endpoint:** `GET https://api.tomtom.com/search/2/geocode/{query}.json?key={key}&countrySet=CH&limit=1`

**Example response (abridged):**

```json
{
  "results": [
    {
      "type": "Geography",
      "id": "CH/GEO/p0/30190",
      "score": 5.4,
      "address": {
        "municipality": "Basel",
        "countrySubdivision": "Basel-Stadt",
        "country": "Switzerland",
        "countryCode": "CH",
        "freeformAddress": "Basel, Basel-Stadt"
      },
      "position": {
        "lat": 47.55764,
        "lon": 7.59262
      }
    }
  ]
}
```

**Key fields used by script:**
- `results[0].position.lat` / `.lon` — coordinates for routing
- `results[0].address.freeformAddress` — human-readable resolved address

---

## Routing API (Calculate Route)

**Endpoint:** `GET https://api.tomtom.com/routing/1/calculateRoute/{lat,lng}:{lat,lng}/json?key={key}&traffic=true&computeTravelTimeFor=all&travelMode=car&routeType=fastest&maxAlternatives=2&routeRepresentation=summaryOnly`

**Example response (abridged):**

```json
{
  "formatVersion": "0.0.12",
  "routes": [
    {
      "summary": {
        "lengthInMeters": 87400,
        "travelTimeInSeconds": 3526,
        "trafficDelayInSeconds": 180,
        "trafficLengthInMeters": 2400,
        "departureTime": "2026-02-28T08:15:00+01:00",
        "arrivalTime": "2026-02-28T09:13:46+01:00",
        "noTrafficTravelTimeInSeconds": 3120,
        "historicTrafficTravelTimeInSeconds": 3400,
        "liveTrafficIncidentsTravelTimeInSeconds": 3526
      }
    }
  ]
}
```

**Summary field definitions:**

| Field | Type | Description |
|-------|------|-------------|
| `lengthInMeters` | int | Total route distance |
| `travelTimeInSeconds` | int | Best estimate with current traffic (uses live + historic) |
| `trafficDelayInSeconds` | int | Extra seconds caused by traffic vs. free-flow |
| `trafficLengthInMeters` | int | Length of route affected by traffic |
| `departureTime` | string | ISO 8601 departure time |
| `arrivalTime` | string | ISO 8601 estimated arrival |
| `noTrafficTravelTimeInSeconds` | int | Free-flow time (no traffic at all) |
| `historicTrafficTravelTimeInSeconds` | int | Based on historical traffic patterns for this day/time |
| `liveTrafficIncidentsTravelTimeInSeconds` | int | Including real-time incident data |

**Note:** `computeTravelTimeFor=all` is required to get the `noTrafficTravelTimeInSeconds`, `historicTrafficTravelTimeInSeconds`, and `liveTrafficIncidentsTravelTimeInSeconds` fields. Without it, only `travelTimeInSeconds` and `trafficDelayInSeconds` are returned.

---

## API Quotas (Free Tier)

- **Daily limit:** 2,500 non-tile requests (shared across all TomTom APIs)
- **Per traffic check:** 3 requests (geocode × 2 + route × 1)
- **Effective checks/day:** ~830
- **No credit card required**
- **Rate limit response:** HTTP 429
