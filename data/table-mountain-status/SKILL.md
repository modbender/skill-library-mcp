---
name: table-mountain-status
description: Fetch and report the Table Mountain Aerial Cableway status via the official weather API. Use when Master asks for “Tafelberg” updates, needs alerts about openings/closures, or wants automated Telegram reports about status, weather, and waiting times.
---

# Table Mountain Status

## Überblick
Dieses Skill ruft die offizielle Cableway-API (`https://cms.tablemountain.net/.../weather-api`) ab, parsed Status/Weather-Felder und liefert eine saubere Zusammenfassung (Text oder JSON). Ideal für Sofortabfragen („Status Tafelberg?“) sowie automatisierte Polling-Jobs mit Telegram-Alerts.

## Quick Start
1. **Manuell abrufen**
   ```bash
   python3 skills/table-mountain-status/scripts/fetch_status.py \
     --output data/table-mountain/$(date +%F_%H%M).txt
   ```
   Ausgabe erscheint sowohl in der Datei als auch im Terminal.

2. **JSON für Weiterverarbeitung**
   ```bash
   python3 skills/table-mountain-status/scripts/fetch_status.py \
     --format json --output data/table-mountain/$(date +%F).json
   ```

3. **Felder** (bereits im Script enthalten): `statusType`, `status`, `temperature`, `visibility`, `wind`, `firstUp`, `lastUp`, `lastDown`, `waitingTimeBottom`, `waitingTimeTop`, `lastUpdated`.

## Automatisierte Telegram-Alerts
1. **Cronjob alle 10 Minuten (Beispiel):**
   ```bash
   openclaw cron add <<'JSON'
   {
     "name": "table-mountain-10min",
     "schedule": { "kind": "every", "everyMs": 600000 },
     "sessionTarget": "isolated",
     "payload": {
       "kind": "agentTurn",
       "model": "default",
       "message": "Run `python3 skills/table-mountain-status/scripts/fetch_status.py --output data/table-mountain/latest.txt`. Post the summary to Master on Telegram, highlight status (open/closed), weather, queues, and timestamp. If the fetch fails, report the error."
     }
   }
   JSON
   ```
2. **Temporäre Jobs** (z. B. nur bis 16:00 lokal) → `schedule.kind = "cron"`, `expr = "*/10 6-15 * * *"`, `tz = "Europe/Berlin"`, und nach Ende wieder `cron update --enabled=false` oder `cron remove`.
3. **Job-Stop**: Immer sowohl Interval- als auch Tagesjob deaktivieren, falls mehrere Instanzen laufen.

## Troubleshooting
- **API down / Consent-Block:** Script liefert Exit-Code 1 + Fehlermeldung → Cron meldet den Fehler weiter.
- **Zeitzonen:** `lastUpdated` wird auf UTC+2 konvertiert (Cape Town). Bei Bedarf `format_summary` im Script anpassen.
- **Standard-Wartezeiten (0:05:00)** stammen oft vom API-Default; wenn echte Queue benötigt wird, Hinweis im Bericht ergänzen.
- **Netzwerk-Limits:** Falls `curl`-Proxy nötig, `urllib` ggf. um Environment-Proxy erweitern.

## Ressourcen
- `scripts/fetch_status.py` – Einfache CLI zum Abrufen, Formatieren und Speichern (Text/JSON) des Table-Mountain-Status.
