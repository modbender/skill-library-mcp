# Route alerts (key nodes) — schema + usage

Goal: add **route-specific key-node reminders** (hazards / ridge / descent start / water / campsite) with **low-token** output.

## Files
- Alerts config: `references/<routeId>_alerts.json` (example: `qiniangshan_alerts.json`)
- Guide script: `scripts/guide_route.js`

## Alerts JSON schema (minimal)
```json
{
  "routeId": "your_route_id",
  "routeName": "Human name",
  "match": { "radiusM": 120 },
  "nodes": [
    {
      "id": "unique-node-id",
      "letter": "A",
      "kind": "hazard|trailhead|summit_or_ridge|descent|finish|water|campsite|node",
      "name": "Label shown on map",
      "lat": 0,
      "lon": 0,
      "message": "Chinese reminder text"
    }
  ]
}
```

Notes:
- `match.radiusM` is the trigger radius.
- `letter` is used in `ALERT <letter>:` output and for map labels.
- Add as many nodes as you want; keep messages short.

## Using alerts with guide_route
`guide_route.js` prints the standard 2-line guide output, and optionally a 3rd line:

- `ALERT <letter>: <message>`

Example:
```bash
node scripts/guide_route.js route.geojson 22.53 114.52 123 \
  --alerts references/qiniangshan_alerts.json \
  --state out/alert_state.json \
  --cooldown-sec 900
```

## Cooldown (anti-spam)
- Use `--state <path>` to persist per-node last-trigger timestamps.
- Use `--cooldown-sec <n>` (default recommended: 900s).

## Rendering annotated map
Use `scripts/render_route_map_annotated.js` with the same alerts JSON.
