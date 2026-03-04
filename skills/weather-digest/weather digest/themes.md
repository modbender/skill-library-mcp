# HTML Theme Pack

Use the `--theme` flag to restyle the HTML digest without touching the template. Three palettes ship by default:

| Theme | Vibe | When to use |
| --- | --- | --- |
| `midnight` (default) | Dark navy background, white cards with magenta accents | Executive dashboards, OLED screens, night-mode newsletters |
| `daybreak` | Light slate background, blue accents | General audience newsletters, web embeds with white backgrounds |
| `citrus` | Warm cream background, orange highlights | Marketing pages, weather landing pages that need a sunny feel |

## CLI example
```bash
python weather_digest.py \
  --config config.json \
  --output digest.md \
  --html digest-daybreak.html \
  --theme daybreak
```

## Adding your own palette
1. Open `weather_digest.py` and locate `HTML_THEMES` near the top.
2. Duplicate one of the entries and adjust the hex values:
   ```python
   "forest": {
       "bg": "#0b132b",
       "card": "#1c2541",
       "text": "#f8f8f2",
       "accent": "#2ec4b6",
       "subhead": "#9aa5b1",
       "alert_bg": "#16324f",
       "alert_text": "#d9f9ff",
   }
   ```
3. Pass `--theme forest` when generating HTML.

Each palette controls body background, card fill, text color, accent color, and alert chip colors. Markdown/JSON output stay untouched, so you can offer multiple HTML downloads from the same run.
