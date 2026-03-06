# Travel Destination Brochure Generator

A Python-based tool that automatically generates travel brochures, videos, and one-day travel plans for any destination city. The tool combines street-level imagery from OpenStreetCam, landmark photos from Wikimedia Commons, and AI-powered video generation using VLM Run to create comprehensive travel content.

## 🌟 Features

- **Automatic City Geocoding**: Converts city names to coordinates using OpenStreetMap's Nominatim service
- **Street-Level Imagery**: Fetches real street photos from OpenStreetCam API
- **Landmark Photography**: Retrieves high-quality landmark images from Wikimedia Commons
- **AI Video Generation**: Creates 30-second travel videos using VLM Run's visual AI
- **Travel Planning**: Generates detailed one-day itineraries with morning, midday, and evening activities
- **All-in-One Script**: Simple command-line interface for quick brochure generation
- **Modular Design**: Individual scripts for custom workflows and advanced usage

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.10 or higher** installed
- **Internet connection** (required for API calls and image downloads)
- **VLMRUN_API_KEY** (optional, but required for video and travel plan generation)

**No API keys required for:**
- OpenStreetCam (public read access)
- Wikimedia Commons (public access)
- Nominatim geocoding (public access)

## 🚀 Quick Start

### Installation

1. **Verify Python Installation**

   ```powershell
   # Windows (PowerShell)
   python --version
   # Should show Python 3.10.x or higher
   ```

   ```bash
   # macOS/Linux
   python3 --version
   # Should show Python 3.10.x or higher
   ```

2. **Install uv Package Manager** (recommended)

   ```powershell
   # Windows (PowerShell)
   pip install uv
   # Or using installer
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

   ```bash
   # macOS/Linux
   pip install uv
   # Or using installer
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install Dependencies**

   ```bash
   # Install vlmrun CLI (required for video and travel plan generation)
   uv pip install "vlmrun[cli]"

   # Install requests (required for API calls)
   uv pip install requests
   ```

4. **Set Up VLMRUN_API_KEY** (Optional but Recommended)

   Create a `.env` file in the project root (see `.env_template` for reference):

   ```env
   VLMRUN_API_KEY="your-api-key-here"
   VLMRUN_BASE_URL="https://agent.vlm.run/v1"
   ```

   Or set it as an environment variable:

   ```powershell
   # Windows (PowerShell)
   $env:VLMRUN_API_KEY="your-api-key-here"
   ```

   ```bash
   # macOS/Linux
   export VLMRUN_API_KEY="your-api-key-here"
   ```

### Generate Your First Travel Brochure

Use the simplified all-in-one script:

```powershell
# Windows (PowerShell)
uv run scripts/simple_travel_brochure.py --city "Doha, Qatar"
```

```bash
# macOS/Linux
uv run scripts/simple_travel_brochure.py --city "Doha, Qatar"
```

**Alternative (if uv is not available):**
```bash
python scripts/simple_travel_brochure.py --city "Doha, Qatar"
```

This script will:
1. ✅ Geocode the city name to coordinates
2. ✅ Fetch 3 street-level photos from OpenStreetCam
3. ✅ Fetch 2 landmark images from Wikimedia Commons (total 5 images)
4. ✅ Generate a 30-second travel video using vlmrun (if `VLMRUN_API_KEY` is set)
5. ✅ Generate a one-day travel plan using vlmrun (if `VLMRUN_API_KEY` is set)
6. ✅ Save all results to `./travel_brochure/` directory

**Output Structure:**
```
travel_brochure/
├── images/
│   ├── image_00.jpg
│   ├── image_01.jpg
│   ├── image_02.jpg
│   ├── image_03.jpg
│   └── image_04.jpg
├── manifest.json          # Metadata about city, coordinates, and images
├── video/                 # Generated travel video (if API key is set)
└── travel_plan.md         # One-day travel itinerary (if API key is set)
```

## 📖 Detailed Usage

### Script Options

#### `simple_travel_brochure.py` (Recommended for Beginners)

The easiest way to generate a complete travel brochure:

```bash
uv run scripts/simple_travel_brochure.py --city "Paris, France" --output ./paris_trip --osc-count 3 --commons-count 2
```

**Options:**
- `--city` (required): City name, e.g., "Paris, France" or "Tokyo"
- `--output DIR`: Output directory (default: `./travel_brochure`)
- `--osc-count N`: Number of OpenStreetCam photos (default: 3)
- `--commons-count N`: Number of Commons images (default: 2)

#### `run_travel_pipeline.py` (Advanced Workflow)

For more control over the image collection process:

```bash
uv run scripts/run_travel_pipeline.py --city "Paris, France" --output-dir ./travel_output --max-photos 15 --max-commons 10
```

**Options:**
- `--city` (required): Destination city name
- `--output-dir DIR`: Output directory (default: `./travel_output`)
- `--radius METERS`: OpenStreetCam search radius in meters (default: 2000)
- `--max-photos N`: Max OpenStreetCam photos (default: 15)
- `--max-commons N`: Max Commons images (default: 10)
- `--skip-osc`: Skip OpenStreetCam fetch
- `--skip-commons`: Skip Wikimedia Commons fetch

**Output:**
- `images/`: All downloaded images (renamed as `img_0000.jpg`, `img_0001.jpg`, etc.)
- `manifest.json`: Combined manifest with all image metadata
- `image_paths.txt`: List of image paths for easy use with vlmrun

#### Individual Scripts

For step-by-step control, use these scripts individually:

**1. Geocode City**
```bash
uv run scripts/geocode_city.py "Paris, France"
# Output: JSON with lat, lng, display_name
```

**2. Fetch OpenStreetCam Photos**
```bash
uv run scripts/fetch_openstreetcam.py --lat 48.8566 --lng 2.3522 --radius 2000 --output ./assets/osc --max-photos 20
```

**3. Fetch Wikimedia Commons Images**
```bash
uv run scripts/fetch_commons.py --query "Paris landmarks" --output ./assets/commons --max-images 15
```

### Generating Videos and Travel Plans

After collecting images, use `vlmrun` to generate content:

**Generate Travel Video:**
```bash
vlmrun chat "Create a 30-second travel video showcasing these images of Paris. Add subtle captions with location names. Keep a calm, inspiring travel-documentary style." \
  -i ./travel_output/images/img_0000.jpg \
  -i ./travel_output/images/img_0001.jpg \
  -i ./travel_output/images/img_0002.jpg \
  -o ./travel_output/video
```

**Generate Travel Plan:**
```bash
vlmrun chat "Using these images and their locations, write a one-day travel plan for Paris: morning, midday, and evening activities with specific places and practical tips. Output as structured markdown." \
  -i ./travel_output/images/img_0000.jpg \
  -i ./travel_output/images/img_0001.jpg \
  -i ./travel_output/images/img_0002.jpg \
  -o ./travel_output
```

## 📁 Project Structure

```
travel-destination-brochure/
├── README.md                    # This file
├── SKILL.md                     # Skill documentation for AI agents
├── .env_template               # Template for environment variables
├── references/                  # API documentation references
│   ├── openstreetcam_api.md    # OpenStreetCam API reference
│   └── commons_api.md          # Wikimedia Commons API reference
└── scripts/                     # Python scripts
    ├── geocode_city.py          # City name → lat/lng (Nominatim)
    ├── fetch_openstreetcam.py   # Fetch OpenStreetCam photos by coordinates
    ├── fetch_commons.py         # Search and download Commons images
    ├── run_travel_pipeline.py   # Full pipeline: geocode + OSC + Commons
    └── simple_travel_brochure.py # All-in-one simplified script
```

## 🔧 Scripts Reference

| Script | Purpose | Key Features |
|--------|---------|--------------|
| `geocode_city.py` | Convert city name to coordinates | Uses Nominatim (OpenStreetMap), returns lat/lng/display_name |
| `fetch_openstreetcam.py` | Fetch street-level photos | Searches by lat/lng/radius, downloads thumbnails/full images |
| `fetch_commons.py` | Search and download Commons images | Searches by query, extracts metadata and captions |
| `run_travel_pipeline.py` | Complete image collection pipeline | Combines geocoding, OSC, and Commons into one manifest |
| `simple_travel_brochure.py` | All-in-one brochure generator | Handles everything: geocode → fetch → video → plan |

## 🌐 API References

### OpenStreetCam API

- **Base URL**: `https://api.openstreetmap.org/`
- **Documentation**: [API Reference](https://api.openstreetcam.org/api/doc.html)
- **Key Endpoints**:
  - `POST /1.0/list/nearby-photos/` - Get photos near coordinates
  - `POST /nearby-tracks` - Get nearby sequences
- **Authentication**: Not required for read operations

See `references/openstreetcam_api.md` for detailed API documentation.

### Wikimedia Commons API

- **Base URL**: `https://commons.wikimedia.org/w/api.php`
- **Documentation**: [MediaWiki API](https://www.mediawiki.org/wiki/Special:MyLanguage/API:Main_page)
- **Key Operations**:
  - `action=query&list=search` - Search for images
  - `action=query&prop=imageinfo` - Get image URLs and metadata
- **Authentication**: Not required for read operations

See `references/commons_api.md` for detailed API documentation.

### VLM Run CLI

- **Installation**: `uv pip install "vlmrun[cli]"`
- **Documentation**: See vlmrun-cli-skill for setup and usage
- **Key Command**: `vlmrun chat <prompt> -i <image> ... -o <output>`

## 🐛 Troubleshooting

### Installation Issues

**Python not found:**
- **Windows**: Ensure Python is added to PATH during installation, or use `py` instead of `python`
- **macOS/Linux**: Use `python3` instead of `python`

**uv command not found:**
- Restart your terminal after installation
- **Windows**: Check if uv is in your PATH: `$env:PATH`
- **macOS/Linux**: Ensure `~/.cargo/bin` or `~/.local/bin` is in your PATH

**Virtual environment activation fails:**
- **Windows PowerShell**: If you get an execution policy error, run:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- **Windows CMD**: Use `.venv\Scripts\activate.bat` instead of `.ps1`
- **macOS/Linux**: Ensure you're using `source .venv/bin/activate`

**vlmrun not found:**
- Ensure dependencies are installed: `uv pip install "vlmrun[cli]"`
- Verify installation: `vlmrun --version`

### Runtime Issues

**Geocode fails:**
- Try adding country/region: "Paris, France" instead of just "Paris"
- Use "City, Country" format for better results

**OpenStreetCam returns few/no results:**
- Increase radius parameter (default: 2000m, try 5000m or 10000m)
- Try city center coordinates instead of outskirts
- Some regions have sparse coverage; try nearby major cities

**Commons returns few results:**
- Broaden query (e.g., "City tourism", "City sights", "City landmarks")
- Try different search terms related to the destination

**vlmrun errors:**
- Confirm `VLMRUN_API_KEY` is set correctly:
  ```bash
  # Windows PowerShell
  echo $env:VLMRUN_API_KEY
  
  # macOS/Linux
  echo $VLMRUN_API_KEY
  ```
- Check network connection
- Reduce number of input images if hitting API limits (try 5-10 images instead of 20+)
- Verify API key is valid and has sufficient credits/quota

**Script execution errors:**
- Ensure you're in the correct directory (skill root directory)
- Check that all dependencies are installed: `uv pip list`
- Verify Python version: `python --version` (should be 3.10+)

## 📝 Example Workflows

### Example 1: Quick Brochure Generation

```bash
# Generate a complete travel brochure for Tokyo
uv run scripts/simple_travel_brochure.py --city "Tokyo, Japan" --output ./tokyo_brochure

# Output will be in ./tokyo_brochure/
```

### Example 2: Custom Image Collection

```bash
# Step 1: Collect images with custom parameters
uv run scripts/run_travel_pipeline.py \
  --city "Barcelona, Spain" \
  --output-dir ./barcelona \
  --max-photos 20 \
  --max-commons 15 \
  --radius 5000

# Step 2: Generate video (manually)
vlmrun chat "Create a 30-second travel video of Barcelona" \
  -i ./barcelona/images/img_0000.jpg \
  -i ./barcelona/images/img_0001.jpg \
  -i ./barcelona/images/img_0002.jpg \
  -i ./barcelona/images/img_0003.jpg \
  -i ./barcelona/images/img_0004.jpg \
  -o ./barcelona/video

# Step 3: Generate travel plan (manually)
vlmrun chat "Write a one-day travel plan for Barcelona" \
  -i ./barcelona/images/img_0000.jpg \
  -i ./barcelona/images/img_0001.jpg \
  -i ./barcelona/images/img_0002.jpg \
  -o ./barcelona
```

### Example 3: Step-by-Step Manual Workflow

```bash
# 1. Geocode city
uv run scripts/geocode_city.py "Dubai, UAE"
# Output: {"lat": 25.2048, "lng": 55.2708, "display_name": "Dubai, UAE"}

# 2. Fetch OpenStreetCam photos
uv run scripts/fetch_openstreetcam.py \
  --lat 25.2048 \
  --lng 55.2708 \
  --radius 3000 \
  --output ./dubai/osc \
  --max-photos 10

# 3. Fetch Commons images
uv run scripts/fetch_commons.py \
  --query "Dubai landmarks tourism" \
  --output ./dubai/commons \
  --max-images 8

# 4. Use collected images with vlmrun
vlmrun chat "Create a travel video of Dubai" \
  -i ./dubai/osc/osc_0000.jpg \
  -i ./dubai/commons/... \
  -o ./dubai/video
```

## 📚 Additional Resources

- **OpenStreetCam**: [Website](https://openstreetcam.org/) | [API Docs](https://api.openstreetcam.org/api/doc.html)
- **Wikimedia Commons**: [Website](https://commons.wikimedia.org/) | [API Docs](https://commons.wikimedia.org/w/api.php)
- **Nominatim Geocoding**: [Documentation](https://nominatim.org/release-docs/develop/api/Overview/)
- **VLM Run**: See vlmrun-cli-skill documentation for detailed usage

## ✅ Checklist for Complete Run

- [ ] Python 3.10+ installed and verified
- [ ] Dependencies installed (`vlmrun[cli]`, `requests`)
- [ ] `VLMRUN_API_KEY` set (optional but recommended)
- [ ] User provided destination city (with country if needed)
- [ ] Geocoded city and confirmed lat/lng
- [ ] Fetched OpenStreetCam photos; saved images and manifest
- [ ] Fetched Commons images for the destination; saved images and manifest
- [ ] Built aggregated manifest/images under output directory
- [ ] Ran vlmrun with collected images to generate travel video (if API key set)
- [ ] Ran vlmrun with same images to generate travel plan (if API key set)

## 🤝 Contributing

This is a skill template for AI agents. To extend functionality:

1. Review the existing scripts in `scripts/`
2. Check API references in `references/`
3. Follow the existing code patterns and structure
4. Test with multiple cities and edge cases

## 📄 License

This project uses public APIs and open-source tools. Please respect:
- OpenStreetCam's [Terms of Service](https://openstreetcam.com/terms/)
- Wikimedia Commons' [Licensing](https://commons.wikimedia.org/wiki/Commons:Licensing)
- Nominatim's [Usage Policy](https://operations.osmfoundation.org/policies/nominatim/)

---

**Happy Travel Planning! ✈️🌍**
