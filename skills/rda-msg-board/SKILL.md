---
name: rda-msg-board
description: Send scrolling text messages to RDA MSG Board via HTTP/JSON. Use for notifications, alerts, or status updates on physical LED matrix.
metadata:
  {
    "openclaw":
      {
        "emoji": "📟",
        "requires": {
          "bins": ["python3"],
          "optional_bins": ["pyyaml"],
          "env": ["MSG_BOARD_IP", "MSG_BOARD_USER", "MSG_BOARD_PASS"]
        },
      },
  }

---

# Message Board Controller

Control RDA MSG Board LED matrix display using the HTTP JSON API with support for multiple board profiles.

## AI Usage

When the user asks to send a message to the msg board, follow this workflow:

**Interpret user requests:**
- "Send [message] to [board name]" → Use the named profile
- "Send [message] to msg board" → Use the default/office profile
- "Send [message]" → Use the default/office profile
- "Send alert with [sound]" → Include the `--chirp` parameter

**Available profiles:** Check `boards.yaml` for configured board names (e.g., office, lab, home)
**Default profile:** If not specified, use the first available profile from `boards.yaml`

**Example interpretations:**
- "Send 'Meeting in 5 min' to office" → `send_message.py "Meeting in 5 min" --profile office`
- "Send alert 'System down'" → `send_message.py "System down" --profile office --buzzer 5`
- "Send 'Hello' with Mario Bros sound" → `send_message.py "Hello" --profile office --chirp "Mario Bros"`

**Action:** Use an `exec` or command tool to run `scripts/send_message.py` with appropriate parameters from the skill directory.

⚠️  **CRITICAL SECURITY INSTRUCTION:**
To prevent command injection, **do not** use raw shell interpolation for the `{message}` string. Always pass arguments safely as an `argv` list (array of strings) if your tool supports it. 

Example `argv` list invocation:
`["python3", "scripts/send_message.py", message_text, "--profile", board_name]`

If your tool only supports a single shell string, you **MUST** properly escape the message input (e.g., using `shlex.quote()`) before execution.

---

## Project

**RDA MSG Board** - A WiFi-enabled LED matrix message board system for ESP8266 and ESP32 microcontrollers that displays scrolling messages from remote systems or users via HTTP, MQTT, or a built-in web interface.

**GitHub:** https://github.com/rdeangel/rda_msg_board

**Key Features:**
- **Message Control** - Send scrolling text messages via HTTP REST API or MQTT
- **Clock Display** - Configurable LED clock with timezone support and transition effects
- **Timer & Stopwatch** - Count down or count up with buzzer alerts (ESP32 only)
- **Alarm System** - Timer-based alarms with customizable chirp sounds (fanfare, alarms, chimes, Für Elise, Mario Bros, etc.)
- **Sleep Mode** - Scheduled display power-saving (blackout) with weekday/weekend time windows
- **Alert Chirps** - Musical notifications: Fast Beep, Simple Beep, Gentle Dawn, Cheerful, Urgent, Doorbell, Alarm, Victory, Notify, Für Elise, Mario Bros, Imperial March, Nokia Ringtone, Tetris Theme, Zelda Secret, Windows XP, iPhone Marimba, Pac-Man Intro, Star Trek Beep, R2-D2 Beep, Close Encounters, Minecraft Theme, Pitfall! Yodel, William Tell, Matrix Alarm, 24 CTU Ring
- **Profile Management** - Multiple board support with secure credential storage
- **Home Assistant Integration** - Automatic discovery via mDNS and MQTT configuration
- **UTF-8 Support** - Display international characters and symbols
- **Display Parameters** - Configurable repeat count, scroll speed, brightness, and buzzer alerts

**Communication Methods:**
- HTTP REST API (GET URL-encoded, POST JSON)
- MQTT (topic subscriptions, wildcard support, anonymous or authenticated)
- Web Interface (responsive GUI with AJAX updates)
- Home Assistant (Zero-config discovery)

---

## Requirements

### Optional (for profile support)
- **PyYAML**: `pip install pyyaml` (enables profile-based configuration)

### Environment Variables (fallback)
These are only needed if not using profiles:

| Variable | Description | Default |
|----------|-------------|---------|
| `MSG_BOARD_IP` | Device IP or Hostname | *Required* |
| `MSG_BOARD_USER` | Web Interface Username | `admin` |
| `MSG_BOARD_PASS` | Web Interface Password | `msgboard` |

## Board Profiles

Profiles are stored in `boards.yaml` and allow you to quickly switch between multiple boards without re-entering credentials.

### Setup (First Time)

1. **Copy sample configuration:**
```bash
cp boards.yaml.sample boards.yaml
```

2. **Edit with your board details:**
```bash
nano boards.yaml
# or use: python3 scripts/manage_boards.py add office --ip 192.168.1.88 --user admin --pass msgboard
```

3. **Verify the profile:**
```bash
python3 scripts/manage_boards.py list
```

4. **Send a message using the profile:**
```bash
python3 scripts/send_message.py "Hello World" --profile main
```

### Managing Profiles

**List all configured boards:**
```bash
python3 scripts/manage_boards.py list
```

**Add a new board:**
```bash
python3 scripts/manage_boards.py add office --ip 10.0.0.50 --user rda --pass secure123
```

**Remove a board profile:**
```bash
python3 scripts/manage_boards.py remove office
```

**Update existing profile:**
```bash
python3 scripts/manage_boards.py add main --ip 192.168.1.101 --force
```

## Usage

### Using Profiles (Recommended)
Send a message to a named profile:
```bash
python3 scripts/send_message.py "Hello World" --profile main
python3 scripts/send_message.py "Alert: High CPU" --profile office --buzzer 5 --brightness 10
```

**List available profiles:**
```bash
python3 scripts/send_message.py --list-profiles
```

### Direct Connection (Ad-hoc)
Override profile or use direct connection:
```bash
python3 scripts/send_message.py "Hello World" --ip 192.168.1.100 --user admin --pass msgboard
python3 scripts/send_message.py "Test" --profile main --ip 192.168.1.101  # Override IP
```

### Alerts & Notifications
Send a high-priority alert with buzzer sounds and high brightness:
```bash
python3 scripts/send_message.py "ALERT: System Failure" --profile main --buzzer 10 --brightness 15 --delay 20
```

### Configuration Options
| Option | Description | Default |
|--------|-------------|---------|
| `--profile <name>` | Board profile name (from boards.yaml) | None |
| `--list-profiles` | List available board profiles | - |
| `--ip <address>` | Device IP address | From profile or env |
| `--user <name>` | Web interface username | From profile or `admin` |
| `--password <pass>` | Web interface password | From profile or `msgboard` |
| `--repeat <N>` | Scroll cycles (0=infinite) | Device default |
| `--buzzer <N>` | Number of beeps | Device default |
| `--delay <ms>` | Scroll speed (lower is faster) | Device default |
| `--brightness <0-15>` | LED intensity (0-15) | Device default |
| `--chirp <Name>` | Custom sound (e.g., 'Mario Bros') | Device default |

### Available Chirps
All available options: `Silent`, `Fast Beep`, `Simple Beep`, `Gentle Dawn`, `Cheerful`, `Urgent`, `Beep`, `Quick Tap`, `Double`, `Triple`, `Doorbell`, `Alarm`, `Victory`, `Notify`, `For Elise`, `Mario Bros`, `Imperial March`, `Nokia Ringtone`, `Tetris Theme`, `Zelda Secret`, `Windows XP`, `iPhone Marimba`, `Pac-Man Intro`, `Star Trek Beep`, `R2-D2 Beep`, `Close Encounters`, `Minecraft Theme`, `Pitfall! Yodel`, `William Tell`, `Matrix Alarm`, `24 CTU Ring`.

### Stop Display
To clear the display immediately:
```bash
python3 scripts/send_message.py "" --profile main
```

## Troubleshooting

- **Status 204**: The board returns HTTP 204 on success. This is normal.
- **Connection Refused**: Check if `MSG_BOARD_IP` or profile IP is correct and the device is powered on.
- **Profile not found**: Use `--list-profiles` to see available profiles.
- **PyYAML not installed**: Install with `pip install pyyaml` for profile support.
- **Cannot load profiles**: Ensure `boards.yaml` exists (copy from `boards.yaml.sample`) and has valid YAML syntax.
