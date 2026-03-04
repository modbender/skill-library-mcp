---
name: earl-display-control
description: >-
  Manage Earl's TV dashboard (VisuoSpatial Sketchpad) — wake the display,
  restart the local server, launch the kiosk browser, and update Earl's mind
  (mood, house stuff, hot takes, sketchpad doodles, weather). Use when asked to
  "wake Earl", "update the TV", "post house stuff", "add a hot take",
  "refresh the dashboard", "update Earl's mood", or when the display shows
  "Earl is sleeping" / "Could not sync".
metadata:
  openclaw:
    emoji: "📺"
    os: [darwin, win32, linux]
    requires:
      bins: [python3]
  homepage: https://github.com/recozers/earl-display-control
---

# Earl Display Control

Skill for managing the VisuoSpatial Sketchpad — Earl's living-room TV dashboard. This covers starting the HTTP server, launching the kiosk browser, and updating `earl_mind.json` via the Python API.

All file paths below use `{baseDir}` to mean this skill's root directory (the repo root containing `VisuoSpatialSketchpad/`).

## Quick Response Checklist

1. **Wake requests** ("Earl wake up", "Could not sync", "Earl is sleeping")
   - Start the local server (see [Server Management](#server-management))
   - Launch the kiosk browser (see [Launching the Kiosk](#launching-the-kiosk))
   - Confirm health: watch for `GET /earl_mind.json ... 200` in the server log
2. **Content updates** (mood, house stuff, hot takes, doodles, weather)
   - Use the `EarlMind` API from `{baseDir}/VisuoSpatialSketchpad/earl_api.py`
   - Relaunch the kiosk after changes if the display looks stale

## Server Management

Start the HTTP server from the `VisuoSpatialSketchpad` directory:

```bash
cd {baseDir}/VisuoSpatialSketchpad && python3 -m http.server 8000
```

Background the process so the shell prompt returns.

### Killing a stuck server

**macOS / Linux:**
```bash
lsof -ti:8000 | xargs kill -9
```

**Windows (PowerShell):**
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```

## Launching the Kiosk

**macOS:**
```bash
open -a "Google Chrome" --args --kiosk http://localhost:8000/sketchpad.html
```
If Chrome is unavailable, Safari works too:
```bash
open -a Safari http://localhost:8000/sketchpad.html
```

**Windows (PowerShell):**
```powershell
Start-Process msedge.exe '--kiosk http://localhost:8000/sketchpad.html --edge-kiosk-type=fullscreen'
```

**Linux:**
```bash
xdg-open http://localhost:8000/sketchpad.html
```
Or for a true kiosk with Chromium:
```bash
chromium-browser --kiosk http://localhost:8000/sketchpad.html
```

Always relaunch after a wake cycle — the browser may cache the old page.

## EarlMind API Reference

All methods live in `{baseDir}/VisuoSpatialSketchpad/earl_api.py`. Run from the `VisuoSpatialSketchpad` directory:

```python
from earl_api import EarlMind
mind = EarlMind()
```

Each mutating method auto-saves and bumps `meta.last_updated` / `meta.update_count`.

### Method Reference

| Method | Purpose | Key Parameters |
|--------|---------|----------------|
| `set_mood(mood, energy, vibe, expression)` | Set Earl's mood and inner monologue | `mood`: str, `energy`: 0-1 float, `vibe`: str, `expression`: str |
| `set_photo(url, caption)` | Set Earl's header photo | `url`: str (URL or local path), `caption`: str |
| `post_house_stuff(title, detail, priority, category, icon)` | Add a household reminder | `priority`: "high"/"medium"/"low", `icon`: emoji str |
| `resolve_house_stuff(item_id)` | Remove a resolved item by ID | `item_id`: str (e.g. "hs_a1b2c3") |
| `clear_house_stuff()` | Clear all house stuff items | — |
| `update_room(room_id, status, notes, attention)` | Update a room's state | `attention`: 0-1 float |
| `add_room(room_id, name, x, y, icon, status, notes, attention)` | Add a new room | `x`, `y`: 0-1 normalized position |
| `sweep()` | Log a full house sweep | — |
| `hot_take(topic, take, heat, emoji)` | Add or update a hot take | `heat`: 0-1 float, updates if topic exists |
| `drop_take(topic)` | Remove a hot take by topic | — |
| `doodle(label, x, y, size, color, note)` | Place an emoji doodle on the sketchpad | `x`, `y`: 0-1, `size`: px, `color`: hex |
| `sketch_note(text, x, y, size, color)` | Place a text note on the sketchpad | Same as doodle |
| `clear_sketchpad()` | Wipe the sketchpad clean | — |
| `learn_pattern(pattern, confidence, observations)` | Record a long-term pattern | `confidence`: 0-1, `observations`: int |
| `summary()` | Get a human-readable state summary | Returns str |
| `snapshot()` | Get the raw mind dict | Returns dict |

### Common Examples

```python
# Set mood
mind.set_mood("happy", energy=0.9, vibe="Sun's out, vibes are immaculate.")

# Post a house reminder
mind.post_house_stuff("Bins go out tonight", detail="Wednesday again.", priority="high", category="chores", icon="🗑️")

# Drop a hot take
mind.hot_take("Pineapple on pizza", "Controversial but I respect the audacity.", heat=0.6, emoji="🍕")

# Doodle on the sketchpad
mind.doodle("🌧️", x=0.3, y=0.2, size=30, note="Rain starting")

# Log a pattern
mind.learn_pattern("The cat sits by the window at 3pm", confidence=0.7, observations=5)
```

### Weather Update

Run the weather helper to fetch live Open-Meteo data, update mood/energy, and drop a weather doodle:

```bash
cd {baseDir}/VisuoSpatialSketchpad && python3 update_weather_ping.py
```

## earl_mind.json Schema

The dashboard reads `{baseDir}/VisuoSpatialSketchpad/earl_mind.json`. Top-level structure:

```
{
  "identity":          { name, role, mood, energy (0-1), current_vibe, avatar_expression, photo, photo_caption }
  "spatial_awareness": { house_name, location: { latitude, longitude, timezone, temperature_unit, wind_speed_unit }, last_sweep, rooms: [...] }
  "house_stuff":       { items: [{ id, title, detail, priority, category, icon }] }
  "earl_unplugged":    [{ id, topic, take, heat (0-1), emoji, date }]
  "sketchpad":         { canvas: [{ id, type ("doodle"|"note"), label, x, y, size, color, note }] }
  "long_term_patterns": [{ pattern, confidence (0-1), observations }]
  "meta":              { schema_version, last_updated (ISO 8601), update_count }
}
```

If you edit JSON directly, always bump `meta.last_updated` and `meta.update_count`, and write with `ensure_ascii=False, indent=2`.

## Troubleshooting

- **Server keeps dying** — Check for duplicate python processes. On macOS/Linux: `lsof -i:8000`. On Windows: `Get-Process python`.
- **Browser won't go fullscreen** — Kill stray browser processes first. macOS: `pkill -f "Google Chrome"`. Windows: `taskkill /IM msedge.exe /F`.
- **Content not updating** — Relaunch the kiosk to bust any cache. Verify the JSON saved correctly.
- **Weather not working** — Check that `spatial_awareness.location.latitude` and `longitude` are set (not 0.0) in `earl_mind.json`.
- **Import error** — Make sure you run Python from the `VisuoSpatialSketchpad` directory, or add it to `sys.path`.

## Tight Loop

Restart server -> launch kiosk -> apply content changes -> relaunch kiosk if needed. Follow this every time the house texts "wake up".
