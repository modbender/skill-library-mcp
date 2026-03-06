# NavClaw Technical Documentation

> Version 0.1 | Currently supported navigation platform: Amap (Gaode)

## 1. Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  config.py  │────▶│  navclaw.py  │◀────│  wrapper.py  │
│  User Config │     │  Core Engine  │     │  Platform    │
└─────────────┘     └──────┬───────┘     └──────────────┘
                           │
                    ┌──────▼───────┐
                    │  Amap API    │
                    │  geocode +   │
                    │  driving v5  │
                    └──────────────┘
```

**Data flow**: config.py → PlannerConfig → RoutePlanner.run() → 3 messages + log file

## 2. Five-Phase Pipeline

### Phase 1: 🟢 Broad Search

Concurrently queries multiple routing strategies to gather as many candidate routes as possible.

- Calls Amap driving route API for each strategy in `BASELINES`
- v5 API returns up to 3 routes per call, v3 returns 1
- Default 6 strategies → ~16 raw routes

**Diversity analysis**: Uses a `(distance, duration, highway_distance)` fingerprint to identify unique routes and detect cross-strategy duplicates.

### Phase 2: 🟡 Smart Filter

Selects diverse seed routes from Phase 1 results.

1. **Deduplication**: Routes with identical fingerprints — keep only the fastest
2. **Similarity removal**: Routes with duration difference < `SIMILAR_DUR_THRESHOLD` and congestion length difference < `SIMILAR_RED_THRESHOLD` are considered similar
3. **Top Y selection**: Keep top `PHASE2_TOP_Y` routes
4. **Non-highway protection**: Retain at least `NOHW_PROTECT` non-highway routes

### Phase 3: 🔴 Deep Optimization

Identifies congestion segments on seed routes and generates bypass alternatives.

#### Congestion Detection

```
TMC data → Filter (status ∈ CONGESTION_STATUSES AND length ≥ MIN_RED_LEN)
         → First merge (gap < MERGE_GAP)
         → Second merge (gap < BYPASS_MERGE_GAP)
         → Final congestion segments
```

#### Bypass Generation

For each congestion segment:
1. Extract waypoints at 33%/67% positions from the corresponding section on the non-highway reference route (s1)
2. Combine waypoints across different congestion segments (single-segment bypass, multi-segment bypass)
3. Query routes with waypoints using strategies from `BYPASS_STRATEGIES`

### Phase 4: 🔄 Iterative Optimization

Further optimizes the best bypass routes from Phase 3.

1. Select top `ITER_CANDIDATES` bypass routes by duration
2. Re-identify congestion segments on each
3. Append new waypoints to existing ones
4. Re-query routes

### Phase 5: ⚓ Route Anchoring

Pins routes using waypoints to ensure the navigation app follows the planned path when the user opens the deep link.

- Sample `ANCHOR_COUNT` evenly-spaced anchor points along the route polyline
- Re-query route using these anchors as waypoints
- Compare pre/post-anchoring duration drift, keep the best version

## 3. API Usage

### Geocode

```
GET https://restapi.amap.com/v3/geocode/geo
Parameters: address, key, city (optional)
```

Fault tolerance: When the address contains parentheses, automatically tries 3 variants (original / remove parentheses keep content / remove parentheses and content).

### Driving Route Planning

```
GET https://restapi.amap.com/v5/direction/driving
Parameters: origin, destination, strategy, show_fields, key
Optional: waypoints (up to 16)
```

v5 API strategy codes:

| Code | Name | Code | Name |
|------|------|------|------|
| 32 | Default recommended | 33 | Avoid congestion |
| 34 | Highway preferred | 35 | No highway |
| 36 | Least toll | 37 | Main roads preferred |
| 38 | Fastest speed | 39 | Avoid congestion + highway |
| 40 | Avoid congestion + no highway | 41 | Avoid congestion + least toll |
| 42 | Least toll + no highway | 43 | Avoid congestion + least toll + no highway |
| 44 | Avoid congestion + main roads | 45 | Avoid congestion + fastest |

v3 API (legacy compatibility):

| Code | Name |
|------|------|
| 0 | Speed priority |
| 1 | No highway |
| 2 | Least cost |
| 3 | Shortest distance |

## 4. Configuration Parameters

### General

| Parameter | Default | Description |
|-----------|---------|-------------|
| `API_KEY` | (required) | Amap Web Service API key |
| `DEFAULT_ORIGIN` | Beijing South Station | Default origin |
| `DEFAULT_DEST` | Guangzhou South Station | Default destination |
| `HOME_KEYWORD` | 家 (home) | Destination shortcut, equivalent to DEFAULT_DEST |

### Strategy

| Parameter | Default | Description |
|-----------|---------|-------------|
| `BASELINES` | [32,36,38,39,35,1] | Phase 1 baseline strategies |
| `BYPASS_STRATEGIES` | [35,33] | Phase 3 bypass strategies |
| `BASELINE_HW_STRAT` | 39 | Highway baseline strategy |

### Congestion Definition

| Parameter | Default | Description |
|-----------|---------|-------------|
| `CONGESTION_STATUSES` | (congested, severely congested) | TMC statuses counted as "congested" |
| `MIN_RED_LEN` | 1000m | Minimum single-segment congestion length |
| `MERGE_GAP` | 3000m | Highway congestion merge gap |
| `MERGE_GAP_NOHW` | 1000m | Non-highway merge gap |
| `BYPASS_MERGE_GAP` | 10000m | Secondary merge gap |

### Algorithm

| Parameter | Default | Description |
|-----------|---------|-------------|
| `PHASE2_TOP_Y` | 5 | Number of routes kept after smart filter |
| `MAX_ITER` | 1 | Iteration rounds (0 = disabled) |
| `ANCHOR_COUNT` | 10 | Number of anchoring waypoints |
| `API_MAX_WP` | 16 | Max waypoints per API call |

### Mattermost

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MM_BASEURL` | (empty) | Mattermost server URL |
| `MM_BOT_TOKEN` | (empty) | Bot token |
| `MM_CHANNEL_ID` | (empty) | Target channel ID |

## 5. Highway Toll-Free Periods

Built-in toll-free calendar for 2026–2036 (Chinese Spring Festival, Qingming, Labor Day, National Day). For reference only.

**Actual toll amounts are based on API responses.** During toll-free periods, displays `¥387 (toll-free)`. On first/last day, displays `¥387 (possibly toll-free)`.

Toll-free period definitions:
- Spring Festival: New Year's Eve 00:00 ~ Day 7 24:00 (8 days)
- Qingming: April 3 – April 6
- Labor Day: May 1 – May 5
- National Day: October 1 – October 7

## 6. Typical API Call Volume

| Scenario | Phase 1 | Phase 3 | Phase 4 | Phase 5 | Total |
|----------|---------|---------|---------|---------|-------|
| No congestion (e.g. Suzhou→Nanjing) | ~6 | 0 | 0 | ~7 | ~15 |
| Some congestion (long trip) | ~6 | ~12 | ~4 | ~9 | ~35 |
| Heavy congestion (multiple segments) | ~6 | ~20 | ~6 | ~12 | ~50 |

## License

[Apache License 2.0](LICENSE)
🌐 [NavClaw.com](https://navclaw.com) (Reserved for NavClaw GitHub Page — redirect only, non-commercial)
Email: nuaa02@gmail.com