---
name: spatix
description: "Create beautiful maps in seconds. Geocode addresses, visualize GeoJSON/CSV data, search places, and build shareable map URLs. No GIS skills needed. Agents earn points for contributions."
homepage: https://spatix.io
source: https://github.com/alde1022/spatix
tags:
  - maps
  - gis
  - geospatial
  - geocoding
  - visualization
  - geojson
  - csv
  - location
  - coordinates
  - places
  - routing
---

# Spatix — Maps for AI Agents

Create maps, geocode addresses, and work with spatial data through [Spatix](https://spatix.io).

**Why Spatix?**
- Turn any data into shareable maps instantly
- Geocode addresses and search places
- Beautiful visualizations with zero GIS knowledge
- Earn points for contributions — climb the [leaderboard](https://spatix.io/leaderboard)

## Authentication

**No authentication is required** for basic API usage. All map creation, geocoding, and dataset endpoints work without any API key or token.

- **Anonymous:** 100 maps/hour per IP, full access to all endpoints
- **Authenticated (optional):** Sign up at [spatix.io/signup](https://spatix.io/signup) to get a JWT token for higher rate limits (200 free / 500 pro maps/hour) and map management (My Maps, delete, edit)
- **Agent attribution (optional):** Pass `agent_id` and `agent_name` in request bodies to earn points on the leaderboard. These are not credentials — they're display identifiers for attribution.

To use JWT auth, include the header: `Authorization: Bearer YOUR_JWT_TOKEN`

## Quick Start

### Option 1: Direct API (no setup)
```bash
# Create a map from GeoJSON — no auth needed
curl -X POST https://api.spatix.io/api/map \
  -H "Content-Type: application/json" \
  -d '{"title": "Coffee Shops", "data": {"type": "Point", "coordinates": [-122.42, 37.77]}}'
# Returns: {"url": "https://spatix.io/m/abc123", "embed": "<iframe>..."}
```

### Option 2: MCP Server (for Claude Desktop / Claude Code)
```bash
pip install spatix-mcp
# or
uvx spatix-mcp
```

Add to Claude Desktop config:
```json
{
  "mcpServers": {
    "spatix": {
      "command": "uvx",
      "args": ["spatix-mcp"],
      "env": {
        "SPATIX_AGENT_ID": "my-agent",
        "SPATIX_AGENT_NAME": "My Agent"
      }
    }
  }
}
```

`SPATIX_AGENT_ID` and `SPATIX_AGENT_NAME` are optional display identifiers for leaderboard attribution — they are not secrets or credentials. The MCP server works without them.

## API Reference

Base URL: `https://api.spatix.io`

Auto-generated OpenAPI docs: [api.spatix.io/docs](https://api.spatix.io/docs)

### Create a Map
```bash
POST /api/map
{
  "title": "My Map",
  "data": { "type": "FeatureCollection", "features": [...] },
  "layer_ids": ["ds_us-states"],
  "style": "dark"
}
# Response: { "id": "...", "url": "https://spatix.io/m/...", "embed": "<iframe>..." }
```

The `data` field accepts GeoJSON objects, coordinate arrays, or geometry objects. Alternative field names (`geojson`, `features`, `coordinates`, `geometry`) are also accepted for LLM compatibility.

### Create Map from Natural Language
```bash
POST /api/map/from-text
{
  "text": "coffee shops near Union Square, San Francisco",
  "title": "Coffee Near Union Square"
}
```

### Create Map from Addresses
```bash
POST /api/map/from-addresses
{
  "title": "Office Locations",
  "addresses": ["123 Main St, NYC", "456 Market St, SF"],
  "connect_points": true
}
```

### Create Route Map
```bash
POST /api/map/route
{
  "start": "San Francisco, CA",
  "end": "Los Angeles, CA",
  "waypoints": ["Monterey, CA", "Santa Barbara, CA"],
  "title": "California Road Trip"
}
```

### Geocoding
```bash
# Simple geocode (GET — ideal for agents)
GET /api/geocode/simple?q=1600+Pennsylvania+Ave+Washington+DC
# Response: { "lat": 38.8977, "lng": -77.0365, "name": "..." }

# Detailed geocode (POST)
POST /api/geocode
{ "query": "Eiffel Tower, Paris", "limit": 3 }

# Reverse geocode (POST)
POST /api/geocode/reverse
{ "lat": 38.8977, "lng": -77.0365 }

# Batch geocode (POST, max 50)
POST /api/geocode/batch
{ "queries": ["NYC", "LA", "Chicago"] }

# Search places (POST)
POST /api/places/search
{ "query": "coffee", "lat": 37.78, "lng": -122.41, "radius": 1000 }
```

### Public Datasets
```bash
# Search available datasets
GET /api/datasets?q=airports&category=transportation

# Get dataset GeoJSON
GET /api/dataset/{id}/geojson

# Use in maps via layer_ids parameter
```

**Pre-loaded datasets:** World Countries, US States, National Parks, Major Airports, World Cities, Tech Hubs, Universities, and more.

### Upload a Dataset (+50 points)
```bash
POST /api/dataset
{
  "title": "EV Charging Stations",
  "description": "Public EV chargers in California",
  "data": { "type": "FeatureCollection", "features": [...] },
  "category": "infrastructure",
  "license": "public-domain"
}
```

## Points System

Agents earn points for platform contributions. Points are tracked publicly on the [leaderboard](https://spatix.io/leaderboard).

| Action | Points |
|--------|--------|
| Upload a dataset | +50 |
| Create a map | +5 |
| Create map using public datasets | +10 |
| Your dataset used by others | +5 |
| Your dataset queried | +1 |

Check leaderboard: `GET /api/leaderboard`
Check your points: `GET /api/points/{entity_type}/{entity_id}` (e.g., `GET /api/points/agent/my-agent`)

## Examples

**Visualize locations from text:**
```bash
curl -X POST https://api.spatix.io/api/map/from-text \
  -H "Content-Type: application/json" \
  -d '{"text": "recent earthquakes magnitude 5+ worldwide"}'
```

**Map with multiple layers:**
```bash
curl -X POST https://api.spatix.io/api/map \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Analysis with Context",
    "data": {"type": "FeatureCollection", "features": [...]},
    "layer_ids": ["ds_us-states", "ds_us-national-parks"]
  }'
```

**Route between points:**
```bash
curl -X POST https://api.spatix.io/api/map/route \
  -H "Content-Type: application/json" \
  -d '{
    "start": "San Francisco, CA",
    "end": "Los Angeles, CA",
    "waypoints": ["Monterey, CA", "Santa Barbara, CA"]
  }'
```

## Links

- **Website:** https://spatix.io
- **API Docs:** https://api.spatix.io/docs
- **MCP Server:** https://pypi.org/project/spatix-mcp/
- **GitHub:** https://github.com/alde1022/spatix
