# Quick Start - Calorie Visualizer

## 1) Add a meal

```bash
python3 scripts/calorie_visualizer.py add "sandwich" 450 20
```

You can also use the local food database (local-first, online fallback optional):

```bash
python3 scripts/calorie_visualizer.py add-food "Subway chicken sandwich" --multiplier 1.0

# local only
python3 scripts/calorie_visualizer.py add-food "rice" --offline
```

After a successful log, the skill will:
- write data to SQLite
- regenerate the latest report image
- print `REPORT_IMAGE:<image_path>`

## 2) View daily summary

```bash
python3 scripts/calorie_visualizer.py summary
```

## 3) Regenerate report manually

```bash
python3 scripts/calorie_visualizer.py report
```

## 4) Set a calorie target (optional)

```bash
python3 scripts/calorie_visualizer.py config daily_goal 2000
```
