---
name: snapmaker-2
description: "Control and monitor Snapmaker 2.0 3D printers via their HTTP API. Status, job management, progress watching, and event monitoring."
summary: "Snapmaker 2.0 3D printer control: status, jobs, monitoring."
version: 1.2.1
homepage: https://github.com/odrobnik/snapmaker-skill
metadata:
  {
    "openclaw":
      {
        "emoji": "🖨️",
        "requires": { "bins": ["python3"] },
      },
  }
---

# Snapmaker 2.0 Skill

Control and monitor Snapmaker 2.0 3D printers via their HTTP API.

## Features

- **Status monitoring** - Real-time printer status (temperatures, progress, position)
- **Job management** - Send, start, pause, resume, and stop print jobs
- **Safety features** - Prevents interfering with active prints without confirmation
- **Progress watching** - Live monitoring of print progress
- **Notification support** - Detect print completion, filament issues, errors

## Configuration

Create `config.json` in your workspace's `snapmaker/` folder (e.g. `~/clawd/snapmaker/config.json`).
Start from `config.json.example`.

Config format:

```json
{
  "ip": "192.168.0.32",
  "token": "your-token-here",
  "port": 8080
}
```

**Finding your token:**
Open the Snapmaker Luban app, connect to your printer, and find the token
in the connection settings. Copy it into your `config.json`.

## Usage

### Discovery

```bash
# Find Snapmaker printers on the local network (UDP broadcast, port 20054)
python3 scripts/snapmaker.py discover

# Probe a specific IP (useful across subnets)
python3 scripts/snapmaker.py discover --target 192.168.0.32

# JSON output
python3 scripts/snapmaker.py discover --json
```

Discovery uses the Snapmaker UDP broadcast protocol (no auth required).
Falls back to HTTP probe using config if UDP gets no reply (e.g. different subnet).

### Basic Commands

```bash
# Get current printer status
python3 scripts/snapmaker.py status

# Watch print progress (updates every 5 seconds)
python3 scripts/snapmaker.py watch

# Get status as JSON
python3 scripts/snapmaker.py status --json
```

### Job Control

```bash
# Send a file (prepares but doesn't start)
python3 scripts/snapmaker.py send ~/prints/model.gcode

# Send and start immediately
python3 scripts/snapmaker.py send ~/prints/model.gcode --start --yes

# Pause current print
python3 scripts/snapmaker.py pause --yes

# Resume paused print
python3 scripts/snapmaker.py resume --yes

# Stop/cancel print (requires confirmation)
python3 scripts/snapmaker.py stop
```

### Safety Flags

- `--yes` - Skip confirmation prompts (use with caution!)
- `--force` - Override safety checks (NOT RECOMMENDED)

All commands that modify state require confirmation unless `--yes` is provided.

## API Endpoints

The skill uses these Snapmaker HTTP API v1 endpoints:

- `POST /api/v1/connect` - Establish connection
- `GET /api/v1/status` - Get printer status
- `POST /api/v1/prepare_print` - Upload file
- `POST /api/v1/start_print` - Start printing
- `POST /api/v1/pause` - Pause print
- `POST /api/v1/resume` - Resume print
- `POST /api/v1/stop` - Stop/cancel print
- `GET /api/v1/print_file` - Download last file

## Status Fields

The status command returns:

- **status** - Overall state (IDLE, RUNNING, PAUSED)
- **printStatus** - Printing / Idle
- **progress** - 0.0 to 1.0
- **fileName** - Current/last file
- **currentLine** / **totalLines** - G-code progress
- **elapsedTime** / **remainingTime** - In seconds
- **nozzleTemperature1** / **nozzleTargetTemperature1**
- **heatedBedTemperature** / **heatedBedTargetTemperature**
- **x** / **y** / **z** - Current position
- **isFilamentOut** - Filament runout detection
- **isEnclosureDoorOpen** - Door state

## Notifications

To detect events:

```bash
# Watch for completion
python3 scripts/snapmaker.py watch

# Or poll status in a loop
while true; do
  python3 scripts/snapmaker.py status --json | jq -r '.printStatus'
  sleep 10
done
```

Event detection:
- **Print complete** - status == "IDLE" && progress >= 0.99
- **Filament out** - isFilamentOut == true
- **Door opened** - isEnclosureDoorOpen == true
- **Error** - Check status field for errors

## Safety Features

1. **Active print protection** - Cannot send files while printing
2. **Confirmation prompts** - All destructive actions require confirmation
3. **State validation** - Commands check printer state before executing
4. **Clear warnings** - Stop command shows prominent warning

## Examples

### Check if printer is busy
```bash
python3 scripts/snapmaker.py status | grep -q "RUNNING" && echo "Busy" || echo "Available"
```

### Get remaining time
```bash
python3 scripts/snapmaker.py status --json | jq -r '.remainingTime'
```

### Monitor temperatures
```bash
python3 scripts/snapmaker.py status --json | jq '{nozzle: .nozzleTemperature1, bed: .heatedBedTemperature}'
```

## Troubleshooting

**"Machine is not connected yet" (401 error):**
- The API requires calling `/api/v1/connect` first before any status queries
- Example: `curl -X POST "http://192.168.0.32:8080/api/v1/connect?token=YOUR_TOKEN"`
- The Python script handles this automatically on first request
- Connection establishes a session that persists until the printer is powered off
- If using raw curl commands, always call connect first

**Connection refused:**
- Verify printer IP: `ping 192.168.0.32`
- Check printer is powered on
- Ensure you're on the same network

**Invalid token:**
- Reconnect Luban to the printer (accept on touchscreen)
- Copy the new token from Luban's connection settings
- Update your `config.json`

**Can't send file:**
- Check if printer is busy: `python3 scripts/snapmaker.py status`
- Wait for current print to finish
- Use `--force` only if absolutely necessary

## References

- [Snapmaker Forum: Auto-start Guide](https://forum.snapmaker.com/t/guide-automatic-start-via-drag-drop/29177)
- [Snapmaker Forum: API Documentation](https://forum.snapmaker.com/t/documentation-of-the-web-api/20976/16)

## Dependencies

- Python 3.6+
- `requests` library (install: `pip3 install requests`)

## License

Part of OpenClaw skills collection.
