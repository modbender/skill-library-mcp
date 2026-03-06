---
name: device-control
description: Expose safe device actions (volume, brightness, open/close apps) for personal automation.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎛️",
        "requires": { "bins": ["node"] },
        "version": "1.1.0",
      },
  }
---

# Device Control Skill

Control device volume, brightness, and applications via command line. Supports Linux, macOS, Windows, and WSL.

## Security

All inputs are validated and sanitized to prevent command injection:
- Volume/brightness values must be numbers between 0-100
- App names are restricted to alphanumeric characters, spaces, dashes, and underscores
- Shell metacharacters are blocked

## Tool API

### device_control
Execute a device control action.

- **Parameters:**
  - `action` (string, required): One of `set_volume`, `change_volume`, `set_brightness`, `open_app`, `close_app`.
  - `value` (string/number, optional): The value for the action (0-100 for volume/brightness, delta for change_volume).
  - `app` (string, optional): The application name or path (required for open/close actions).

**Usage:**

```bash
# Set volume to 50%
node skills/device-control/ctl.js --action set_volume --value 50

# Change volume by +10 or -10
node skills/device-control/ctl.js --action change_volume --value 10
node skills/device-control/ctl.js --action change_volume --value -10

# Set brightness to 75%
node skills/device-control/ctl.js --action set_brightness --value 75

# Open an application
node skills/device-control/ctl.js --action open_app --app "firefox"
node skills/device-control/ctl.js --action open_app --app "Visual Studio Code"

# Close an application
node skills/device-control/ctl.js --action close_app --app "firefox"
```

## Platform Support

| Action | Linux | macOS | Windows | WSL |
|--------|-------|-------|---------|-----|
| set_volume | ✅ (pactl/amixer) | ✅ (osascript) | ✅ (nircmd) | ✅ (nircmd) |
| change_volume | ✅ | ✅ | ❌ | ❌ |
| set_brightness | ✅ (brightnessctl) | ⚠️ (requires brightness CLI) | ✅ (WMI) | ✅ (WMI) |
| open_app | ✅ | ✅ | ✅ | ✅ |
| close_app | ✅ (pkill) | ✅ (pkill) | ✅ (taskkill) | ✅ (taskkill) |

## Requirements

- **Linux:** `pactl` (PulseAudio) or `amixer` (ALSA), `brightnessctl` (optional, for brightness)
- **macOS:** Built-in osascript, `brightness` CLI tool (optional, for brightness)
- **Windows/WSL:** `nircmd.exe` for volume control (download from nirsoft.net)
