---
name: tuebingen-weather
description: Send daily 08:00 weather reports for Tübingen using open-meteo.com. Use when Master wants an automated summary (current conditions + today’s high/low + rain chance) stored locally and forwarded via Telegram.
---

# Tübingen Weather

## Überblick
Dieses Skill liefert eine tägliche Wetterzusammenfassung für Tübingen (Open-Meteo API, keine API-Keys). Output: kompakte Text-Zusammenfassung mit aktuellem Zustand, Tagesminimum/-maximum und Regenwahrscheinlichkeit.

## Quick Start
1. **Manuell abrufen**
   ```bash
   python3 skills/tuebingen-weather/scripts/fetch_tuebingen_weather.py \
     --output data/weather/$(date +%F)_tuebingen.txt
   ```
   -> gibt die Zusammenfassung aus und speichert sie optional.

2. **Ohne Datei** (nur Konsole/Telegram):
   ```bash
   python3 skills/tuebingen-weather/scripts/fetch_tuebingen_weather.py
   ```

## Automatisierter 08:00-Versand
1. **Cron-Job anlegen**
   ```bash
   openclaw cron add <<'JSON'
   {
     "name": "tuebingen-weather-08",
     "schedule": { "kind": "cron", "expr": "0 8 * * *", "tz": "Europe/Berlin" },
     "sessionTarget": "isolated",
     "payload": {
       "kind": "agentTurn",
       "model": "default",
       "message": "Run `python3 skills/tuebingen-weather/scripts/fetch_tuebingen_weather.py --output data/weather/$(date +%F)_tuebingen.txt`. Send Master the stdout summary + mention the saved file. Report errors if the command fails."
     }
   }
   JSON
   ```
2. **Überblick**
   - Speichert Textdateien unter `data/weather/YYYY-MM-DD_tuebingen.txt` (frei anpassbar).
   - Cron-Bot postet jeden Morgen um 08:00 automatisch die Nachricht.

## Hinweise
- Script nutzt nur Stdlib (`urllib`, `json`). Kein pip install nötig.
- Wettercodes → deutsche Beschreibung in `WEATHER_CODES`.
- Zeitzone: `Europe/Berlin` – passt sich automatisch Sommer/Winter an.
- Anpassungen (weitere Felder, z. B. Böen, UV) einfach im Script ergänzen.

## Ressourcen
- `scripts/fetch_tuebingen_weather.py` – CLI-Skript für Open-Meteo.
