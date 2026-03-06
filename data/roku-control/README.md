# Roku Control

Control your Roku TV or streaming device directly over your local network. No cloud services, no authentication, no complex setup - just fast, reliable local control.

## Features

✅ **Automatic Discovery** - Find all Roku devices on your network  
✅ **Full Remote Control** - Navigate menus, control playback, adjust volume  
✅ **App Launching** - Open Netflix, YouTube, Hulu, and any installed app  
✅ **Power Control** - Turn TV on/off remotely  
✅ **Text Input** - Fast text entry for searches  
✅ **Works Offline** - No internet required, purely local network control  

## Quick Start

### 1. Install Dependencies

```bash
pip3 install requests
```

### 2. Discover Your Roku

```bash
python3 scripts/roku_control.py discover
```

This will show all Roku devices on your network:

```json
[
  {
    "ip": "192.168.1.100",
    "name": "Living Room TV",
    "model": "Hisense•Roku TV",
    "serial": "X00100XXXXX"
  }
]
```

### 3. Test Control

```bash
# Get device info
python3 scripts/roku_control.py --ip 192.168.1.100 info

# Press the Home button
python3 scripts/roku_control.py --ip 192.168.1.100 key Home

# Launch Netflix
python3 scripts/roku_control.py --ip 192.168.1.100 launch Netflix
```

## Usage Examples

### Navigation

```bash
# Navigate menus
python3 scripts/roku_control.py --ip 192.168.1.100 key Up
python3 scripts/roku_control.py --ip 192.168.1.100 key Down
python3 scripts/roku_control.py --ip 192.168.1.100 key Select

# Go home or back
python3 scripts/roku_control.py --ip 192.168.1.100 key Home
python3 scripts/roku_control.py --ip 192.168.1.100 key Back
```

### Playback

```bash
# Control playback
python3 scripts/roku_control.py --ip 192.168.1.100 key Play
python3 scripts/roku_control.py --ip 192.168.1.100 key Pause
python3 scripts/roku_control.py --ip 192.168.1.100 key Rev
python3 scripts/roku_control.py --ip 192.168.1.100 key Fwd
```

### Apps

```bash
# Launch apps by name
python3 scripts/roku_control.py --ip 192.168.1.100 launch Netflix
python3 scripts/roku_control.py --ip 192.168.1.100 launch YouTube
python3 scripts/roku_control.py --ip 192.168.1.100 launch "Disney Plus"

# Or by app ID (faster)
python3 scripts/roku_control.py --ip 192.168.1.100 launch 12  # Netflix

# List all installed apps
python3 scripts/roku_control.py --ip 192.168.1.100 apps
```

### Volume & Power

```bash
# Volume control
python3 scripts/roku_control.py --ip 192.168.1.100 key VolumeUp
python3 scripts/roku_control.py --ip 192.168.1.100 key VolumeDown
python3 scripts/roku_control.py --ip 192.168.1.100 key VolumeMute

# Power control
python3 scripts/roku_control.py --ip 192.168.1.100 key PowerOff
python3 scripts/roku_control.py --ip 192.168.1.100 key PowerOn
```

### Search

```bash
# Send text for search (much faster than individual key presses)
python3 scripts/roku_control.py --ip 192.168.1.100 text "Breaking Bad"
```

## Configuration

For convenience, save your Roku IP addresses in `references/roku.json`:

```json
{
  "living_room": {
    "ip": "192.168.1.100",
    "name": "Living Room TV",
    "model": "Roku Ultra"
  },
  "bedroom": {
    "ip": "192.168.1.101",
    "name": "Bedroom Roku",
    "model": "Roku Streaming Stick+"
  }
}
```

Then reference them by friendly name in your automation scripts.

## Natural Language Examples

When translating user requests to commands:

| User Says | Command |
|-----------|---------|
| "Turn on the TV" | `key PowerOn` |
| "Open Netflix" | `launch Netflix` |
| "Go to YouTube" | `launch YouTube` |
| "Turn up the volume" | `key VolumeUp` |
| "Pause" | `key Pause` |
| "Go back" | `key Back` |
| "Search for The Office" | `text "The Office"` |

## Technical Details

**Protocol:** Roku External Control Protocol (ECP)  
**Communication:** Local HTTP REST API on port 8060  
**Discovery:** SSDP multicast on 239.255.255.250:1900  
**Authentication:** None required  
**Internet:** Not needed after initial setup  

## Compatibility

✅ All Roku devices (TV, Ultra, Streaming Stick, Express, etc.)  
✅ Works with any Roku OS version  
⚠️ Volume/power commands require Roku TV or HDMI-CEC setup  
⚠️ Device must be on same network/subnet as OpenClaw  

## Troubleshooting

**Discovery not working?**
- Ensure Roku is powered on and connected to network
- Check both devices are on same subnet
- Some routers block SSDP - use manual IP if needed
- Find IP in Roku Settings → Network → About

**Commands timeout?**
- Verify IP address: `ping <roku-ip>`
- Check port 8060 is accessible: `curl http://<roku-ip>:8060`
- Roku may have changed IP (use DHCP reservation)

**Volume not working?**
- Volume keys only work on Roku TVs
- Roku sticks need HDMI-CEC configured
- Check TV volume control settings

## Contributing

Found a bug or have a feature request? Open an issue on GitHub or submit a pull request!

## License

MIT License - Free to use, modify, and distribute.

## Credits

Built for the OpenClaw community. Uses Roku's official ECP protocol.
