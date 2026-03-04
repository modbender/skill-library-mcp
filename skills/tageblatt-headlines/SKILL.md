---
name: tageblatt-headlines
description: Download and archive daily Schlagzeilen from https://www.tageblatt.de/. Use when Master asks for TAGEBLATT headlines, wants them saved locally, or needs an automated 07:00 workflow that fetches and forwards the latest headlines.
---

# Tageblatt Headlines

## Überblick
Dieses Skill-Paket lädt die Startseite von **tageblatt.de**, extrahiert die sichtbaren Artikelüberschriften (`<h2 class="article-heading">`), bereinigt sie und speichert sie lokal als Text- oder JSON-Datei. Nutze es für Ad-hoc-Abfragen ("Schlagzeilen jetzt"), tägliche Archive oder automatisierte Benachrichtigungen.

## Quick Start
1. **Headlines ziehen**
   ```bash
   python3 skills/tageblatt-headlines/scripts/fetch_headlines.py \
     --limit 15 \
     --output data/tageblatt/$(date +%Y-%m-%d)_headlines.txt
   ```
2. **JSON statt Text** (falls du die Daten weiterverarbeiten willst):
   ```bash
   python3 skills/tageblatt-headlines/scripts/fetch_headlines.py \
     --format json --output data/tageblatt/$(date +%Y-%m-%d).json
   ```
3. Die Skriptausgabe wird zusätzlich auf STDOUT geloggt – perfekt, um die Liste sofort per Telegram zu senden.

## Automatischer 07:00-Job
1. **Cronjob anlegen (lokale Zeit Europe/Berlin):**
   ```bash
   openclaw cron add <<'JSON'
   {
     "name": "tageblatt-headlines-07",
     "schedule": {
       "kind": "cron",
       "expr": "0 7 * * *",
       "tz": "Europe/Berlin"
     },
     "sessionTarget": "isolated",
     "payload": {
       "kind": "agentTurn",
       "model": "default",
       "message": "Run `python3 skills/tageblatt-headlines/scripts/fetch_headlines.py --limit 15 --output data/tageblatt/$(date +%F)_headlines.txt`. Send Master the list via Telegram (bulleted) and mention where the file was saved."
     }
   }
   JSON
   ```
2. **Automation optionalen Versand hinzufügen:** Nach erfolgreichem Lauf kann derselbe Job eine Telegram-Zusammenfassung verschicken (siehe Payload oben).
3. **Aufbewahrung:** Lege `data/tageblatt/` an und committe Archivdateien, falls sie langfristig gespeichert werden sollen.

## Fehlerbehebung & Hinweise
- Das Skript nutzt nur Standardbibliotheken (`urllib`, `re`). Keine zusätzlichen Pip-Abhängigkeiten nötig.
- Falls Consent-Banner den HTML-Aufbau ändert, prüfe die Regex in `scripts/fetch_headlines.py` (Pattern `HEADING_PATTERN`).
- Bei Netzwerkfehlern gibt das Skript Exit-Code 1 zurück. Cronjobs sollten in diesem Fall automatisch beim nächsten Zyklus erneut laufen.
- Begrenze `--limit`, falls du nur eine kurze Liste brauchst (z. B. Top 5).

## Ressourcen
- `scripts/fetch_headlines.py` – HTTP-Download & Parser für Schlagzeilen (Text/JSON-Ausgabe, limitierbar).
