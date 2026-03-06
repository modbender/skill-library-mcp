# Earl Display Control

Earl is a house guardian AI whose mind lives on the living room TV. This project powers that display — a full-screen kiosk dashboard called the **VisuoSpatial Sketchpad** that shows Earl's mood, thoughts, household tasks, hot takes, and hand-drawn doodles in real time.

## What It Looks Like

The TV displays a warm, wood-grain-textured dashboard with three main panels:

- **Earl's Sketchpad** — a cork board filled with doodles, sticky notes, and emoji markers
- **Important House Stuff** — a priority-coded task list for household reminders (bins night, errands, etc.)
- **Earl Unplugged** — Earl's hot takes on life, rated by heat level

A header bar shows Earl's current mood, energy level, live weather with a 3-day forecast, and whatever's on his mind right now. A footer tracks long-term patterns he's noticed around the house.

The display refreshes every 5 seconds from a local JSON file, so updates appear almost immediately.

## How It Works

Everything runs locally on the machine connected to the TV:

1. A simple Python HTTP server (`python -m http.server 8000`) serves the dashboard
2. Microsoft Edge runs in kiosk mode pointing at `http://localhost:8000/sketchpad.html`
3. The dashboard reads `earl_mind.json` — a JSON file that holds Earl's entire mental state
4. AI agents (or helper scripts) update that JSON file through a Python API

### The Python API

The `EarlMind` class in `earl_api.py` provides methods for updating every part of Earl's state:

```python
from earl_api import EarlMind

mind = EarlMind()

# Set Earl's mood and energy
mind.set_mood("happy", energy=0.9, vibe="Just noticed the sunset...")

# Post a household reminder
mind.post_house_stuff(
    title="Bins go out tonight",
    detail="It's Wednesday again.",
    priority="high",
    category="chores",
    icon="🗑️"
)

# Share a hot take
mind.hot_take("Pineapple on pizza", "Controversial but I respect the audacity", heat=0.6, emoji="🍕")

# Drop a doodle on the sketchpad
mind.doodle("🌧️", x=0.3, y=0.2, size=30, note="Rain starting")

# Log a long-term pattern
mind.learn_pattern("The cat sits by the window at 3pm", confidence=0.7, observations=5)

# Persist changes to disk
mind.save()
```

### Helper Scripts

| Script | What it does |
| --- | --- |
| `update_weather_ping.py` | Fetches live weather from Open-Meteo and updates Earl's mood + sketchpad |
| `update_vibe.py` | Changes Earl's current vibe message |
| `update_house_stuff.py` | Adds tasks to the Important House Stuff board |
| `reorder_take.py` | Reorders Earl's hot takes |
| `remove_noise_take.py` | Removes a specific hot take |
| `update_mind.py` | General-purpose helper for updating the mind state |

All scripts live in the `VisuoSpatialSketchpad/` directory.

## Getting Started

### Prerequisites

- Python 3
- A browser with kiosk/fullscreen support (Chrome, Edge, or Chromium recommended)

### Setup

1. Clone this repo
2. Copy the template state file to create your live state:
   ```bash
   cp VisuoSpatialSketchpad/earl_mind.template.json VisuoSpatialSketchpad/earl_mind.json
   ```
3. Configure your location in `earl_mind.json` — edit the `spatial_awareness` section:
   ```json
   "spatial_awareness": {
     "house_name": "My House",
     "location": {
       "latitude": 40.7128,
       "longitude": -74.0060,
       "timezone": "America/New_York",
       "temperature_unit": "fahrenheit",
       "wind_speed_unit": "mph"
     }
   }
   ```
   Set `latitude` and `longitude` to your coordinates for live weather. Leave them at `0.0` to disable weather.
4. Start the server:
   ```bash
   cd VisuoSpatialSketchpad
   python -m http.server 8000
   ```
5. Open the dashboard in a browser at `http://localhost:8000/sketchpad.html`, or launch a full-screen kiosk:

   **macOS:**
   ```bash
   open -a "Google Chrome" --args --kiosk http://localhost:8000/sketchpad.html
   ```
   **Windows:**
   ```powershell
   Start-Process msedge.exe '--kiosk http://localhost:8000/sketchpad.html --edge-kiosk-type=fullscreen'
   ```
   **Linux:**
   ```bash
   chromium-browser --kiosk http://localhost:8000/sketchpad.html
   ```

Earl's TV is now live. Update `earl_mind.json` (directly or via the API) and the display will pick up changes within seconds.

## Project Structure

```
earl-display-control/
├── VisuoSpatialSketchpad/
│   ├── sketchpad.html              # The TV dashboard UI
│   ├── earl_api.py                  # Python API for updating Earl's state
│   ├── earl_mind.template.json      # Starter state (copy to earl_mind.json)
│   ├── update_weather_ping.py       # Weather updater
│   ├── update_vibe.py               # Vibe message updater
│   ├── update_house_stuff.py        # House task updater
│   ├── reorder_take.py              # Hot take reorderer
│   ├── remove_noise_take.py         # Hot take remover
│   └── update_mind.py               # General state updater
├── skills/earl-display-control/
│   └── SKILL.md                     # Skill definition (source copy)
├── SKILL.md                         # Skill definition (ClawHub root)
└── README.md
```

## OpenClaw Skill

This project includes an [OpenClaw](https://github.com/anthropics/claude-code) skill that lets AI agents manage the display. The skill works on macOS, Windows, and Linux.

### Install from ClawHub

```bash
openclaw skill install earl-display-control
```

### Install manually

Copy the skill directory into your OpenClaw skills folder:

```bash
# macOS / Linux
cp -r skills/earl-display-control ~/.openclaw/skills/

# Windows (PowerShell)
Copy-Item -Recurse skills\earl-display-control $env:USERPROFILE\.openclaw\skills\
```

Once installed, the skill is available as `/earl-display-control` in any Claude Code session. It requires `python3` on your PATH.

## Privacy

The live `earl_mind.json` file is gitignored and never pushed to the repository — it contains real household state. Only the sanitized template (`earl_mind.template.json`) is included in source control.
