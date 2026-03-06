---
name: synology-surveillance
description: Steuere Synology Surveillance Station Kameras über die Web API. Nutze diesen Skill für Snapshots, Live-Streams, Aufnahmen, PTZ-Steuerung und Ereignis-Überwachung. Erfordert Synology NAS mit Surveillance Station.
---

# Synology Surveillance Station Skill

Steuere deine Überwachungskameras über die Synology Surveillance Station API.

## Voraussetzungen

1. **Synology NAS** mit installierter Surveillance Station
2. **Benutzer** mit Surveillance Station-Rechten
3. **2FA deaktiviert** für den API-Benutzer
4. **jq** installiert (`apt install jq`)

## Schnellstart

### 1. Konfiguration in TOOLS.md

Füge die Verbindungsdaten zu `TOOLS.md` hinzu:

```markdown
### Synology Surveillance
- **Host:** 192.168.1.100 (deine NAS IP)
- **Port:** 5000 (HTTP) oder 5001 (HTTPS)
- **User:** surveillance_user
- **Pass:** dein_passwort
- **HTTPS:** false (true falls HTTPS aktiviert)
```

### 2. Login testen

```bash
./scripts/syno-surveillance.sh login
```

### 3. Kameras anzeigen

```bash
./scripts/syno-surveillance.sh cameras
```

Output:
```
ID: 1, Name: Eingang, Status: 1
ID: 2, Name: Garten, Status: 1
ID: 3, Name: Garage, Status: 0
```

### 4. Snapshot erstellen

```bash
./scripts/syno-surveillance.sh snapshot 1
```

Speichert: `syno_snapshot_1_1738972800.jpg`

### 5. Ereignisse anzeigen

```bash
# Letzte 10 Ereignisse
./scripts/syno-surveillance.sh events

# Letzte 50 Ereignisse
./scripts/syno-surveillance.sh events 50
```

## Verfügbare Befehle

| Befehl | Beschreibung |
|--------|--------------|
| `login` | Session erstellen (wird automatisch bei anderen Befehlen ausgeführt) |
| `logout` | Session beenden |
| `cameras` | Alle Kameras mit ID und Status auflisten |
| `snapshot <id>` | Snapshot einer Kamera erstellen |
| `record <id> start\|stop` | Aufnahme starten/stoppen |
| `events [limit]` | Ereignis-Log anzeigen |
| `stream <id>` | Live-Stream URL generieren |
| `ptz <id> <direction>` | PTZ-Kamera bewegen (left/right/up/down/zoomin/zoomout) |
| `preset <id> <num>` | PTZ-Voreinstellung anfahren |

## Umgebungsvariablen

| Variable | Standard | Beschreibung |
|----------|----------|--------------|
| `SYNOLOGY_HOST` | 192.168.1.100 | NAS IP/Hostname |
| `SYNOLOGY_PORT` | 5000 | NAS Port |
| `SYNOLOGY_USER` | admin | Username |
| `SYNOLOGY_PASS` | (leer) | Passwort |
| `SYNOLOGY_HTTPS` | false | HTTPS verwenden |

## Direkte API-Calls

Falls das Script nicht passt, direkt mit curl:

```bash
# Login
curl -c cookies.txt "http://192.168.1.100:5000/webapi/auth.cgi?api=SYNO.API.Auth&method=login&version=3&account=USER&passwd=PASS&session=SurveillanceStation&format=cookie"

# Snapshot
curl -b cookies.txt "http://192.168.1.100:5000/webapi/entry.cgi?api=SYNO.SurveillanceStation.Camera&method=GetSnapshot&version=1&cameraId=1" -o snapshot.jpg
```

## API Details

Für komplexere Operationen: [references/api.md](references/api.md)

## Home Assistant Integration

Für Home Assistant Nutzer: Der Skill kann auch für HA Automatisierungen genutzt werden:

```yaml
shell_command:
  syno_snapshot: "/pfad/zu/syno-surveillance.sh snapshot {{ camera_id }}"
```

## Troubleshooting

- **Login failed**: Passwort prüfen, 2FA deaktivieren
- **Permission denied**: Benutzer braucht Surveillance Station-Rechte
- **Camera not found**: Kamera-ID prüfen mit `cameras` Befehl
- **Empty snapshot**: Kamera offline oder keine Lizenz verfügbar

## Lizenz-Hinweis

Surveillance Station benötigt pro Kamera eine Lizenz (2 kostenlose inklusive bei den meisten NAS-Modellen).
