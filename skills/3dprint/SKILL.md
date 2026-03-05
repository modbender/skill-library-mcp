# 3D Print Automation Skill

Automate 3D printing with Flashforge Adventurer 5M printers ("Ralph Wiggum").

## Overview

Complete workflow for automated 3D printing. Originally inspired by Bambu Studio AI patterns.

## Features

- ✅ **Printer Status** - Real-time temp, progress, state
- ✅ **Print Control** - Start, pause, stop prints  
- ✅ **File Management** - List/select files on printer
- ✅ **Slicing** - PrusaSlicer CLI integration
- ✅ **Camera** - Snapshot from printer camera (port 8080)
- ✅ **Full Pipeline** - Search → Slice → Print → Monitor

## Printer Configuration

- **Name:** Ralph Wiggum
- **IP:** 10.0.0.41
- **Serial:** SNMSRE9704441
- **Check Code:** a31d9729
- **Camera:** Port 8080 (web interface)
- **Control:** Port 8899 (G-code)

## Installation

```bash
# Install dependencies
pip install flashforge-python-api requests

# Or use virtual environment
source ~/.openclaw/workspace/.venv/bin/activate
```

## Quick Commands

```bash
# Check status
python3 ralph_wiggum.py --status

# List files
python3 ralph_wiggum.py --list

# Start print (file must be on printer)
python3 ralph_wiggum.py --start "filename.gcode"

# Slice STL
python3 ralph_wiggum.py --slice model.stl

# Full automation (slice + print)
python3 ralph_wiggum.py --slice-print model.stl

# Camera snapshot
python3 ralph_wiggum.py --camera
```

## Camera

The Flashforge Adventurer 5M has a camera connected to the main controller.

**Endpoints to try:**
```bash
curl http://10.0.0.41:8080/camera
curl http://10.0.0.41:8080/
```

## Material Settings

| Material | Nozzle | Bed | Notes |
|----------|--------|-----|-------|
| PLA | 200-210°C | 60°C | Most common |
| PETG | 230-250°C | 80°C | Stronger |
| ABS | 240-260°C | 100-110°C | Needs enclosure |

## Printer Specs

| | Adventurer 5M |
|---|---|
| Build Volume | 220×220×220mm |
| Max Nozzle Temp | 110°C |
| Max Bed Temp | 110°C |
| Connection | WiFi/Ethernet/USB |

## G-Code Commands

| Command | Description |
|---------|-------------|
| `~M105` | Get temperatures |
| `~M119` | Get status |
| `~M27` | Get print progress |
| `~M23 filename` | Select file |
| `~M24` | Start print |
| `~M25` | Pause print |
| `~M26` | Stop print |
| `~G28` | Home axes |

## Known Issues

- **Network Upload:** The Flashforge Python API may have issues from sandboxed environments. Use manual upload via FlashPrint or USB if needed.
- **Camera:** Some endpoints may require running from host machine (not sandbox).

## Files

- `ralph_wiggum.py` - Main controller script
- `WORKFLOW.md` - Detailed workflow documentation
- `SKILL.md` - This file
