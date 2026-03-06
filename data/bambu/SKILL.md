---
name: bambu
description: Control Bambu Lab 3D printers (H2D, X1C, P1S, A1) via CLI. Print management, AMS filament control, temperature, fans, lights, calibration, file management, and live monitoring. Use when operating a 3D printer, starting prints, monitoring progress, managing filaments, or troubleshooting printer issues.
---

# Bambu Lab 3D Printer Control

Full control of Bambu Lab printers via MQTT + FTP. Agent-agnostic, local-only, no cloud.

## Prerequisites

- Printer must be in **Developer Mode** (Settings → LAN Only → Enable Developer Mode)
- Need: IP address, serial number, LAN access code (from printer touchscreen)
- CLI: `@versatly/bambu` installed globally (`npm i -g @versatly/bambu`)

## Setup

```bash
bambu setup <ip> <serial> <access_code>
bambu ping  # verify connection
```

Config stored at `~/.bambu/config.json`.

## Progressive Loading Guide

Load ONLY what you need for the current task:

### Level 1: Status Check (most common)
```bash
bambu status          # full status overview
bambu status --json   # programmatic access
bambu temp            # just temperatures  
bambu ams             # just AMS/filament info
bambu errors          # any active errors
```

### Level 2: Print Operations
```bash
# Start a print from SD card
bambu print "filename.3mf"

# Upload and print in one step
bambu job upload-and-print ./my-part.3mf

# Control running print
bambu pause
bambu resume  
bambu stop

# Live monitoring (streams progress)
bambu watch
```

### Level 3: Hardware Control
```bash
# Temperature
bambu heat nozzle:220 bed:60
bambu cooldown

# Fans (0-100%)
bambu fan part 80
bambu fan aux 50
bambu fan chamber 30

# Lights
bambu light on
bambu light off

# Movement
bambu home
bambu move x:10 y:20 z:5
bambu gcode "G28"
```

### Level 4: AMS Filament Management
```bash
# Check what's loaded
bambu ams

# Load specific tray (0-3)
bambu load 0
bambu load 2

# Unload current filament
bambu unload
```

### Level 5: File Management & Calibration
```bash
# SD card files
bambu files
bambu upload ./part.3mf
bambu delete old-print.3mf

# Calibration
bambu calibrate bed
bambu calibrate vibration
bambu calibrate flow
bambu calibrate all
```

## Common Agent Workflows

### "Print this file"
```bash
bambu job upload-and-print ./part.3mf
bambu watch  # monitor until done
```

### "Check if printer is ready"
```bash
bambu status --json | jq '.gcode_state'
# IDLE = ready, RUNNING = busy, FAILED = needs attention
```

### "What filament is loaded?"
```bash
bambu ams --json
```

### "Preheat for PLA"
```bash
bambu heat nozzle:210 bed:60
```

### "Preheat for ABS"
```bash
bambu heat nozzle:260 bed:100
```

### "Something went wrong"
```bash
bambu errors --json   # check HMS error codes
bambu status          # full state overview
```

### "Finish up and shut down"
```bash
bambu cooldown
bambu light off
```

## Output Modes

- **Default:** Human-readable, emoji-prefixed, compact. Optimized for LLM context windows.
- **--json:** Raw JSON for programmatic parsing. Use with `jq` for field extraction.

## Safety Notes

- `bambu status`, `bambu temp`, `bambu ams`, `bambu errors`, `bambu version`, `bambu files` are **read-only and always safe**.
- `bambu print`, `bambu stop`, `bambu heat`, `bambu move`, `bambu gcode` **control the printer physically**. The nozzle is 200°C+. Use judgment.
- `bambu calibrate` moves the printer head. Ensure bed is clear.
- `bambu gcode` sends raw G-code. Know what you're sending.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Connection timeout | Developer Mode enabled? Correct IP? Printer on? |
| Auth failed | Check LAN access code (it changes if you re-enable Developer Mode) |
| FTP error | Port 990, implicit TLS. Printer must be in LAN mode. |
| No AMS data | AMS connected and detected? Check printer touchscreen. |
| MQTT drops | WiFi signal weak? Check `bambu status` for wifi_signal field. |
