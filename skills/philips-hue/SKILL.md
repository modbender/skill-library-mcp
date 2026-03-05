---
name: philips-hue
description: Local control of Philips Hue lights via API v1.
homepage: https://developers.meethue.com/
metadata: {"clawdbot":{"emoji":"💡","requires":{"bins":["curl","jq","python3"]}}}
---

# Philips Hue Skill

Local control of Philips Hue lights via API v1.

## Installation & Configuration

### 1. Prerequisites
- A Philips Hue Bridge on the same local network.
- `curl`, `jq`, and `python3` installed on your system.

### 2. Configure .env file
Create a `.env` file in the skill directory:
```bash
BRIDGE_IP=192.168.1.XX  # Your bridge IP
USERNAME=your_api_key   # Obtained after pairing
```

### 3. Pairing (Obtain an API key)
If you don't have a `USERNAME`, follow these steps:
1. Press the physical button on your Hue Bridge.
2. Run a test command; the script will guide you or you can use a setup tool to register "OpenClaw" as a new devicetype.

## Usage

The `hue.sh` script is designed to be fast and flexible. It allows combining multiple actions in a single command.

### Basic Commands
```bash
# Turn On / Off
./hue.sh light 1 on
./hue.sh light 1 off

# See status of all lights
./hue.sh status
```

### Advanced Control (Chaining)
You can combine color, hex codes, and brightness:
```bash
# Turn on in blue at 50% brightness
./hue.sh light 1 on color blue bri 50

# Use HTML Hex codes (e.g., #3399FF)
./hue.sh light 1 color "#3399FF"

# Change color only
./hue.sh light 1 color red

# Precise setting (Brightness 0-100, Hue 0-65535, Sat 0-254)
./hue.sh light 1 bri 80 sat 200 hue 15000
```

### Supported Colors
- **Named:** `red`, `blue`, `green`, `yellow`, `orange`, `pink`, `purple`, `white`, `warm`, `cold`.
- **Hex:** Any HTML color code starting with `#` (e.g., `"#FF5733"`). Always wrap in quotes.

## Skill Structure
- `hue.sh`: The control engine (Shell).
- `.env`: Your secrets (IP and API Key).
- `SKILL.md`: This documentation.

---
💡 **Tip:** For ultra-fast access, add a reminder of these commands in your `TOOLS.md` file at the root of your workspace.
