# Geomanic — OpenClaw Skill

Connect [OpenClaw](https://www.getopenclaw.ai) to [Geomanic](https://geomanic.com), your privacy-first GPS tracking platform.

## What you can do

- **Query travel statistics** — distances, speeds, altitudes, country breakdown
- **Manage waypoints** — create, update, delete, list, and search GPS waypoints
- **Analyze journeys** — ask natural language questions about your travel data

## Setup

### 1. Get your API key

Go to [geomanic.com/data](https://geomanic.com/data) and generate an MCP API key in the "MCP Integration" tile.

### 2. Install the skill

```
/skills install @weltspion/geomanic
```

### 3. Configure

Set your API key:

```
/secrets set GEOMANIC_TOKEN gmnc_mcp_your_key_here
```

Or configure in `openclaw.json`:

```json
{
  "skills": {
    "@weltspion/geomanic": {
      "enabled": true,
      "config": {
        "apiKey": "${GEOMANIC_TOKEN}"
      }
    }
  }
}
```

## Available tools

| Tool | Description |
|------|-------------|
| `create_waypoint` | Create a new GPS waypoint |
| `update_waypoint` | Update an existing waypoint by ID |
| `delete_waypoint` | Delete a waypoint by ID |
| `get_waypoint` | Get a single waypoint by ID |
| `list_waypoints` | List waypoints with time range, pagination, sorting |
| `get_statistics` | Aggregated stats: distance, speed, altitude, country breakdown |
| `get_date_range` | Earliest and latest waypoint dates |

## Example prompts

- "How many countries have I visited this year?"
- "What was my total distance in January?"
- "Show me my last 10 waypoints"
- "How many days did I spend in Germany in 2025?"

## Security

- Your API key is stored locally and never shared
- All data stays on your Geomanic account
- Revoke and regenerate keys anytime at [geomanic.com/data](https://geomanic.com/data)

## Links

- [Geomanic](https://geomanic.com) — GPS tracking platform
- [MCP Bridge repo](https://github.com/monswyk/geomanic-mcp) — Bridge and configs for Claude Desktop, Cursor, and other MCP clients
