# Urban Sports Scanner

Scannt deine Urban Sports Club Venues, zeigt Kurse mit direkten Booking-Links und kann Kurse buchen und stornieren.

## Setup

### 1. Python-Umgebung

```bash
cd /pfad/zu/urban-sports
python3 -m venv venv
venv/bin/pip install playwright
venv/bin/playwright install chromium
venv/bin/playwright install-deps chromium
```

### 2. Zugangsdaten

Trage deine USC-Logindaten ein:

```json
{
  "email": "deine-email@beispiel.de",
  "password": "dein-passwort"
}
```

Die Datei `credentials.json` ist in `.gitignore` und wird nicht committet.
Zugangsdaten werden nur fuer `--book`, `--cancel` und `--bookings` benoetigt.

### 3. Venues konfigurieren

Trage deine Venues in `config.py` ein. Die Venue-ID findest du in der URL auf urbansportsclub.com:

```
https://urbansportsclub.com/de/venues/20818
                                       ^^^^^
```

Beispiel:

```python
VENUES = {
    "storm": {
        "name": "STORM Cycling Berlin - Mitte",
        "url": "https://urbansportsclub.com/de/venues/20818",
        "type": "cycling",
        "keywords": ["Performance", "Groove", "Cycling"],
    },
    "fitboxing": {
        "name": "Brooklyn Fitboxing",
        "url": "https://urbansportsclub.com/de/venues/27355",
        "type": "boxing",
        "keywords": ["Boxing", "Fitboxing", "HIIT"],
    },
}
```

- `name`: Anzeigename
- `url`: Venue-Seite auf urbansportsclub.com
- `type`: Frei waehlbar, wird im Output angezeigt
- `keywords`: Helfen bei der Erkennung der Kursnamen im Seitentext

### URL-Parameter

Der Scanner haengt automatisch folgende Parameter an die Venue-URL an:

- `plan_type`: Mitgliedschafts-Stufe. Bestimmt welche Kurse angezeigt werden (nur die, die mit der jeweiligen Stufe buchbar sind). Privat: 1=Essential, 2=Classic, 3=Premium, 6=Max. Firma: 1=S, 2=M, 3=L, 6=XL. Standardwert: `3`.
- `business_type`: `b2c` (Privatmitglieder) oder `b2b` (Firmenmitglieder). Standardwert: `b2c`.

Diese Werte sind in `config.py` als `PLAN_TYPE` und `BUSINESS_TYPE` konfigurierbar.

## Usage

### Kurse scannen

```bash
# Alle Venues fuer heute
venv/bin/python scan.py

# Bestimmtes Datum
venv/bin/python scan.py --date 2026-02-10

# Nur eine Venue
venv/bin/python scan.py --venue storm

# JSON-Ausgabe (fuer Weiterverarbeitung)
venv/bin/python scan.py --json
```

Jeder Kurs wird mit direktem Booking-Link zurueckgegeben:
```
  07:30  STORM Cycling Berlin - Mitte    45 Min STORM Ride - Performance
         https://www.urbansportsclub.com/de/activities?class=98049323
```

### Buchen

```bash
venv/bin/python scan.py --book 98049323
```

### Stornieren

```bash
venv/bin/python scan.py --cancel 98049323
```

### Anstehende Buchungen

```bash
venv/bin/python scan.py --bookings
venv/bin/python scan.py --bookings --json
```

## Dateien

```
urban-sports/
├── SKILL.md                  # Diese Doku
├── scan.py                   # Scanner + Buchen + CLI
├── config.py                 # Venue-Konfiguration
├── credentials.json          # Login-Daten (nicht im Repo)
├── credentials.example.json  # Vorlage
├── .gitignore
└── venv/                     # Python virtualenv (nicht im Repo)
```

## Fehlerbehebung

### "Keine Venues konfiguriert"
Trage mindestens eine Venue in `config.py` ein.

### "credentials.json nicht gefunden"
Kopiere `credentials.example.json` nach `credentials.json` und trage deine Daten ein.

### Scanner findet keine Kurse
- Prüfe ob das Datum korrekt ist (nicht in der Vergangenheit)
- Manche Venues haben an bestimmten Tagen keine Kurse
- Chromium-Dependencies: `venv/bin/playwright install-deps chromium`
