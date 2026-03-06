---
name: calorie-visualizer
description: Local calorie logging and visual reporting (auto-refreshes and returns report image after each log)
metadata:
  openclaw:
    emoji: "📊"
    os:
      - darwin
      - linux
    requires:
      bins:
        - python3
---

# Calorie Visualizer

A local skill for meal logging and visual nutrition analysis.

## Core Flow

1. User sends meal text/photo (upstream extracts calorie/protein values or calls food-db lookup).
2. `add` (or `add-food`) writes to `calorie_data.db`.
3. After write, `visual_renderer.py` generates a fresh report image.
4. CLI prints `REPORT_IMAGE:<path>` so the chat layer can send the image.

## Daily Goal Priority

1. `config.daily_goal` (manual override)
2. TDEE derived from `USER.md`
3. If user explicitly refuses profile data: logging only, no repeated prompting
4. Fallback default in renderer: `2000 kcal`

## CLI Commands

```bash
# Add a meal with explicit nutrition values
python3 scripts/calorie_visualizer.py add "food name" 500 25 [--photo /path/to/image.jpg]

# Add from local food database (local-first, online fallback optional)
python3 scripts/calorie_visualizer.py add-food "Subway chicken sandwich" --multiplier 1.0
python3 scripts/calorie_visualizer.py add-food "rice" --offline

# Daily summary
python3 scripts/calorie_visualizer.py summary

# Regenerate report image
python3 scripts/calorie_visualizer.py report

# Config
python3 scripts/calorie_visualizer.py config daily_goal 2000
python3 scripts/calorie_visualizer.py config user_refused_profile True
```

## Dependencies

```bash
cd skills/calorie-visualizer
python3 -m pip install -r requirements.txt
```

- Python libs: `html2image`, `Pillow`
- Online fallback: optional USDA API (`USDA_API_KEY`)
- Database: SQLite (built into Python)
- Rendering: requires system Chromium/Chrome (called by html2image)

## Storage

- `calorie_data.db` (local SQLite)
- No automatic external sync
