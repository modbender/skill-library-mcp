# Naver Cloud Maps API Specification

Complete reference for Ncloud Maps APIs.

## Directions15 API

## API Endpoint

```
GET https://maps.apigw.ntruss.com/map-direction-15/v1/driving
```

## Request Headers

| Field | Required | Description |
|-------|----------|-------------|
| `x-ncp-apigw-api-key-id` | Yes | API Key ID (Client ID) |
| `x-ncp-apigw-api-key` | Yes | API Key Secret (Client Secret) |

## Query Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `start` | String | Start point (longitude,latitude) |
| `goal` | String | Destination (longitude,latitude); supports multiple destinations separated by `:` |
| | | Example: `goal=123.45,34.56:124.56,35.67` |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `waypoints` | String | Waypoints (longitude,latitude) separated by `\|`; max 5 | - |
| | | Example: `waypoints=127.1,37.1:127.2,37.2\|128.1,38.1` | - |
| `option` | String | Route option; multiple allowed via `:` | `traoptimal` |
| | | `trafast`: Fast route | |
| | | `tracomfort`: Comfort route | |
| | | `traoptimal`: Optimal route | |
| | | `traavoidtoll`: Toll-free priority | |
| | | `traavoidcaronly`: Avoid car-only roads | |
| `cartype` | Integer | Vehicle type (1-6) | `1` |
| | | 1: Small sedan, 2: Medium, 3: Large, 4: 3-axle cargo, 5: 4+ axle, 6: Compact | |
| `fueltype` | String | Fuel type | `gasoline` |
| | | `gasoline`, `highgradegasoline`, `diesel`, `lpg` | |
| `mileage` | Double | Fuel efficiency (km/L) | `14` |
| `lang` | String | Response language | `ko` |
| | | `ko`: Korean, `en`: English, `ja`: Japanese, `zh`: Simplified Chinese | |

## Response Format

### Success Response

```json
{
  "code": 0,
  "message": "ok",
  "currentDateTime": "2026-02-21T13:30:00",
  "route": {
    "traoptimal": [
      {
        "summary": {
          "start": {
            "location": [127.1058342, 37.359708]
          },
          "goal": {
            "location": [129.075986, 35.179470],
            "dir": 0
          },
          "distance": 298700,
          "duration": 8500000,
          "departureTime": "2026-02-21T13:30:00",
          "tollFare": 23000,
          "taxiFare": 45000,
          "fuelPrice": 3500,
          "bbox": [[127.1, 35.1], [129.1, 37.4]]
        },
        "path": [[127.1058342, 37.359708], [127.1057, 37.3596], ...],
        "section": [...],
        "guide": [...]
      }
    ]
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `code` | Integer | Response code (0 = success) |
| `message` | String | Response message |
| `currentDateTime` | String | Query timestamp (ISO format) |
| `route.{option}` | Array | Route array by requested option |

### Route Summary

| Field | Type | Description |
|-------|------|-------------|
| `start.location` | Array | [longitude, latitude] |
| `goal.location` | Array | [longitude, latitude] |
| `goal.dir` | Integer | Direction (0: ahead, 1: left, 2: right) |
| `distance` | Integer | Total distance (meters) |
| `duration` | Integer | Total duration (milliseconds) |
| `departureTime` | String | Departure time (ISO format) |
| `tollFare` | Integer | Toll fee (KRW) |
| `taxiFare` | Integer | Estimated taxi fare (KRW) |
| `fuelPrice` | Integer | Estimated fuel cost (KRW) |
| `bbox` | Array | Bounding box [[left_bottom], [right_top]] |

### Path

Array of coordinate arrays `[longitude, latitude]` representing the route geometry.

### Section

Major road segments with detailed info:

| Field | Type | Description |
|-------|------|-------------|
| `pointIndex` | Integer | Index in path array |
| `pointCount` | Integer | Number of points in segment |
| `distance` | Integer | Segment distance (meters) |
| `name` | String | Road name |
| `congestion` | Integer | Congestion level (0-3) |
| `speed` | Integer | Average speed (km/h) |

**Congestion levels:**
- 0: No data
- 1: Smooth (normal speed)
- 2: Slow
- 3: Congested

### Guide

Turn-by-turn navigation instructions:

| Field | Type | Description |
|-------|------|-------------|
| `pointIndex` | Integer | Index in path array |
| `type` | Integer | Turn type (see table below) |
| `instructions` | String | Navigation text |
| `distance` | Integer | Distance to next instruction (meters) |
| `duration` | Integer | Duration to next instruction (milliseconds) |

**Turn types:**
- 1: Straight
- 2: Left turn
- 3: Right turn
- 4: Left direction
- 5: Right direction
- 6: U-turn
- 8: Unprotected left turn
- 11-16: Diagonal directions (8/9/11 o'clock, 1/3/4 o'clock)
- 21-23: Roundabout instructions

## Error Responses

| HTTP Status | Code | Message | Meaning |
|-------------|------|---------|---------|
| 400 | 100 | Bad Request Exception | Invalid request syntax |
| 401 | 200 | Authentication Failed | Invalid credentials |
| 401 | 210 | Permission Denied | No API access |
| 404 | 300 | Not Found Exception | Server error |
| 413 | 430 | Request Entity Too Large | Request > 10 MB |
| 429 | 400 | Quota Exceeded | Rate limit hit |
| 429 | 410 | Throttle Limited | Too many rapid requests |
| 429 | 420 | Rate Limited | Too many requests in time window |
| 503 | 500 | Endpoint Error | Server error |
| 504 | 510 | Endpoint Timeout | Timeout |
| 500 | 900 | Unexpected Error | Unknown error |

## Coordinate Format

Use WGS84 (EPSG:4326) coordinates:
- Longitude: -180 to 180 (east-west)
- Latitude: -90 to 90 (north-south)

South Korea examples:
- Seoul: 127.1, 37.5
- Busan: 129.1, 35.1
- Daegu: 128.6, 35.9

## Notes

- Real-time traffic data is included in route calculations
- Identical requests may return different routes due to traffic changes
- Response times typically 1-3 seconds
- Supports both JSON requests and query parameters
- All distances in meters, durations in milliseconds
- All prices in Korean Won (KRW)
