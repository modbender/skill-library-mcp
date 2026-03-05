# outsideclaw integration (via trail-nav-telegram skill)

Goal: keep outsideclaw as the full repo/CLI, but make it easy to import into OpenClaw.

## 1) Install/update outsideclaw repo
Run:
```bash
bash scripts/outsideclaw_setup.sh
```

Default install location:
- `~/.outsideclaw/app/outsideclaw`

This also runs:
- `npm install`
- `npm run setup` (creates DB + routes dirs)

## 2) Generate OpenClaw config snippet
```bash
node scripts/generate_openclaw_snippet.js
```

Copy the JSON snippet into your OpenClaw config's `skills` list.

## 3) Use outsideclaw CLI
Once installed:
```bash
cd ~/.outsideclaw/app/outsideclaw
npm run setup
npm run import:kml -- /path/to/route.kml
npm run import:gpx -- /path/to/route.gpx
npm run guide -- <routeId> <lat> <lon> --wx on --mode day_hike
```

Notes:
- outsideclaw is local-first (DB defaults to `~/.outsideclaw/outsideclaw.sqlite`).
- Do not bypass external site login/captcha.
