# Bambu Lab MQTT API Reference

## Verbindung

**Protokoll:** MQTT over TLS (MQTTS)  
**Port:** 8883  
**Host:** IP-Adresse des Druckers  
**Username:** Seriennummer (z.B. `03919A3A2200009`)  
**Passwort:** Access Code (z.B. `33576961`)

## Topics

### Report (Drucker → Client)

Der Drucker sendet Status-Updates an:
```
device/<serial>/report
```

### Request (Client → Drucker)

Kommandos werden gesendet an:
```
device/<serial>/request
```

## Nachrichten-Format

### Status-Report (JSON)

```json
{
  "print": {
    "mc_print_stage": "1",
    "mc_percent": 45,
    "mc_remaining_time": 3600,
    "bed_temper": 60.0,
    "bed_target_temper": 60,
    "nozzle_temper": 210.0,
    "nozzle_target_temper": 210,
    "chamber_temper": 35.0,
    "fan_speed": "9",
    "lights_report": [{"node": "chamber_light", "mode": "on"}],
    "gcode_state": "RUNNING",
    "print_error": 0,
    "layer_num": 45,
    "total_layer_num": 100,
    "filename": "test.gcode.3mf"
  }
}
```

### Wichtige Felder

| Feld | Beschreibung | Werte |
|------|--------------|-------|
| `mc_print_stage` | Druck-Phase | `1`=Vorheizen, `2`=Drucken, etc. |
| `mc_percent` | Fortschritt | 0-100 |
| `mc_remaining_time` | Restzeit | Sekunden |
| `gcode_state` | Druck-Status | `IDLE`, `RUNNING`, `PAUSE`, `FINISH`, `FAILED` |
| `print_error` | Fehler-Code | `0`=OK, sonst Fehler |
| `bed_temper` | Bett-Temperatur | °C |
| `nozzle_temper` | Nozzle-Temperatur | °C |
| `chamber_temper` | Kammer-Temperatur | °C (X1C) |
| `fan_speed` | Lüftergeschwindigkeit | 0-15 (entspricht 0-255) |
| `layer_num` | Aktueller Layer | Zahl |
| `total_layer_num` | Gesamt-Layer | Zahl |

## Kommandos (JSON)

### Pause
```json
{"print": {"command": "pause"}}
```

### Resume
```json
{"print": {"command": "resume"}}
```

### Stop
```json
{"print": {"command": "stop"}}
```

### Licht an/aus
```json
{"print": {"command": "ledctrl", "led_node": "chamber_light", "led_mode": "on"}}
```

### Lüftersteuerung
```json
{"print": {"command": "gcode_line", "param": "M106 S255"}}
```

### Drucken von SD-Karte
```json
{"print": {"command": "gcode_file", "param": "test.gcode.3mf"}}
```

## Fehler-Codes

Häufige `print_error` Codes:
- `0` - Kein Fehler
- `50348044` - Filament runter (HMS_ERR)
- `50348045` - Filament verstopft
- `16777248` - Bett-Abfall fehlgeschlagen
- `16777249` - Objekt abgefallen

## Links

- [Bambu Lab LAN Wiki](https://wiki.bambulab.com/en/home)
- [GitHub: bambu-mqtt-docs](https://github.com/Doridian/bambu-mqtt)
