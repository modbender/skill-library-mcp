---
name: alexa-remote
description: Control Alexa devices via CLI - set alarms, play music, flash briefings, smart home commands. Use when asked to set an alarm, play something on Echo, control smart home devices, or send voice commands to Alexa.
---

# Alexa Remote Control

Control Amazon Echo devices via shell commands using [alexa-remote-control](https://github.com/adn77/alexa-remote-control).

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/adn77/alexa-remote-control.git
cd alexa-remote-control
```

### 2. Get a refresh token

The script needs a refresh token from Amazon. Use [alexa-cookie-cli](https://github.com/adn77/alexa-cookie-cli):

```bash
npx alexa-cookie-cli
```

This opens a browser for Amazon login. After authentication, copy the `refreshToken` (starts with `Atnr|...`).

### 3. Create a wrapper script

Create `alexa-alarm.sh` (or similar) with credentials:

```bash
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TIME="${1:-7:00 am}"
DEVICE="${2:-Bedroom Echo Show}"

export REFRESH_TOKEN='Atnr|YOUR_TOKEN_HERE'
export AMAZON='amazon.co.uk'      # or amazon.com for US
export ALEXA='alexa.amazon.co.uk' # or alexa.amazon.com

"$SCRIPT_DIR/alexa_remote_control.sh" -d "$DEVICE" -e "textcommand:Set an alarm for $TIME"
```

Make executable: `chmod +x alexa-alarm.sh`

## Usage

### Set alarms

```bash
./alexa-alarm.sh "6:30 am"                    # Default device
./alexa-alarm.sh "7:00 am" "Kitchen Echo"     # Specific device
```

### Generic commands

```bash
# Play flash briefing (news)
./alexa_remote_control.sh -d "Bedroom Echo Show" -e "textcommand:Play my flash briefing"

# Play music
./alexa_remote_control.sh -d "Kitchen Echo" -e "textcommand:Play BBC Radio 6"

# Smart home
./alexa_remote_control.sh -d "Living Room Echo" -e "textcommand:Turn off the lights"

# Weather
./alexa_remote_control.sh -d "Bedroom Echo Show" -e "textcommand:What's the weather"

# Timer
./alexa_remote_control.sh -d "Kitchen Echo" -e "textcommand:Set a timer for 10 minutes"
```

### List devices

```bash
./alexa_remote_control.sh -a  # Lists all devices with names/types
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `REFRESH_TOKEN` | Amazon auth token | `Atnr|EwMDI...` |
| `AMAZON` | Amazon domain | `amazon.co.uk` / `amazon.com` |
| `ALEXA` | Alexa domain | `alexa.amazon.co.uk` |

## Notes

- Token expires periodically; re-run `alexa-cookie-cli` if auth fails
- Device names are case-sensitive; use `-a` to check exact names
- UK users: use `amazon.co.uk` / `alexa.amazon.co.uk`
- US users: use `amazon.com` / `alexa.amazon.com`
