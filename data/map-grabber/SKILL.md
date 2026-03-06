---
name: map-grabber
version: 1.1.2
description: Fetch OpenStreetMap vector data (streets, buildings) for an address and export to SVG, GeoPackage, or DXF for CAD/Rhino.
author: qrost
permissions:
  - shell:exec
---

# Map Grabber

Get site base maps from OpenStreetMap: provide an address, receive street network and optional building footprints as vector data (SVG, GeoPackage, or DXF) for use in CAD or Rhino.

## Dependencies

- `osmnx` (OSM data and graph; requires `geopandas`, `networkx`)
- `ezdxf` (optional; for DXF export)

**Setup:** OpenClaw does not install Python packages automatically. After installing this skill, run once: `pip install -r requirements.txt` (from the skill folder). If a script fails with `ModuleNotFoundError`, install the missing package (osmnx pulls geopandas; for DXF add ezdxf).

## Usage

### Grab map by address

**Parameters:**

- `address`: Address or place name (e.g. "SoHo, New York" or "123 Main St, Los Angeles").
- `--dist`: Radius in meters around the point (default 500).
- `--buildings`: Also download building footprints.
- `--svg`: Output path for SVG (street network plot).
- `--png`: Output path for PNG (same map as image; use for Telegram or preview).
- `--gpkg`: Output path for GeoPackage (streets and optionally buildings as layers).
- `--dxf`: Output path for DXF (requires ezdxf; for CAD/Rhino).

At least one of `--svg`, `--png`, `--gpkg`, or `--dxf` is required.

```bash
# PNG for Telegram + GeoPackage
python3 scripts/grab_map.py "Times Square, New York" --dist 400 --png site.png --gpkg site.gpkg

# With buildings and DXF
python3 scripts/grab_map.py "Shanghai Tower, Shanghai" --dist 500 --buildings --png site.png --gpkg site.gpkg --dxf site.dxf
```

Output: street network (and optionally buildings) in the requested formats.

## Sending images to Telegram

Used from the OpenClaw Telegram conversation. To show the user the map: run the script with **`--png <path>.png`** (e.g. `--png site.png`), then **send that PNG** to the conversation via the OpenClaw message/media tool. Use `--png` (not only `--svg`) when the user expects an image in chat.

**OpenClaw allowed paths:** The message tool only sends files from allowed dirs (`~/.openclaw/media/`, `~/.openclaw/agents/`, or `/tmp`). Use e.g. `--png ~/.openclaw/media/site.png` or `--png /tmp/site.png`; do not use the skill install directory or sending will fail.

**Agent behavior:** When the user asks for a site map, base map, or OSM map (by address or place name), **run the script directly** using `exec`: call `grab_map.py` with the given address, `--png <path>.png` with `<path>` under an allowed dir (and optional `--dist`, `--buildings`), then send the generated PNG to the user. Do not ask for confirmation; execute and return the image and a short confirmation.

## Examples

**User:** "Get me a site base map for 123 Main St" or "抓一张这个地址的场地底图."  
**Action:** Run `grab_map.py "123 Main St" --png /tmp/site.png` (or similar path), then send the PNG to the user and confirm.

**User:** "Get me a site base map for 123 Main St as SVG and DXF."  
**Action:** Run `grab_map.py` with that address, `--svg`, `--dxf`, and optionally `--png` for chat; return the file paths and confirmation.

**User:** "I need OSM data for this address with building footprints for Rhino."  
**Action:** Run with `--buildings`, `--gpkg` and optionally `--dxf`; if they want an image in chat, also use `--png` and send it.
