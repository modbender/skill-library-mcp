---
name: wind-site
version: 1.1.1
description: Wind rose, wind speed/direction at a site; supports site and urban wind assessment (data only; detailed CFD is out of scope).
author: qrost
permissions:
  - shell:exec
---

# Wind & Site

Wind climate and current wind at a location: wind rose (direction and speed frequency) and latest wind conditions. Uses Open-Meteo (no API key). For detailed **urban or building wind effects** (pedestrian comfort, corner acceleration), use CFD tools; this skill provides the **site wind data** needed for context and input to such studies.

## Dependencies

- `requests`
- `numpy`
- `matplotlib`

**Setup:** OpenClaw does not install Python packages automatically. After installing this skill, run once: `pip install -r requirements.txt` (from the skill folder). If a script fails with `ModuleNotFoundError`, install the missing package.

## Usage

### 1. Current or recent wind

**Parameters:** `--lat`, `--lon`, optional `--days` (0 = current from forecast; >0 = last N days from archive).

```bash
python3 scripts/wind_info.py --lat 31.23 --lon 121.47
python3 scripts/wind_info.py --lat 34.05 --lon -118.24 --days 7
```

Output: latest wind speed (m/s) and direction (°), and period mean if multiple hours.

### 2. Wind rose

**Parameters:** `--lat`, `--lon`, `--days` (default 30), `--output` (default `wind_rose.png`).

```bash
python3 scripts/wind_rose.py --lat 31.23 --lon 121.47 --days 30 --output wind_rose.png
```

Fetches hourly wind from Open-Meteo historical API and plots a wind rose (% of hours by direction and speed bins).

## Sending images to Telegram

Used from the OpenClaw Telegram conversation. The wind rose is an image: run `wind_rose.py` with `--output <path>.png`. Then **send that PNG** to the user via the OpenClaw message/media tool. `wind_info.py` is text-only; use it for numbers and use the wind rose image for the visual.

**OpenClaw allowed paths:** The message tool can only send files from allowed directories. If you see "Local media path is not under an allowed directory", the image was saved outside them. **Always use an allowed output path** for the PNG:

- `~/.openclaw/media/` (e.g. `--output ~/.openclaw/media/wind_rose.png`)
- `~/.openclaw/agents/`
- The system temp dir (e.g. `/tmp/wind_rose.png`)

Do **not** use the skill install directory (e.g. `~/.openclaw/skills/windsite/`) as `--output`; that path is not allowed and sending will fail.

**Agent behavior:** When the user asks for wind at a site or a wind rose (with location or lat/lon), **run the script directly** with `exec`: use `wind_info.py` for current/recent wind text, and `wind_rose.py --output <path>.png` for the diagram, where `<path>` must be under an allowed directory (e.g. `~/.openclaw/media/wind_rose.png` or `/tmp/wind_rose.png`); then send the wind rose PNG and summarize the numbers. Do not ask for confirmation; execute and return the image and data.

## Urban wind effect

This skill does **not** run CFD or pedestrian wind simulation. It provides:

- **Wind rose** and **wind speed/direction** for the site, so you can see prevailing wind and strength.
- Use that data as input to CFD or specialist tools (e.g. SimScale, OpenFOAM, or wind-tunnel studies) for building/urban wind effects and comfort.

## Examples

**User:** "What's the wind like at this site?"  
**Action:** Run `wind_info.py` for the site lat/lon; return speed, direction, and brief interpretation.

**User:** "Give me a wind rose for Shanghai for the last 30 days."  
**Action:** Run `wind_rose.py --lat 31.23 --lon 121.47 --days 30 --output ~/.openclaw/media/wind_rose.png` (or `/tmp/wind_rose.png`); send that file and return a short summary.

**User:** "I need to assess urban wind around a new tower."  
**Action:** Run wind_rose and wind_info for the site; explain that for building/urban effects they should use CFD or wind-tunnel studies, with this data as climate input.
