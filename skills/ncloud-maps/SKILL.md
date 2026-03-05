---
name: ncloud-maps
description: "Query Naver Cloud Maps APIs for route navigation. Smart routing: Directions5 by default, auto-switches to Directions15 for 5+ waypoints."
---

## Prompt

When a user requests a route calculation with addresses or coordinates, use this skill to calculate driving time, distance, and cost.

**Usage:**
- `/skill ncloud-maps <start> <goal> [waypoints]`
- Start and goal must be in `longitude,latitude` format OR addresses (convert using goplaces/naver-local-search first)
- Returns: distance, duration, toll fare, taxi fare, fuel cost

**Examples:**
- `/skill ncloud-maps "126.9633,37.5524" "127.0165,37.4889"` (coordinates)
- `/skill ncloud-maps 아현역 서초역` (addresses - requires geocoding skill first)

# Ncloud Maps

Query Naver Cloud Maps APIs for intelligent routing (Directions5 + Directions15).

## Key Feature: Smart Routing

**v1.0.8+** — By default, the skill uses **Directions5** for queries with fewer than 5 waypoints, and automatically switches to **Directions15** when you have 5 or more waypoints. No manual selection needed.

| Waypoints | API Used | Max Waypoints |
|-----------|----------|---------------|
| 0–4       | Directions5 | 5 |
| 5+        | Directions15 | 15 |

## Setup

1. **Get API credentials from Naver Cloud Console:**
   - Create/register an Application in Naver Cloud Console
   - Obtain `Client ID` (API Key ID) and `Client Secret` (API Key)
   - Enable "Maps Directions15" API

2. **Set environment variables (or use .env file):**

```bash
export NCLOUD_API_KEY_ID="your-api-key-id"
export NCLOUD_API_KEY="your-api-key-secret"
```

Or create a `.env` file:
```
NCLOUD_API_KEY_ID=your-api-key-id
NCLOUD_API_KEY=your-api-key-secret
```

3. **Install dependencies:**

```bash
cd ~/.openclaw/workspace/skills/ncloud-maps
npm install
```

## Usage

### Using with Address-to-Coordinate Skills

ncloud-maps requires coordinates in `longitude,latitude` format. If you have address-based location data, use one of these compatible skills to convert addresses to coordinates:

**Available Options (choose based on your environment):**

| Skill | Provider | Coordinates | Setup Required |
|-------|----------|-------------|-----------------|
| `goplaces` | Google Places API | Yes (lon,lat) | `GOOGLE_PLACES_API_KEY` |
| `naver-local-search` | Naver Local Search | Yes (lon,lat) | `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET` |
| Custom API | Your choice | Yes (lon,lat) | Your setup |

**Example workflow with goplaces:**

```bash
# Get coordinates from address
COORDS=$(goplaces resolve "강남역, 서울" --json | jq -r '.places[0] | "\(.location.longitude),\(.location.latitude)"')

# Use coordinates with ncloud-maps
npx ts-node scripts/index.ts --start "$COORDS" --goal "127.0049,37.4947"
```

**Example workflow with naver-local-search:**

```bash
# Get coordinates from address
COORDS=$(naver-local-search search "강남역" --format json | jq -r '.[0] | "\(.x),\(.y)"')

# Use coordinates with ncloud-maps
npx ts-node scripts/index.ts --start "$COORDS" --goal "127.0049,37.4947"
```

**Or integrate any other geocoding service** that returns `longitude,latitude` coordinates.

### Smart Routing (Default Behavior)

By default, no `--api` flag needed. The skill automatically:
- Uses **Directions5** for 0–4 waypoints (faster)
- Switches to **Directions15** for 5+ waypoints (necessary)

Provide coordinates in `longitude,latitude` format:

```bash
# 0–4 waypoints → Directions5 (automatic)
npx ts-node scripts/index.ts \
  --start "127.0683,37.4979" \
  --goal "126.9034,37.5087" \
  --waypoints "127.0100,37.5000|127.0200,37.5100"

# 5+ waypoints → Directions15 (automatic)
npx ts-node scripts/index.ts \
  --start "127.0683,37.4979" \
  --goal "126.9034,37.5087" \
  --waypoints "127.0100,37.5000|127.0200,37.5100|127.0300,37.5200|127.0400,37.5300|127.0500,37.5400"
```

### Basic route query by coordinates (direct)

```bash
npx ts-node scripts/index.ts \
  --start "127.0683,37.4979" \
  --goal "126.9034,37.5087"
```

### Force specific API (optional)

If you need to override the smart routing:

```bash
# Force Directions5 (max 5 waypoints)
npx ts-node scripts/index.ts \
  --start "127.0683,37.4979" \
  --goal "126.9034,37.5087" \
  --api directions5 \
  --waypoints "127.0100,37.5000|127.0200,37.5100"

# Force Directions15 (max 15 waypoints)
npx ts-node scripts/index.ts \
  --start "127.0683,37.4979" \
  --goal "126.9034,37.5087" \
  --api directions15 \
  --waypoints "127.0100,37.5000|127.0200,37.5100|127.0300,37.5200|127.0400,37.5300|127.0500,37.5400"
```

### With waypoints (coordinates only)

```bash
npx ts-node scripts/index.ts \
  --start "127.0683,37.4979" \
  --goal "126.9034,37.5087" \
  --waypoints "127.0100,37.5000"
```

Multiple waypoints:
```bash
npx ts-node scripts/index.ts \
  --start "127.0683,37.4979" \
  --goal "126.9034,37.5087" \
  --waypoints "127.0100,37.5000|127.0200,37.5100"
```

### Route options

Choose from: `trafast` (fast), `tracomfort` (comfort), `traoptimal` (default), `traavoidtoll` (toll-free), `traavoidcaronly` (avoid car-only roads)

```bash
npx ts-node scripts/index.ts \
  --start "127.0683,37.4979" \
  --goal "126.9034,37.5087" \
  --option "traavoidtoll"
```

### Vehicle and fuel settings

```bash
npx ts-node scripts/index.ts \
  --start "127.0683,37.4979" \
  --goal "126.9034,37.5087" \
  --cartype 2 \
  --fueltype "diesel" \
  --mileage 10.5
```

Vehicle types:
- `1` (default): Small sedan
- `2`: Medium van/cargo
- `3`: Large vehicle
- `4`: 3-axle cargo truck
- `5`: 4+ axle special cargo
- `6`: Compact car

Fuel types: `gasoline` (default), `highgradegasoline`, `diesel`, `lpg`

## Output

```json
{
  "success": true,
  "start": "127.0683,37.4979",
  "goal": "126.9034,37.5087",
  "distance": 12850,
  "duration": 1145000,
  "toll_fare": 0,
  "taxi_fare": 18600,
  "fuel_price": 1550,
  "departure_time": "2026-02-21T14:10:00"
}
```

### Response Fields

- `success` - Whether the query succeeded
- `start` - Starting point coordinates
- `goal` - Destination coordinates
- `distance` - Total distance in meters
- `duration` - Total duration in milliseconds (÷1000 = seconds)
- `toll_fare` - Toll/highway fare in KRW
- `taxi_fare` - Estimated taxi fare in KRW
- `fuel_price` - Estimated fuel cost in KRW
- `departure_time` - Query timestamp
- `error` - Error message (if success=false)

## How It Works

1. **Address Resolution (Optional - any geocoding skill)**
   - Use any available skill that provides coordinates (goplaces, naver-local-search, etc.)
   - Extract `longitude,latitude` format from the result
   - Pass coordinates to ncloud-maps

2. **Coordinate Validation**
   - Input: Coordinates in `longitude,latitude` format (direct input or from geocoding skill)
   - Validates format and range
   - Returns error if format is invalid

3. **Route Calculation (Directions15 or Directions5)**
   - Coordinates sent to appropriate Directions API
   - Returns distance, duration, tolls, taxi fare, fuel cost
   - **Only for vehicle (car) routes** — not for pedestrian or public transit

4. **Waypoints Support**
   - Each waypoint must be in `longitude,latitude` format
   - All coordinates sent to Directions API

## Limitations

⚠️ **This skill only calculates vehicle (car) routes.** It does not support:
- Public transportation (subway, bus, etc.)
- Walking routes
- Multi-modal journeys
- Transit-specific features (fare, stops, schedules)

For those use cases, use transit-specific APIs (e.g., Kakao Map, Naver Map Transit API).

## Environment Variables

**Required:**
- `NCLOUD_API_KEY_ID` - Naver Cloud API Key ID
- `NCLOUD_API_KEY` - Naver Cloud API Key Secret

## API Limits

**Smart Routing:**
- 0–4 waypoints: Directions5 API (max 5 waypoints)
- 5+ waypoints: Directions15 API (max 15 waypoints)

**General:**
- Real-time traffic information included
- Request rate limits apply per your Naver Cloud plan

## Error Handling

Common errors:
- `좌표 형식 오류` - Invalid coordinate format (use `longitude,latitude`)
- `Authentication Failed` - Invalid API credentials
- `Quota Exceeded` - API rate limit hit
- `No routes found` - No valid route between points

Check Naver Cloud Console for:
- API enablement for your application
- Quota/rate limit status
- Valid coordinates

## References

See [api-spec.md](references/api-spec.md) for detailed API specifications.
