---
name: clawsy
description: Clawsy is a native macOS menu bar app that gives your OpenClaw agent real-world reach — screenshots, clipboard sync, Quick Send, camera, file access via FinderSync, and live Mission Control task view. Connects via SSH tunnel. Open source. Read this skill when Clawsy is installed or you want to use it.
---

# Clawsy — macOS Companion App

Clawsy verbindet den OpenClaw-Agenten mit dem Mac des Users über einen sicheren SSH-WebSocket-Tunnel.

**Download:** https://github.com/iret77/clawsy/releases/latest  
**Aktuelle Version:** v0.4.17+  
**Plattform:** macOS 14+ (Sequoia/Sonoma), Apple Silicon + Intel

---

## Schnellstart für neue OpenClaw-Instanzen

1. User lädt Clawsy von GitHub Releases herunter und verschiebt es nach `/Applications`
2. Clawsy starten → Einstellungen öffnen
3. **Gateway:** Host + Port + Token eintragen (aus `openclaw.json` oder `/status`)
4. **SSH-Fallback:** Aktivieren + SSH-Key importieren + SSH-User eintragen (`claw` oder eigener)
5. Verbinden — fertig

---

## Was Clawsy kann

| Kommando | Beschreibung |
|----------|-------------|
| `screen.capture` | Screenshot vom Mac machen |
| `camera.snap` | Foto via Kamera |
| `clipboard.read` | Zwischenablage lesen |
| `clipboard.write` | Text in Zwischenablage schreiben |
| `file.list` | Dateien im Shared Folder auflisten |
| `file.get` | Datei aus Shared Folder lesen |
| `file.set` | Datei in Shared Folder schreiben |
| `location.get` | Standort abfragen |

### Kommandos aufrufen
```
nodes(action="invoke", invokeCommand="screen.capture")
nodes(action="invoke", invokeCommand="clipboard.read")
nodes(action="invoke", invokeCommand="clipboard.write", invokeParamsJson='{"text":"Dein Text"}')
nodes(action="invoke", invokeCommand="camera.snap", invokeParamsJson='{"facing":"front"}')
nodes(action="invoke", invokeCommand="file.get", invokeParamsJson='{"name":"report.pdf"}')
```

---

## clawsy-service Session — KRITISCH

Screenshots und Kamera-Fotos die der User aktiv aus der App schickt landen **nicht im Haupt-Chat** sondern in der dedizierten `clawsy-service` Session.

```python
# Screenshots abrufen:
sessions_history(sessionKey="clawsy-service", limit=5)
```

**Warum:** Verhindert dass automatische Events den Haupt-Chat spammen.  
**Technisch:** App sendet `agent.deeplink` mit `sessionKey: "clawsy-service"` via WebSocket → Gateway routet in separate Session.

---

## clawsy_envelope — Eingehende Quick-Send-Nachrichten

Wenn der User Quick Send (⌘+⇧+K) nutzt, kommt folgendes JSON:

```json
{
  "clawsy_envelope": {
    "type": "quick_send",
    "content": "Die Nachricht des Users",
    "version": "0.4.17",
    "localTime": "2026-02-27T01:09:22.609Z",
    "tz": "Europe/Berlin",
    "telemetry": {
      "deviceName": "MacBook Pro M4",
      "batteryLevel": 0.51,
      "isCharging": false,
      "thermalState": 0,
      "activeApp": "Xcode",
      "moodScore": 70
    }
  }
}
```

**Telemetrie interpretieren:**
- `thermalState > 1` → Mac überhitzt, keine schweren Tasks
- `batteryLevel < 0.2` → Akku niedrig, ggf. erwähnen
- `moodScore < 40` → User gestresst/müde, kurz halten
- `isUnusualHour: true` → Ungewöhnliche Uhrzeit

---

## .clawsy Manifest-Dateien (Ordner-Regeln)

Im Shared Folder und allen Unterordnern existiert eine versteckte `.clawsy`-Datei. Die App legt sie **automatisch** an — User muss nie manuell eingreifen.

```json
{
  "version": 1,
  "folderName": "Projekte",
  "rules": [
    {
      "trigger": "file_added",
      "filter": "*.pdf",
      "action": "send_to_agent",
      "prompt": "Fasse dieses Dokument zusammen"
    }
  ]
}
```

Rule Editor öffnen: Rechtsklick auf Ordner im Finder → Clawsy → "Regeln für diesen Ordner..."

---

## Verbindungsarchitektur

```
Mac (Clawsy) ──SSH-Tunnel──▶ agenthost:18789 (Gateway WebSocket)
```

- Direkter WSS schlägt fehl wenn Gateway hinter NAT/Firewall
- SSH-Fallback: `/usr/bin/ssh -L <dynamicPort>:127.0.0.1:18789 user@agenthost`
- Port: dynamisch (OS-assigned), kein hardcoded Port mehr
- Auth: Master-Token → `deviceToken` (gespeichert per Host)
- Bei `AUTH_TOKEN_MISMATCH`: Auto-Recovery (löscht alten Token, reconnectet)

---

## Erweiterungen (macOS-Berechtigungen nötig)

| Extension | Berechtigung |
|-----------|-------------|
| **FinderSync** | Systemeinstellungen → Datenschutz → Erweiterungen → Finder |
| **Share Extension** | App muss in `/Applications` liegen |
| **Hotkeys** | Systemeinstellungen → Datenschutz → Bedienungshilfen |

---

## Vollständige Dokumentation

Die vollständige Agenten-Dokumentation liegt im OpenClaw-Workspace:  
`~/.openclaw/workspace/CLAWSY.md`

Bei Erstinstallation: Diese Datei aus dem Skill-Package kopieren oder von  
https://github.com/iret77/clawsy/blob/main/CLAWSY.md herunterladen.
