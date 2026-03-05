# Low-token guide protocol (Telegram)

Route ID used in examples: `qiniangshan_jinghua`

## Route acquisition
- Preferred: user exports/sends GPX/KML via Telegram → deterministic parsing.
- Optional: user manually logs in to 2bulu in a persistent browser profile; automation may assist after login (no bypass).

## Commands
- `/use <routeId>` bind route to current chat.
- `/g` guide once. Location-only message may be treated as `/g`.

## Output (2-4 lines)
Line 1 (machine):
`G S:<0|1|2> D:<m> B:<deg><dir> GO:<m> IDX:<n>`

- S: 0=on_route, 1=off_route, 2=arrived
- D: distance to route (m)
- B: bearing degrees + dir (N/NE/E/SE/S/SW/W/NW)
- GO: recommended distance (m) to rejoin/advance
- IDX: nearest point index (for incremental window search)

Line 2 (Chinese template, deterministic):
- on_route: `在路线内（偏离{D}米）。朝{dir}（{B}°）前进约{GO}米。`
- off_route: `你已偏离路线约{D}米。请朝{dir}（{B}°）走约{GO}米回到路线。`
- arrived: `你已接近终点（{D}米内）。建议在此附近确认营地/下撤方向。`

Line 3 (optional alert, if near a key node):
`ALERT <letter>: <message>`

Line 4 (optional weather alert, if enabled and sharp change detected):
`WX ALERT: <CODE> <brief>`

## Defaults
- toleranceM=50
- arrivedM=60
- lookaheadM=120
- bboxGuardM=2000 (if far from bbox, return E:OUT_OF_BBOX)

## Reference implementation
- `scripts/guide_route.js`: given a GeoJSON LineString + (lat,lon) (+ optional lastIdx), prints the 2-3 line response.
  - Add `--alerts references/<route>_alerts.json` to enable key-node alerts.
  - Add `--state /tmp/guide_state.json --cooldown-sec 1800` to dedupe alerts.

## Errors (single line)
- `E:NO_ROUTE`
- `E:OUT_OF_BBOX`
- `E:GPS_BAD`
