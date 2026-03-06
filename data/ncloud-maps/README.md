# Ncloud Maps

🗺️ **Naver Cloud Maps API integration for OpenClaw** - Calculate driving routes with real-time traffic data.

[![npm version](https://img.shields.io/npm/v/ncloud-maps-skill.svg)](https://www.npmjs.com/package/ncloud-maps-skill)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

✨ **Smart Routing** - Intelligent API selection
- **Directions5** (0-4 waypoints) - Lightweight, optimized
- **Directions15** (5+ waypoints) - Full-featured, up to 15 stops
- **Automatic selection** - No configuration needed; choose based on waypoint count
- **Manual override** - Force specific API with `--api` flag if needed

🛣️ **Directions APIs** - Calculate optimal driving routes
- Distance (meters)
- Duration (milliseconds)
- Toll fare (KRW)
- Taxi fare estimate (KRW)
- Fuel cost estimate (KRW)
- Real-time traffic info

🔄 **Waypoints Support** - Multi-stop routing
- Directions5: Up to 5 intermediate stops (auto-selected)
- Directions15: Up to 15 intermediate stops (auto-selected)
- Coordinates only (longitude,latitude format)

⚙️ **Route Options**
- `trafast` - Fastest route
- `tracomfort` - Most comfortable
- `traoptimal` - Default (best balance)
- `traavoidtoll` - Toll-free route
- `traavoidcaronly` - Avoid car-only roads

🚗 **Vehicle Settings**
- 6 vehicle types (sedan, van, truck, etc.)
- Fuel types (gasoline, diesel, LPG)
- Custom mileage

## Quick Start

### Installation (OpenClaw)

```bash
# Via ClawHub
clawhub install ncloud-maps

# Or locally
npm install ncloud-maps-skill
```

### Authentication

Get API credentials from [Naver Cloud Console](https://console.ncloud.com):

1. Create/register an Application
2. Enable "Maps Directions15"
3. Copy `Client ID` and `Client Secret`

Set environment variables:

```bash
export NCLOUD_API_KEY_ID="your-client-id"
export NCLOUD_API_KEY="your-client-secret"
```

Or create `.env`:
```
NCLOUD_API_KEY_ID=your-client-id
NCLOUD_API_KEY=your-client-secret
```

### Basic Usage

**Smart Routing (Default)**

Provide coordinates in `longitude,latitude` format:

```bash
# 0-4 waypoints → Automatically uses Directions5 (lighter, faster)
npx ts-node scripts/index.ts \
  --start "127.0683,37.4979" \
  --goal "126.9034,37.5087" \
  --waypoints "127.0100,37.5000|127.0200,37.5100"

# 5+ waypoints → Automatically uses Directions15 (supports up to 15 stops)
npx ts-node scripts/index.ts \
  --start "127.0683,37.4979" \
  --goal "126.9034,37.5087" \
  --waypoints "127.0100,37.5000|127.0200,37.5100|127.0300,37.5200|127.0400,37.5300|127.0500,37.5400"
```

The skill automatically selects the optimal API. No `--api` flag needed.

**Force Specific API (Optional)**

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

**Other Queries**

```bash
# Query by coordinates (direct)
npx ts-node scripts/index.ts \
  --start "127.0683,37.4979" \
  --goal "126.9034,37.5087"

# With route options
npx ts-node scripts/index.ts \
  --start "127.0683,37.4979" \
  --goal "126.9034,37.5087" \
  --option "traavoidtoll"
```

## Output Example

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

## API Parameters

### Required
- `--start` - Starting point (longitude,latitude format, e.g., 127.0683,37.4979)
- `--goal` - Destination (longitude,latitude format, e.g., 126.9034,37.5087)

### Optional
- `--waypoints` - Intermediate stops in longitude,latitude format, pipe-separated (max 15)
- `--option` - Route preference (trafast|tracomfort|traoptimal|traavoidtoll|traavoidcaronly)
- `--cartype` - Vehicle type (1-6)
- `--fueltype` - Fuel type (gasoline|diesel|lpg)
- `--mileage` - Vehicle mileage (km/L) for fuel cost calculation
- `--lang` - Response language (ko|en|ja|zh)

## Project Structure

```
ncloud-maps/
├── lib/
│   ├── directions.ts      # Directions15 API integration
│   ├── directions5.ts     # Directions5 API integration
│   └── smartDirections.ts # Intelligent routing (auto-select API based on waypoints)
├── scripts/
│   └── index.ts           # CLI entry point
├── references/
│   └── api-spec.md        # Full API documentation
├── SKILL.md               # OpenClaw skill description
├── package.json
├── tsconfig.json
└── .env                   # (local, not in git) API credentials
```

## API Endpoints

- **Directions5**: `https://maps.apigw.ntruss.com/map-direction/v1/driving` (max 5 waypoints)
- **Directions15**: `https://maps.apigw.ntruss.com/map-direction-15/v1/driving` (max 15 waypoints)

## Error Handling

Common errors and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| `좌표 형식 오류` | Invalid coordinate format | Use `longitude,latitude` format (e.g., 127.0683,37.4979) |
| `Authentication Failed` | Invalid API credentials | Verify NCLOUD_API_KEY_ID & NCLOUD_API_KEY |
| `Quota Exceeded` | Rate limit hit | Check Naver Cloud Console quota |
| `No routes found` | Invalid route | Verify start/goal are reachable by car |

## Development

### Install deps
```bash
npm install
```

### Run tests
```bash
npm test
```

### Build
```bash
npm run build
```

### Local development with .env
```bash
cat > .env << EOF
NCLOUD_API_KEY_ID=your-id
NCLOUD_API_KEY=your-key
EOF

npx ts-node scripts/index.ts --start "127.0683,37.4979" --goal "126.9034,37.5087"
```

## API Limits

| API | Waypoints | Auto-Selected When |
|-----|-----------|-------------------|
| **Directions5** | Max 5 | 0-4 waypoints (default, lighter) |
| **Directions15** | Max 15 | 5+ waypoints (auto-upgraded) |
| **Rate Limits** | Per your Naver Cloud plan | Both APIs |

## Limitations

⚠️ **This skill only calculates vehicle (car) routes.** It does not support:
- Public transportation (subway, bus, etc.)
- Walking routes
- Multi-modal journeys
- Transit-specific features (fare, stops, schedules)

For those use cases, use transit-specific APIs (e.g., Kakao Map, Naver Map Transit API).

## Resources

- [Naver Cloud Console](https://console.ncloud.com)
- [Maps Directions API Docs](https://api.ncloud-docs.com/docs/ko/application-maps-directions)
- [OpenClaw Docs](https://docs.openclaw.ai)
- [ClawHub](https://clawhub.com)

## License

MIT - See [LICENSE](LICENSE) file

## Contributing

Pull requests welcome! Please follow existing code style.

## Changelog

### v1.0.8 (2026-02-25)
- **Add OpenClaw skill prompt** - Enable `/skill ncloud-maps` command integration
- Add prompt section to SKILL.md for proper skill recognition
- Document usage with coordinates and addresses

### v1.0.7 (2026-02-25)
- **Add CLI binary support** - Register ncloud-maps command globally
- Enable direct command: `ncloud-maps --start <lon,lat> --goal <lon,lat>`
- Include dist/ directory in npm package
- Update .gitignore to track compiled JavaScript

### v1.0.6 (2026-02-22)
- **Fix axios dependency issues** - Update to latest stable version
- Upgrade axios from 1.6.0 to 1.13.5
- Add @types/axios for TypeScript support
- Resolve runtime axios errors

### v1.0.5 (2026-02-22)
- **Support multiple geocoding skills** - More generic, flexible approach
- Add goplaces and naver-local-search examples
- Allow users to integrate any geocoding service that returns lon,lat
- Update documentation to be provider-agnostic

### v1.0.4 (2026-02-21)
- **Fix TypeScript build** - Add node types to tsconfig.json
- Resolve TS2580 "Cannot find name 'process'" error
- Resolve TS2584 "Cannot find name 'console'" error
- Build process now works correctly

### v1.0.3 (2026-02-21)
- **Add limitations documentation** - Clarify vehicle-only routes
- Document that skill only supports car routes
- Explicitly list unsupported features (public transit, walking, etc.)
- Prevent ambiguous or incorrect suggestions

### v1.0.2 (2026-02-21)
- **Remove all geocoding references** - Complete removal of Geocoding API
- Remove `lib/geocoding.ts` entirely
- Update all code and documentation to coordinates-only API
- Remove geocoding from keywords and package description
- Smart Directions Routing continues to work automatically

### v1.0.1 (2026-02-21)
- **Smart Directions Routing**: Automatically select between Directions5 and Directions15 based on waypoint count
  - 0-4 waypoints: Uses Directions5 (lightweight, optimized)
  - 5+ waypoints: Uses Directions15 (supports up to 15 stops)
- Add `lib/directions5.ts` for Directions5 API support
- Add `lib/smartDirections.ts` for intelligent routing logic
- Update CLI to use smart routing by default
- Update documentation with smart routing examples
- Maintain backward compatibility with explicit `--api` flag

### v1.0.0 (2026-02-21)
- Initial release
- Directions15 API integration
- Waypoints support
- Route options
- Vehicle & fuel settings
