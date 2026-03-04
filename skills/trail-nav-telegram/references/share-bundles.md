# Share routes (outsideclaw bundles)

Goal: share a route (and optional alerts) with another person's outsideclaw agent without relying on external platforms.

## Bundle format
- `.tar.gz` containing:
  - `manifest.json` (kind: `outsideclaw.route.bundle`)
  - `route.geojson`
  - `routepack.json`
  - `meta.json`
  - optional `alerts.json`

## outsideclaw CLI workflow
Create bundle (sender):
```bash
npm run share:route -- <routeId> [--alerts /path/to/alerts.json]
```

Import bundle (receiver):
```bash
npm run import:bundle -- /path/to/outsideclaw-route-<routeId>-*.tar.gz
```

## Telegram workflow (planned)
- `/share <routeId>` → bot replies with the `.tar.gz` file
- Receiver forwards the file to their bot → bot auto-imports and replies with `/use <routeId>` instructions

Security notes:
- Validate `manifest.json.kind` before importing.
- Extract only into a controlled directory.
