---
name: gaode_map
description: A skill to interact with Gaode Map (AMap) for location search and route planning.
metadata:
  openclaw:
    requires:
      env: ["AMAP_API_KEY"]
      bins: ["python"]
---

# Gaode Map Skill

This skill allows you to search for places and plan routes using Gaode Map (AMap) API.

## Usage

You can use the `amap_tool.py` script to perform actions. The API Key is expected to be in the `AMAP_API_KEY` environment variable.

### Place Search
Search for POIs (Points of Interest).

**Command:**
```bash
python amap_tool.py search --keywords "<keywords>" [--city "<city>"]
```

**Parameters:**
- `keywords`: The search query (e.g., "restaurants", "gas station").
- `city`: (Optional) The city to search in.

### Route Planning
Plan a route between two locations.

**Command:**
```bash
python amap_tool.py route --origin "<origin>" --destination "<destination>" [--mode "<mode>"] [--city "<city>"]
```

**Parameters:**
- `origin`: Start location (address or coordinates "lon,lat").
- `destination`: End location (address or coordinates "lon,lat").
- `mode`: (Optional) Route mode: `driving` (default), `walking`, `bicycling`, `transit`.
- `city`: (Optional) City name (required for `transit` mode, or to help geocoding).

## Examples

**User:** "Find coffee shops in Shanghai."
**Action:**
```bash
python amap_tool.py search --keywords "coffee shop" --city "Shanghai"
```

**User:** "Show me the driving route from Beijing West Station to the Forbidden City."
**Action:**
```bash
python amap_tool.py route --origin "Beijing West Station" --destination "Forbidden City" --mode "driving" --city "Beijing"
```
