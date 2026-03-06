---
name: terrain-route-video
description: Generate a minimalist terrain-style animated driving route video (MP4) from a list of stops (cities/POIs) without Remotion. Uses OSRM for road-following geometry, OpenTopoMap terrain tiles for basemap, Matplotlib for frame rendering, and FFmpeg for encoding. Use when the user asks to create/export a dynamic self-driving route map video (fly-follow camera, route draw animation, labels) and wants it along roads/highways.
---

# Terrain Route Video (no Remotion)

## Output defaults (recommended)

- Size: `1600x900`
- FPS: `30`
- Duration: `12s`
- Style: dark terrain basemap + red route line + cyan head dot

## Inputs

### Option A) Road-follow (OSRM) via `stops.json`

Create a `stops.json` file:

```json
{
  "stops": [
    {"id": "01", "name": "襄阳", "lon": 112.1163785, "lat": 32.0109980},
    {"id": "02", "name": "老河口", "lon": 111.7575073, "lat": 32.4370526}
  ]
}
```

Schema reference: `references/stops.schema.json`.

### Option B) Track-follow via `.gpx` / `.kml`

If you already have a route track (GPX/KML), you can generate the video **directly from the track geometry** (no OSRM calls):

- GPX: uses `<trkpt>` (track points) or falls back to `<rtept>`
- KML: supports both:
  - standard `<LineString><coordinates>`
  - 2bulu/Google-style `<gx:Track><gx:coord>` (common in hiking app exports)

## Runbook

1) Create a fresh working folder (keeps caches + frames local).

2) Create a Python venv and install deps:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install numpy matplotlib pillow requests
```

3) Render video (choose one):

**OSRM road-follow mode (`stops.json`)**
```bash
python /path/to/skills/terrain-route-video/scripts/terrain_route_video.py \
  --stops stops.json \
  --out out.mp4 \
  --size 1600x900 \
  --fps 30 --duration 12 \
  --title "江汉平原到洞庭湖 · 足迹" \
  --subtitle "襄阳 → 老河口 → 荆州 → 监利 → 洪湖·峰口镇 → 岳阳"
```

**GPX/KML track mode**
```bash
python /path/to/skills/terrain-route-video/scripts/terrain_route_video.py \
  --route my-track.gpx \
  --out out.mp4 \
  --size 1600x900 \
  --fps 30 --duration 12 \
  --title "My Trip" \
  --subtitle "GPX/KML track"
```

Notes:
- The script creates `frames/` and `.tile-cache/` in the current folder.
- If the user complains the line is not “hugging highways”, keep **full OSRM geometry** (default) and avoid any simplification.
- If text shows missing glyphs, pass `--font /System/Library/Fonts/Hiragino Sans GB.ttc` (default) or another CJK font path.
- OpenTopoMap tile availability can vary by zoom/region/network. The script will auto-fallback to a lower zoom if tile requests fail.

## Useful tuning flags

### Camera / route

- `--zoom 18` (terrain tile zoom; default is 18; may auto-fallback if tiles fail)
- `--lookahead 0.02` (camera looks ahead on the route; smaller = steadier)
- `--dwell 0` (pause frames at each stop; default 0)
- `--no-follow` (static full-route view, no fly-follow)

### Basemap readability (new)

These are useful when map labels feel too dark/washed out.

- `--basemap-alpha 0.85` (make basemap more visible)
- `--overlay-alpha 0.25` (reduce the dark overlay; clearer labels)
- `--basemap-contrast 1.20` (increase contrast)
- `--basemap-sharpness 1.45` (sharpen text/lines)
- `--basemap-color 0.80` (saturation multiplier)
