---
name: android-agent — AI-Powered Android Phone Control
description: Got an old Android in a drawer? Connect it to any machine running
  OpenClaw — your gateway, a Mac Mini, a Raspberry Pi. Your AI can now open
  apps, tap buttons, type text, and complete tasks on a rea...
---

# android-agent — AI-Powered Android Phone Control

> Plug your old Android phone into your Mac/PC. Now your AI assistant can use it.

Got an old Android in a drawer? Connect it to any machine running OpenClaw — your gateway, a Mac Mini, a Raspberry Pi. Your AI can now open apps, tap buttons, type text, and complete tasks on a real phone. Book a cab, order food, check your bank app — anything you'd do with your thumbs.

## How It Works

Your AI agent sees the phone screen (via screenshots), decides what to tap/type/swipe, and executes actions via ADB. Under the hood it uses [DroidRun](https://github.com/droidrun/droidrun) with GPT-4o vision.

```
┌─────────────┐    screenshots    ┌──────────────┐    ADB commands    ┌─────────────┐
│  GPT-4o     │◄─────────────────│  DroidRun    │──────────────────►│  Android    │
│  Vision     │─────────────────►│  Agent       │◄──────────────────│  Phone      │
│             │   tap/type/swipe  │              │    screen state    │             │
└─────────────┘                   └──────────────┘                    └─────────────┘
```

## Works Two Ways

### Direct Mode
Phone plugged into your OpenClaw gateway machine via USB. Zero networking required.

```
[Gateway Machine] ──USB──► [Android Phone]
```

### Node Mode
Phone plugged into a Mac Mini, Raspberry Pi, or any OpenClaw node. The gateway controls it over the network.

```
[Gateway] ──network──► [Mac Mini / Pi node] ──USB──► [Android Phone]
```

For Node mode, connect ADB over TCP/WiFi so the node can forward commands.

## Quick Start (3 steps)

### 1. Enable USB Debugging
On your Android phone:
- Go to **Settings → About Phone**
- Tap **Build Number** 7 times to enable Developer Options
- Go to **Settings → Developer Options**
- Enable **USB Debugging**

### 2. Connect & Install
```bash
# Plug phone in via USB, then:
pip install -r requirements.txt
adb devices  # verify phone shows up — authorize on phone if prompted
```

### 3. Run Your First Task
```bash
export OPENAI_API_KEY="sk-..."
python scripts/run-task.py "Open Settings and turn on Dark Mode"
```

That's it. The script handles everything: waking the screen, unlocking, keeping the display on, and running your task.

## What Can It Do?

### 📱 Daily Life
```bash
python scripts/run-task.py "Order an Uber to the airport"
python scripts/run-task.py "Set an alarm for 6 AM tomorrow"
python scripts/run-task.py "Check my bank balance on PhonePe"
python scripts/run-task.py "Open Google Maps and navigate to the nearest coffee shop"
```

### 💬 Messaging
```bash
python scripts/run-task.py "Send a WhatsApp message to Mom saying I'll be late"
python scripts/run-task.py "Read my latest SMS messages"
python scripts/run-task.py "Open Telegram and check unread messages"
```

### 🛒 Shopping
```bash
python scripts/run-task.py "Open Amazon and search for wireless earbuds under 2000 rupees"
python scripts/run-task.py "Add milk and bread to my Instamart cart"
```

### 📅 Productivity
```bash
python scripts/run-task.py "Open Google Calendar and check my schedule for tomorrow"
python scripts/run-task.py "Create a new note in Google Keep: Buy groceries"
```

### 🎵 Entertainment
```bash
python scripts/run-task.py "Play my Discover Weekly playlist on Spotify"
python scripts/run-task.py "Open YouTube and search for lo-fi study music"
```

### ⚙️ Settings & Setup
```bash
python scripts/run-task.py "Turn on Dark Mode"
python scripts/run-task.py "Connect to my home WiFi network"
python scripts/run-task.py "Enable Do Not Disturb mode"
python scripts/run-task.py "Turn off Bluetooth"
```

### 📸 Utilities
```bash
python scripts/run-task.py "Take a screenshot"
python scripts/run-task.py "Open the camera and take a photo"
python scripts/run-task.py "Clear all notifications"
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | **Yes** | API key for GPT-4o vision |
| `ANDROID_SERIAL` | No | Device serial number. Auto-detected if only one device is connected |
| `ANDROID_PIN` | No | Phone PIN/password for auto-unlock. If not set, unlock is skipped |
| `DROIDRUN_TIMEOUT` | No | Task timeout in seconds (default: 120) |

## Setup Details

### Direct Mode (USB)

1. Install ADB:
   ```bash
   # macOS
   brew install android-platform-tools

   # Ubuntu/Debian
   sudo apt install android-tools-adb

   # Windows
   # Download from https://developer.android.com/tools/releases/platform-tools
   ```

2. Connect phone via USB and verify:
   ```bash
   ./scripts/connect.sh usb
   ```

3. Install DroidRun Portal APK on the phone:
   - Download from [DroidRun releases](https://github.com/droidrun/droidrun/releases)
   - Or sideload: `adb install droidrun-portal.apk`
   - Open the Portal app on the phone and grant accessibility permissions

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Node Mode (Remote via WiFi/TCP)

1. On the node machine (Mac Mini, Pi, etc.), connect the phone via USB and enable WiFi ADB:
   ```bash
   adb tcpip 5555
   adb connect <phone-ip>:5555
   ```

2. From your gateway, connect to the node's ADB:
   ```bash
   # If using SSH tunnel:
   ssh -L 15555:<phone-ip>:5555 user@node-ip
   export ANDROID_SERIAL="127.0.0.1:15555"

   # Or direct WiFi (same network):
   ./scripts/connect.sh wifi <phone-ip>
   ```

3. Run tasks as normal — the script uses whatever `ANDROID_SERIAL` points to.

### DroidRun Portal Setup

The DroidRun Portal APK must be installed and running on the phone. It provides the accessibility service that allows DroidRun to read screen content and interact with UI elements.

1. Install the APK (download from DroidRun GitHub releases)
2. Open the Portal app
3. Grant **Accessibility Service** permission when prompted
4. Keep it running in the background

## Script Reference

### `scripts/run-task.py` — The Main Script

```bash
# Basic usage
python scripts/run-task.py "Your task description here"

# With options
python scripts/run-task.py --timeout 180 "Install Spotify from Play Store"
python scripts/run-task.py --model gpt-4o "Open Chrome and search for weather"
python scripts/run-task.py --no-unlock "Take a screenshot"
python scripts/run-task.py --serial 127.0.0.1:15555 "Check notifications"
python scripts/run-task.py --verbose "Open Settings"
```

**Options:**
| Flag | Description |
|------|-------------|
| `goal` | Task description (positional, required) |
| `--timeout` | Timeout in seconds (default: 120, or `DROIDRUN_TIMEOUT` env) |
| `--model` | LLM model to use (default: gpt-4o) |
| `--no-unlock` | Skip the auto-unlock step |
| `--serial` | Device serial (default: `ANDROID_SERIAL` env or auto-detect) |
| `--verbose` | Show detailed debug output |

### `scripts/connect.sh` — Setup & Verify Connection

```bash
./scripts/connect.sh          # Auto-detect USB device
./scripts/connect.sh usb      # USB mode (explicit)
./scripts/connect.sh wifi 192.168.1.100  # WiFi/TCP mode
```

### `scripts/screenshot.sh` — Screenshot (ADB `screencap`, reliable)

DroidRun’s internal screenshot sometimes fails on certain devices. Use this to bypass DroidRun and capture a PNG directly via ADB.

```bash
# Save to /tmp/android-screenshot.png
./scripts/screenshot.sh

# Explicit serial + output path
./scripts/screenshot.sh 127.0.0.1:15555 /tmp/a03.png
```

You can also do it from Python:

```bash
python scripts/run-task.py --screenshot --serial 127.0.0.1:15555 --screenshot-path /tmp/a03.png
```

### `scripts/status.sh` — Device Status

```bash
./scripts/status.sh
# Output:
# 📱 Device: Samsung Galaxy A03 (SM-A035F)
# 🤖 Android: 11 (API 30)
# 🔋 Battery: 87%
# 📺 Screen: ON (unlocked)
# 🔌 Connection: USB
# 📦 DroidRun Portal: installed (v0.5.5)
```

## Troubleshooting

### "no devices/emulators found"
- Check USB cable (use a data cable, not charge-only)
- Authorize the computer on your phone's USB debugging prompt
- Try `adb kill-server && adb start-server`

### "device unauthorized"
- Disconnect and reconnect USB
- Check the phone screen for an authorization dialog
- If no dialog appears, revoke USB debugging authorizations in Developer Options and reconnect

### Phone screen turns off during task
- The script sets keep-awake mode automatically, but some phones override this
- Manually: Settings → Developer Options → Stay Awake (while charging)

### Task fails with dialog/popup blocking
- The script tries to dismiss common dialogs automatically
- For persistent popups, dismiss them manually first, then retry
- Use `--verbose` to see what the agent is seeing

### WiFi ADB disconnects after reboot
- WiFi ADB mode resets on phone reboot — you need to re-enable it via USB
- Run `./scripts/connect.sh usb` first, then `./scripts/connect.sh wifi <ip>`

### DroidRun agent seems confused
- Make sure DroidRun Portal is running and accessibility service is enabled
- Close unnecessary apps to reduce screen complexity
- Try a simpler task first to verify the setup works

### PIN unlock fails
- PIN pad button coordinates vary by device and screen resolution
- To find your device's coordinates: `adb shell getevent -l` and tap each digit
- Or use `adb shell input text <PIN>` as a fallback on some devices
- Set `ANDROID_PIN` environment variable (never hardcode it)

## Security

- **ADB grants full device access** — only connect devices you trust and own
- **Screenshots are sent to your LLM provider** (OpenAI by default) — be mindful of sensitive content on screen (banking apps, private messages)
- **PIN is read from environment variable only** — never stored in files or logs
- **WiFi ADB is unencrypted** — use USB or an SSH tunnel on untrusted networks
- **DroidRun Portal requires accessibility permissions** — this is powerful access; understand what it enables

## Requirements

- Python 3.10+
- ADB (Android Debug Bridge)
- Android 8.0+ phone with Developer Options and USB Debugging enabled
- [DroidRun Portal](https://github.com/droidrun/droidrun) APK installed on phone
- OpenAI API key (GPT-4o for vision capabilities)
- USB data cable (not charge-only)

## ⚠️ Security Notes

**Use a dedicated test device, not your primary phone.**

- **Screenshots & screen text go to OpenAI.** Every screenshot the agent takes is sent to GPT-4o for vision processing. Don't run this on devices with sensitive data visible — banking apps, 2FA tokens, private messages, medical info. If it's on screen, it's sent to the cloud.
- **ANDROID_PIN is stored as an environment variable.** While it's never written to files or logs, anyone with access to the host's environment can read it. Use a disposable device PIN you don't use elsewhere, or accept the risk.
- **Only install DroidRun Portal from official sources.** Download the APK exclusively from [DroidRun GitHub releases](https://github.com/droidrun/droidrun/releases). Never sideload APKs from third-party sites.
- **ADB grants full device access.** Combined with accessibility permissions, this is effectively root-level control. Only connect devices you own and are comfortable exposing.
- **WiFi ADB is unencrypted.** If using TCP/WiFi mode on an untrusted network, wrap it in an SSH tunnel.

**Bottom line:** Treat the connected phone as a "work device for AI." Don't leave personal accounts logged in. Don't store secrets on it. If you wouldn't hand your unlocked phone to a stranger, don't point this skill at it.

## License

MIT — see [LICENSE](LICENSE)
