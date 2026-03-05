---
name: bambu-lab
description: Steuere Bambu Lab 3D-Drucker (A1, P1P, X1) über MQTT. Nutze diesen Skill für Druck-Überwachung, Status-Abfragen, Steuerung (Pause/Stopp) und Benachrichtigungen bei Druckende oder Fehlern. Erfordert LAN-Mode mit Access Code.
---

# Bambu Lab 3D-Drucker Skill

Steuerung und Überwachung von Bambu Lab 3D-Druckern über MQTT im lokalen Netzwerk.

## Konfiguration

Standard-Konfiguration (anpassbar in `scripts/bambu.sh`):
- **Host:** `192.168.30.103` (A1 Drucker)
- **Port:** `8883` (MQTT über TLS)
- **Username:** `03919A3A2200009` (Seriennummer)
- **Passwort:** `33576961` (Access Code)
- **Model:** A1

## Verwendung

Nutze das Skript `scripts/bambu.sh` für alle Operationen:

```bash
./skills/bambu-lab/scripts/bambu.sh <befehl>
```

### Befehle

**Status & Überwachung:**
- `status` - Aktueller Druckstatus
- `progress` - Druckfortschritt in %
- `temps` - Temperaturen (Nozzle, Bed, Chamber)
- `watch` - Live-Überwachung (läuft dauerhaft)

**Steuerung:**
- `pause` - Druck pausieren
- `resume` - Druck fortsetzen
- `stop` - Druck abbrechen
- `light on|off` - Druckerlicht an/aus
- `fans <0-255>` - Lüftergeschwindigkeit

**Benachrichtigungen:**
- `notify` - Starte Überwachung mit Telegram-Benachrichtigung

**MQTT Debug:**
- `raw` - Rohe MQTT-Nachrichten anzeigen

## Beispiele

```bash
# Status abfragen
./skills/bambu-lab/scripts/bambu.sh status

# Druckfortschritt
./skills/bambu-lab/scripts/bambu.sh progress

# Live-Überwachung
./skills/bambu-lab/scripts/bambu.sh watch

# Druck pausieren
./skills/bambu-lab/scripts/bambu.sh pause

# Mit Benachrichtigung
./skills/bambu-lab/scripts/bambu.sh notify
```

## Automatische Benachrichtigungen

Für automatische Benachrichtigungen bei Druckende:

```bash
# Im Hintergrund starten
./skills/bambu-lab/scripts/bambu.sh notify &
```

Oder per Cron/Heartbeat regelmäßig ausführen.

## API Referenz

Siehe [references/mqtt.md](references/mqtt.md) für vollständige MQTT-Dokumentation.

## Unterstützte Modelle

- ✅ A1 (getestet)
- ✅ A1 Mini
- ✅ P1P / P1S
- ✅ X1 / X1C

Alle Modelle nutzen das gleiche MQTT-Protokoll im LAN-Mode.
