---
name: roku-control
description: "Control Roku devices via local network (ECP protocol). Use when the user wants to control their Roku TV or streaming device, change channels, launch apps (Netflix, YouTube, Hulu, etc.), navigate menus, adjust volume, play/pause content, search for shows, or power off. Works over LAN with no authentication required."
---

# Roku Control

Control Roku devices over your local network using the External Control Protocol (ECP). No authentication, cloud services, or complex setup required - just local HTTP commands.

## Prerequisites

- Roku device on the same network as OpenClaw
- Roku's IP address (can be discovered automatically)

## Setup (First Time)

**1. Discover your Roku:**

```bash
python3 scripts/roku_control.py discover
```

This will show all Roku devices on your network with their IP addresses.

**2. Save the IP address:**

Note your Roku's IP (e.g., `192.168.1.100`) for use in commands.

**3. Test connectivity:**

```bash
python3 scripts/roku_control.py --ip 192.168.1.100 info
```

## Common Operations

### Device Information

```bash
# Get device details
python3 scripts/roku_control.py --ip 192.168.1.100 info

# List all installed apps
python3 scripts/roku_control.py --ip 192.168.1.100 apps

# See what's currently playing
python3 scripts/roku_control.py --ip 192.168.1.100 active
```

### Navigation & Control

```bash
# Navigate menus
python3 scripts/roku_control.py --ip 192.168.1.100 key Up
python3 scripts/roku_control.py --ip 192.168.1.100 key Down
python3 scripts/roku_control.py --ip 192.168.1.100 key Left
python3 scripts/roku_control.py --ip 192.168.1.100 key Right
python3 scripts/roku_control.py --ip 192.168.1.100 key Select

# Go home
python3 scripts/roku_control.py --ip 192.168.1.100 key Home

# Go back
python3 scripts/roku_control.py --ip 192.168.1.100 key Back
```

### Playback

```bash
# Play/pause
python3 scripts/roku_control.py --ip 192.168.1.100 key Play
python3 scripts/roku_control.py --ip 192.168.1.100 key Pause

# Rewind/fast forward
python3 scripts/roku_control.py --ip 192.168.1.100 key Rev
python3 scripts/roku_control.py --ip 192.168.1.100 key Fwd

# Instant replay (back 10 seconds)
python3 scripts/roku_control.py --ip 192.168.1.100 key InstantReplay
```

### Volume & Power

```bash
# Volume control (Roku TV or HDMI-CEC enabled)
python3 scripts/roku_control.py --ip 192.168.1.100 key VolumeUp
python3 scripts/roku_control.py --ip 192.168.1.100 key VolumeDown
python3 scripts/roku_control.py --ip 192.168.1.100 key VolumeMute

# Power off
python3 scripts/roku_control.py --ip 192.168.1.100 key PowerOff
```

### Launch Apps

```bash
# Launch by app ID (faster)
python3 scripts/roku_control.py --ip 192.168.1.100 launch 12  # Netflix

# Launch by app name (case-insensitive)
python3 scripts/roku_control.py --ip 192.168.1.100 launch Netflix
python3 scripts/roku_control.py --ip 192.168.1.100 launch YouTube
python3 scripts/roku_control.py --ip 192.168.1.100 launch "Disney+"
```

### Search & Text Input

```bash
# Send search text
python3 scripts/roku_control.py --ip 192.168.1.100 text "Breaking Bad"

# This is much faster than individual key presses for searches
```

## Natural Language Translation

Map user requests to commands:

**Navigation:**
- "Go to home screen" → `key Home`
- "Go back" → `key Back`
- "Scroll down" / "Move down" → `key Down`
- "Select this" / "Click" → `key Select`

**Playback:**
- "Play" / "Resume" → `key Play`
- "Pause" → `key Pause`
- "Rewind" → `key Rev`
- "Fast forward" → `key Fwd`
- "Go back 10 seconds" / "Replay that" → `key InstantReplay`

**Volume:**
- "Turn up the volume" → `key VolumeUp`
- "Turn down the volume" → `key VolumeDown`
- "Mute" / "Unmute" → `key VolumeMute`

**Apps:**
- "Open Netflix" → `launch Netflix`
- "Launch YouTube" → `launch YouTube`
- "Start Hulu" → `launch Hulu`

**Search:**
- "Search for Breaking Bad" → `text "Breaking Bad"`
- "Find Stranger Things" → Open search + send text

**Power:**
- "Turn off the TV" → `key PowerOff`

## Common App IDs

See [references/common-apps.md](references/common-apps.md) for a comprehensive list.

Quick reference:
- Netflix: 12
- YouTube: 837
- Hulu: 2285
- Disney+: 291097
- Amazon Prime Video: 13
- HBO Max: 61322
- The Roku Channel: 151908

To get app IDs for your specific Roku:
```bash
python3 scripts/roku_control.py --ip <ip> apps
```

## Complete Key Reference

See [references/remote-keys.md](references/remote-keys.md) for all supported remote keys.

Common keys: `Home`, `Back`, `Up`, `Down`, `Left`, `Right`, `Select`, `Play`, `Pause`, `Rev`, `Fwd`, `VolumeUp`, `VolumeDown`, `VolumeMute`, `PowerOff`, `Search`, `Info`

## Advanced Workflows

### Watch Netflix

```bash
# Go home, launch Netflix
python3 scripts/roku_control.py --ip 192.168.1.100 key Home
sleep 1
python3 scripts/roku_control.py --ip 192.168.1.100 launch 12
```

### Search and Play

```bash
# Open search, send text, select first result
python3 scripts/roku_control.py --ip 192.168.1.100 key Search
sleep 1
python3 scripts/roku_control.py --ip 192.168.1.100 text "The Office"
sleep 1
python3 scripts/roku_control.py --ip 192.168.1.100 key Select
```

### Quick Replay

```bash
# Go back 10 seconds and resume
python3 scripts/roku_control.py --ip 192.168.1.100 key InstantReplay
sleep 1
python3 scripts/roku_control.py --ip 192.168.1.100 key Play
```

### Movie Night Setup

```bash
# Launch streaming app, adjust volume
python3 scripts/roku_control.py --ip 192.168.1.100 launch "Disney+"
sleep 2
python3 scripts/roku_control.py --ip 192.168.1.100 key VolumeDown
python3 scripts/roku_control.py --ip 192.168.1.100 key VolumeDown
```

## Device Mapping

Store your Roku IP in `references/roku.json`:

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

Then reference by friendly name in conversations.

## Troubleshooting

**"No Roku devices found"**
- Ensure Roku is powered on and connected to network
- Check that OpenClaw and Roku are on same network/subnet
- Some routers block SSDP discovery - try manual IP if known
- Verify Roku's network settings in Settings → Network

**"Connection timeout"**
- Verify IP address is correct
- Ping the Roku: `ping <roku-ip>`
- Check firewall isn't blocking port 8060
- Roku may have changed IP (use DHCP reservation)

**"Key not working"**
- Some keys only work on Roku TVs (volume, power, inputs)
- Volume keys require HDMI-CEC or Roku TV
- Power commands may not be supported on older devices
- Check [references/remote-keys.md](references/remote-keys.md) for compatibility

**App won't launch**
- Verify app is installed: run `apps` command
- Use correct app ID (case-sensitive for name matching)
- Some apps require additional authentication in their own UI

**Discovery not finding device**
- Try manual IP if you know it: check router DHCP leases
- Roku's IP is shown in Settings → Network → About
- Set static IP or DHCP reservation for reliability

## Integration with Other Skills

### Movie Night Routine

Combine with Govee lights skill:

```bash
# Dim lights
for light in "living room" "tv lights"; do
  python3 govee-lights/scripts/govee_control.py brightness "$light" 15
  python3 govee-lights/scripts/govee_control.py temp "$light" 2700
done

# Launch streaming app
python3 roku-control/scripts/roku_control.py --ip 192.168.1.100 launch Netflix

# Set comfortable volume
python3 roku-control/scripts/roku_control.py --ip 192.168.1.100 key VolumeDown
```

## Notes

- ECP protocol works entirely over LAN (no internet required)
- No authentication or API keys needed
- Commands are instant (local network speed)
- Multiple Roku devices can be controlled independently
- Works with Roku TVs, streaming sticks, and boxes
- Power-on commands not supported (ECP limitation - Roku must be awake)
- For power-on, use HDMI-CEC or network wake features if available

## Limitations

- Cannot power on a fully-off Roku (ECP only works when device is on)
- Volume/power commands limited to Roku TVs or HDMI-CEC setups
- No feedback on success/failure for some commands
- Text input is character-by-character (slower for long searches)
- Discovery requires SSDP (some networks block multicast)
