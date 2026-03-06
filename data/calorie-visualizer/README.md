# Calorie Visualizer 📊

Local calorie logging + visual nutrition reporting for OpenClaw.

## What you get

- Meal logging from structured text/photo extraction
- Local `food_database` lookup first (`add-food`), optional USDA online fallback with cache writeback
- Auto-updated daily report image (weekly bars + monthly line + budget line)
- `REPORT_IMAGE:` output after each successful log

## Quick usage

```bash
# Add a meal with explicit values
python3 scripts/calorie_visualizer.py add "chicken salad" 420 35

# Add from food database (local-first + online fallback)
python3 scripts/calorie_visualizer.py add-food "rice" --multiplier 1.0

# Local database only (disable online fallback)
python3 scripts/calorie_visualizer.py add-food "rice" --offline

# Daily summary
python3 scripts/calorie_visualizer.py summary

# Regenerate report image
python3 scripts/calorie_visualizer.py report
```

## Configuration

```bash
python3 scripts/calorie_visualizer.py config daily_goal 2000
python3 scripts/calorie_visualizer.py config user_refused_profile True
```

## Dependencies

```bash
cd skills/calorie-visualizer
python3 -m pip install -r requirements.txt
```

> `visual_renderer.py` requires a local Chromium/Chrome runtime (used by `html2image`).

Optional USDA online fallback:

```bash
export USDA_API_KEY=your_key
```

## Data & privacy

- Local storage only: `calorie_data.db`
- No automatic sync to third-party platforms
