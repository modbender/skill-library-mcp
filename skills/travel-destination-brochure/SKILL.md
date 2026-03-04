---
name: travel-destination-brochure
description: "Build travel destination scenarios and brochures from a city name. Fetches street-level and landmark imagery from OpenStreetCam and Wikimedia Commons, then uses VLM Run (vlmrun) to generate a travel video and a travel plan. Use when the user wants a travel brochure, destination guide, travel video, or travel planning for a city."
---

# Travel Destination Brochure & Video

Create travel brochures, videos, and 1-day plans for a destination city by combining OpenStreetCam street-level photos, Wikimedia Commons imagery, and VLM Run for video and copy.

## Prerequisites

Before starting, ensure you have:

- **Python 3.10 or higher** installed
- **Internet connection** (for downloading images and API access)
- **VLMRUN_API_KEY** (optional, but required for video and travel plan generation)

**No API keys required for:**
- OpenStreetCam (public read access)
- Wikimedia Commons (public access)
- Nominatim geocoding (public access)

## Installation Steps

### Step 1: Verify Python Installation

Check if Python 3.10+ is installed:

**Windows (PowerShell):**
```powershell
python --version
# Should show Python 3.10.x or higher
```

**macOS/Linux:**
```bash
python3 --version
# Should show Python 3.10.x or higher
```

If Python is not installed or is an older version:
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **macOS**: `brew install python@3.11` (or use python.org installer)
- **Linux**: `sudo apt install python3.11` (Ubuntu/Debian) or use your distribution's package manager

### Step 2: Install uv (Package Manager)

**Windows (PowerShell):**
```powershell
# Using pip
pip install uv

# Or using PowerShell installer
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
# Using pip
pip install uv

# Or using curl installer
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Verify installation:**
```bash
uv --version
```

### Step 3: Create Virtual Environment

Navigate to the skill directory and create a virtual environment:

**Windows (PowerShell):**
```powershell
cd c:\Users\mehed\.claude\skills\travel-destination-brochure
uv venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
cd ~/.claude/skills/travel-destination-brochure
uv venv
source .venv/bin/activate
```

**Note:** You should see `(.venv)` in your terminal prompt when activated.

### Step 4: Install Dependencies

Install the required packages:

```bash
# Install vlmrun CLI (required for video and travel plan generation)
uv pip install "vlmrun[cli]"

# Install requests (required for API calls)
uv pip install requests
```

**Verify installation:**
```bash
vlmrun --version
python -c "import requests; print(requests.__version__)"
```

### Step 5: Set Up VLMRUN_API_KEY (Optional but Recommended)

To generate travel videos and plans, you need a VLMRUN API key:

**Windows (PowerShell):**
```powershell
# Set for current session
Check .env file for api key

$env:VLMRUN_API_KEY="your-api-key-here"

# Set permanently (User-level)
[System.Environment]::SetEnvironmentVariable('VLMRUN_API_KEY', 'your-api-key-here', 'User')
```

**macOS/Linux:**
```bash
# Set for current session
export VLMRUN_API_KEY="your-api-key-here"

# Set permanently (add to ~/.bashrc or ~/.zshrc)
echo 'export VLMRUN_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

**Verify environment variable:**

Read **.env** file to find api keys

```bash
# Windows PowerShell
echo $env:VLMRUN_API_KEY

# macOS/Linux
echo $VLMRUN_API_KEY
```

### Step 6: Verify Installation

Test that everything works:

```bash
# Test geocoding (should work without API key)
uv run scripts/geocode_city.py "Paris, France"

# Test vlmrun (if API key is set)
vlmrun --help
```

**Installation Complete!** You're ready to generate travel brochures.

## Quick Start (Recommended)

Use the simplified all-in-one script that handles everything automatically:

**Windows (PowerShell):**
```powershell
uv run scripts/simple_travel_brochure.py --city "Doha, Qatar"
```

**macOS/Linux:**
```bash
uv run scripts/simple_travel_brochure.py --city "Doha, Qatar"
```

**Alternative (if uv is not available):**
```bash
python scripts/simple_travel_brochure.py --city "Doha, Qatar"
```

This script will:
1. Geocode the city name to coordinates
2. Fetch 3 street-level photos from OpenStreetCam
3. Fetch 2 landmark images from Wikimedia Commons (total 5 images)
4. Generate a 30-second travel video using vlmrun (if `VLMRUN_API_KEY` is set)
5. Generate a one-day travel plan using vlmrun (if `VLMRUN_API_KEY` is set)
6. Clean up temporary files automatically

**Options:**
- `--output DIR` — Output directory (default: `./travel_brochure`)
- `--osc-count N` — Number of OpenStreetCam photos (default: 3)
- `--commons-count N` — Number of Commons images (default: 2)

**Note:** Set the `VLMRUN_API_KEY` environment variable to enable video and travel plan generation. The script will skip video generation gracefully if the API key is not set.

**Example:**
```bash
uv run scripts/simple_travel_brochure.py --city "Paris, France" --output ./paris_trip
```

**Output:**
- `images/` — Downloaded photos (5 images total)
- `manifest.json` — Metadata about the city, coordinates, and image paths
- `video/` — Generated travel video (if VLMRUN_API_KEY is set)
- `travel_plan.md` — One-day travel itinerary (if VLMRUN_API_KEY is set)

---

## Advanced: Step-by-Step Workflow

For more control over each step, use the individual scripts below.

### Workflow Overview

1. **Collect input** – Get destination city from the user.
2. **Geocode** – Resolve city name to coordinates (lat, lng).
3. **Fetch imagery & info** – OpenStreetCam (nearby photos) + Wikimedia Commons (search images and metadata).
4. **Generate assets** – Use **vlmrun** to create a short travel video and a travel plan from the collected images and info.

All paths below are relative to the directory containing this SKILL.md. 

**Run scripts using:**
- `uv run scripts/script_name.py` (recommended - handles dependencies automatically via PEP 723)
- `python scripts/script_name.py` (if dependencies are already installed)

### Step 1: Get Destination City

Ask the user: *"Which city do you want the travel brochure and video for?"* Use the exact city name (and country/region if ambiguous) for geocoding and Commons search.

### Step 2: Geocode City

Resolve city name to latitude/longitude (e.g. for OpenStreetCam and optional Commons geo-search).

```bash
uv run scripts/geocode_city.py "Paris, France"
# Or: python scripts/geocode_city.py "Tokyo"
```

Output: JSON with `lat`, `lng`, `display_name`. Use these in Steps 3–4.

### Step 3: Fetch OpenStreetCam Photos

OpenStreetCam provides street-level imagery. Base URL: `https://api.openstreetcam.org/`.

- **Nearby sequences:** `POST /nearby-tracks` — body: `lat`, `lng`, `distance` (km).
- **Nearby photos:** `POST /1.0/list/nearby-photos/` — body: `lat`, `lng`, `radius` (meters), optional `page`, `ipp`.

No `access_token` required for these read endpoints. Use `scripts/fetch_openstreetcam.py` to request photos and optionally download thumbnails/full images into a folder.

```bash
uv run scripts/fetch_openstreetcam.py --lat 48.8566 --lng 2.3522 --radius 2000 --output ./assets/osc --max-photos 20
```

Produces: image files under `--output` and a small manifest (e.g. `osc_manifest.json`) with captions/locations if available.

### Step 4: Fetch Wikimedia Commons Images & Info

Commons provides landmark and cultural images. API: `https://commons.wikimedia.org/w/api.php`.

- **Search:** `action=query`, `list=search`, `srsearch=<city or landmark>`, `srnamespace=6` (File namespace).
- **Image URLs and metadata:** `action=query`, `prop=imageinfo`, `iiprop=url|extmetadata`, `titles=File:...`.

Use `scripts/fetch_commons.py` to search by destination name, resolve file URLs, and optionally download to a folder.

```bash
uv run scripts/fetch_commons.py --query "Paris landmarks" --output ./assets/commons --max-images 15
```

Produces: image files and a manifest (e.g. `commons_manifest.json`) with captions/descriptions from Commons.

### Step 5: Aggregate Manifest for vlmrun

Combine OSC and Commons manifests (and optionally add short text lines per image) into a single manifest or list that you can pass to vlmrun (e.g. paths + one short caption per image). The pipeline script can do this.

```bash
uv run scripts/run_travel_pipeline.py --city "Paris, France" --output-dir ./travel_output
```

This script should: geocode → fetch OSC → fetch Commons → write `images/` and `manifest.json` (or `manifest.txt`) under `--output-dir`.

### Step 6: Generate Video and Travel Plan with vlmrun

Use the **vlmrun-cli-skill** workflow: ensure `vlmrun` is installed and `VLMRUN_API_KEY` is set.

**Travel video** – Pass the collected images and a single prompt so the model produces a short travel video (e.g. 30 seconds). Prefer `-o` to save the artifact.

**Note:** If `VLMRUN_API_KEY` is set as an environment variable, you can omit `--api-key`:

```bash
# Using environment variable (recommended)
vlmrun chat "Create a 30-second travel video showcasing these images of [CITY]. Add subtle captions with the location names. Keep a calm, inspiring travel-documentary style." -i ./travel_output/images/photo1.jpg -i ./travel_output/images/photo2.jpg -i ./travel_output/images/photo3.jpg ... -o ./travel_output/video

# Or using --api-key from .env, flag directly
vlmrun --api-key "your-api-key-here" chat "Create a 30-second travel video showcasing these images of [CITY]. Add subtle captions with the location names. Keep a calm, inspiring travel-documentary style." -i ./travel_output/images/photo1.jpg -i ./travel_output/images/photo2.jpg -i ./travel_output/images/photo3.jpg ... -o ./travel_output/video
```

If the number of files is large, reference the manifest and pass a subset (e.g. up to 10–15 representative images) or use a prompt that says “using the attached images in order.”

**Travel plan (1-day)** – Use the same images plus a text prompt to get a narrative or bullet-point plan.

```bash
# Using environment variable (recommended)
vlmrun chat "Using these images and their locations, write a one-day travel plan for [CITY]: morning, midday, and evening activities with specific places and practical tips. Output as structured markdown (headings and bullet points)." -i ./travel_output/images/photo1.jpg -i ./travel_output/images/photo2.jpg ... -o ./travel_output

# Or using --api-key flag directly
vlmrun --api-key "your-api-key-here" chat "Using these images and their locations, write a one-day travel plan for [CITY]: morning, midday, and evening activities with specific places and practical tips. Output as structured markdown (headings and bullet points)." -i ./travel_output/images/photo1.jpg -i ./travel_output/images/photo2.jpg ... -o ./travel_output
```

Save the model’s text response (and any artifact) under `--output-dir` (e.g. `travel_plan.md`).

## Scripts Reference

| Script | Purpose |
|--------|--------|
| `scripts/geocode_city.py` | City name → lat, lng (Nominatim) |
| `scripts/fetch_openstreetcam.py` | Fetch/download OpenStreetCam photos by lat/lng/radius |
| `scripts/fetch_commons.py` | Search and download Wikimedia Commons images by query |
| `scripts/run_travel_pipeline.py` | Run geocode + OSC + Commons and write manifest + images |

## API References

- **OpenStreetCam:** [API Reference](https://api.openstreetcam.org/api/doc.html) — nearby-tracks, list/nearby-photos, auth only for uploads.
- **Wikimedia Commons:** [Commons API](https://commons.wikimedia.org/w/api.php) — `action=query`, `list=search`, `prop=imageinfo`; [MediaWiki API help](https://www.mediawiki.org/wiki/Special:MyLanguage/API:Main_page).
- **vlmrun:** Use the **vlmrun-cli-skill** for setup, env vars, and all `vlmrun chat` options.

## Checklist for a Complete Run

- [ ] User provided destination city (and country if needed).
- [ ] Geocoded city and confirmed lat/lng.
- [ ] Fetched OpenStreetCam photos; saved images and manifest.
- [ ] Fetched Commons images for the destination; saved images and manifest.
- [ ] Built aggregated manifest/images under one output dir.
- [ ] Ran vlmrun with collected images to generate travel video; saved artifact with `-o`.
- [ ] Ran vlmrun with same (or subset) images to generate travel plan; saved text as markdown.

## Troubleshooting

### Installation Issues

**Python not found:**
- **Windows**: Ensure Python is added to PATH during installation, or use `py` instead of `python`
- **macOS/Linux**: Use `python3` instead of `python`

**uv command not found:**
- Restart your terminal after installation
- **Windows**: Check if uv is in your PATH: `$env:PATH`
- **macOS/Linux**: Ensure `~/.cargo/bin` or `~/.local/bin` is in your PATH

**Virtual environment activation fails:**
- **Windows PowerShell**: If you get an execution policy error, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **Windows CMD**: Use `.venv\Scripts\activate.bat` instead of `.ps1`
- **macOS/Linux**: Ensure you're using `source .venv/bin/activate` (not `./.venv/bin/activate`)

**vlmrun not found:**
- Ensure virtual environment is activated
- Reinstall: `uv pip install "vlmrun[cli]"`
- Verify: `which vlmrun` (macOS/Linux) or `where.exe vlmrun` (Windows)

### Runtime Issues

- **Geocode fails** – Try adding country/region, or use “City, Country” format.
- **OpenStreetCam returns few/no results:**
- Increase radius parameter (default: 2000m, try 5000m or 10000m)
- Try city center coordinates instead of outskirts
- Some regions have sparse coverage; try nearby major cities
- **Commons returns few results** – Broaden query (e.g. “City tourism”, “City sights”).
- **vlmrun errors:**
- Confirm `VLMRUN_API_KEY` is set correctly: `echo $VLMRUN_API_KEY` (macOS/Linux) or `echo $env:VLMRUN_API_KEY` (Windows)
- Check network connection
- Reduce number of input images if hitting API limits (try 5-10 images instead of 20+)
- Verify API key is valid and has sufficient credits/quota

**Script execution errors:**
- Ensure you're in the correct directory (skill root directory)
- Check that virtual environment is activated
- Verify all dependencies are installed: `uv pip list`

## Example End-to-End

```bash
# 1) Ask user for city, then run pipeline (e.g. "Paris, France")
uv run scripts/run_travel_pipeline.py --city "Paris, France" --output-dir ./travel_output

# 2) Generate travel video (use image paths from travel_output/images/ or image_paths.txt)
vlmrun chat "Create a 30-second travel video from these images of Paris. Add short location captions. Calm documentary style." -i ./travel_output/images/img_0000.jpg -i ./travel_output/images/img_0001.jpg -o ./travel_output/video

# 3) Generate 1-day travel plan (same images)
vlmrun chat "Using these photos of Paris, write a one-day travel plan (morning, midday, evening) with specific places and tips in markdown." -i ./travel_output/images/img_0000.jpg -i ./travel_output/images/img_0001.jpg -o ./travel_output
```

## Quick Reference: Key URLs

- OpenStreetCam API base: `https://api.openstreetcam.org/`
- Commons API: `https://commons.wikimedia.org/w/api.php`
- Nominatim geocoding: `https://nominatim.openstreetmap.org/search?q=<query>&format=json`
