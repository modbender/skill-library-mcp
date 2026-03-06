---
name: tuebingen-weather-graphics
description: Generate and send a 5-day Tübingen weather graphic (PNG) from open-meteo.com. Use when Master wants a nicer visual forecast plus summary text for the next few days.
---

# Tübingen Weather Graphics

## Überblick
Erstellt eine ansprechende PNG-Grafik (max/min-Temperaturen + Regenwahrscheinlichkeit für 5 Tage) auf Basis von Open-Meteo. Ideal für morgendliche Forecast-Posts via Telegram oder Archivierung.

## Voraussetzungen
- Python 3.11+ 
- `matplotlib`, `numpy`, `pillow` (am einfachsten via virtuelles Environment):
  ```bash
  python3 -m venv /tmp/tuebingen-plot
  source /tmp/tuebingen-plot/bin/activate
  pip install matplotlib
  ```

## Quick Start
```bash
/tmp/tuebingen-plot/bin/python \
  skills/tuebingen-weather-graphics/scripts/generate_forecast_graph.py \
  --days 5 \
  --output data/weather/tuebingen_forecast.png
```
Ausgabe: 
- PNG unter `data/weather/...`
- Textzusammenfassung im Terminal (z. B. „Fri 13.02: 5/10°C, Regen 85% | …“)

## Automatischer Versand
1. **Cron-Job 07:30 (Beispiel):**
   ```bash
   openclaw cron add <<'JSON'
   {
     "name": "tuebingen-forecast-graphic",
     "schedule": { "kind": "cron", "expr": "30 7 * * *", "tz": "Europe/Berlin" },
     "sessionTarget": "isolated",
     "payload": {
       "kind": "agentTurn",
       "model": "default",
       "message": "Run `/tmp/tuebingen-plot/bin/python skills/tuebingen-weather-graphics/scripts/generate_forecast_graph.py --output data/weather/tuebingen_forecast.png`. Send Master the summary text plus attach the PNG."
     }
   }
   JSON
   ```
2. **Telegram Versand:** `message.send` mit `media=data/weather/tuebingen_forecast.png`.

## Troubleshooting
- **Matplotlib ImportError:** Stelle sicher, dass das oben genannte venv aktiv ist oder die Pakete systemweit installiert wurden.
- **Leere Daten:** Open-Meteo liefert manchmal keine Regenwahrscheinlichkeit → Script zeigt 0%. Kann im Code angepasst werden.
- **Mehr Tage:** `--days 7` o. Ä. möglich (die API liefert bis zu 7+ Tage im daily-Block).

## Ressourcen
- `scripts/generate_forecast_graph.py` – Lädt Daily-Daten, zeichnet Linien/Flächen-Plot + Regen-Balken, speichert PNG.
