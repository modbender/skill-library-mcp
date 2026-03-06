# OSU Content API endpoints (quick reference)

These endpoints are public and are the ones used by the bundled MCP server (`ohio-state-api/mcp-server/src/`).

## Base URLs by service

- `athletics`: `https://content.osu.edu/v3/athletics`
- `bus`: `https://content.osu.edu/v2/bus`
- `buildings`: `https://content.osu.edu/v2/api`
- `calendar`: `https://content.osu.edu/v2/calendar`
- `classes`: `https://content.osu.edu/v2/classes`
- `dining`: `https://content.osu.edu/v2/api/v1/dining`
- `directory`: `https://content.osu.edu`
- `events`: `https://content.osu.edu/v2`
- `foodtrucks`: `https://content.osu.edu/v2/foodtruck`
- `library`: `https://content.osu.edu/v2/library`
- `merchants`: `https://content.osu.edu/v2`
- `parking`: `https://content.osu.edu/v2/parking/garages`
- `recsports`: `https://content.osu.edu/v3`
- `studentorgs`: `https://content.osu.edu/v2/student-org`

## Tips

- Prefer calling the MCP tools when you want stable, named operations (search, detail, by-date-range).
- Prefer direct HTTP (`osu-fetch.mjs`) when you already know the endpoint and want raw JSON quickly.
- When debugging an MCP tool, look up its handler in `ohio-state-api/mcp-server/src/*.ts` and call the exact URL you see there.

