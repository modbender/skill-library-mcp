# 📹 ClawCamera — Multi-Camera Surveillance with AI

Professional-grade office/home monitoring system with motion detection, continuous monitoring (Overwatch), and AI-powered analysis. Built for OpenClaw.

## 🎯 What It Does

✅ **Instant snapshots** — Ask "Is anyone here?" and get AI-powered visual answers

✅ **Motion detection** — Alerts when movement is detected (configurable modes)

✅ **Overwatch mode** — 24/7 background monitoring with periodic check-ins

✅ **Smart Overwatch** — Local motion detection (zero cost) → AI escalation only when needed

✅ **Multi-camera** — USB webcams, Wyze RTSP, ESP32-CAM all supported

✅ **Telegram integration** — Instant notifications with images

✅ **No secrets in git** — Comprehensive .gitignore + env-based config

## 🚀 Quick Start

### 1. Install

```bash
git clone https://github.com/Snail3D/ClawCamera.git
cd ClawCamera
npm install
```

### 2. Configure

```bash
# Copy example config
cp .env.example .env

# Add your Telegram credentials for notifications
export TELEGRAM_TOKEN=your_bot_token
export TELEGRAM_CHAT_ID=your_chat_id
```

### 3. Use

**One-shot capture:**
```bash
./scripts/capture.sh
# → Captures photo
# → Output: Saved to /tmp/capture.jpg
```

**Start Overwatch:**
```bash
./scripts/overwatch-pro start
# → Continuous background monitoring
# → Motion alerts sent to Telegram
# → Live stream at http://localhost:8080
```

**Smart Overwatch (AI-escalated):**
```bash
./scripts/smart-overwatch start
# → Local motion detection (zero API cost)
# → Creates triggers for AI analysis
# → AI only runs when motion detected
```

## 📚 Documentation

- [SKILL.md](/Snail3D/ClawCamera/blob/main/SKILL.md) — Full feature list, configuration, and integration guide (for OpenClaw Hub)
- [guides/esp32-setup.md](/Snail3D/ClawCamera/blob/main/guides/esp32-setup.md) — ESP32-CAM firmware & deployment
- [guides/wyze-setup.md](/Snail3D/ClawCamera/blob/main/guides/wyze-setup.md) — Wyze camera RTSP configuration
- [guides/troubleshooting.md](/Snail3D/ClawCamera/blob/main/guides/troubleshooting.md) — Common issues & solutions

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│  User Request (Chat / Voice Command)    │
└────────────────┬────────────────────────┘
                 │
        ┌────────▼────────┐
        │    Capture      │
        │       OR        │
        │  Motion Check   │
        │       OR        │
        │    Overwatch    │
        └────────┬────────┘
                 │
        ┌────────▼────────────────────┐
        │      Image Storage          │
        │   ~/.clawdbot/overwatch/    │
        └────────┬────────────────────┘
                 │
        ┌────────▼──────────────────┐
        │   OpenClaw AI Analysis    │
        │   (On-demand via triggers)│
        └────────┬──────────────────┘
                 │
        ┌────────▼──────────────────┐
        │   Telegram Notification   │
        │      Image + Alert        │
        └────────────────────────────┘
```

**How AI Analysis Works:**

1. **Local motion detection** runs continuously using file size comparison (zero API cost)
2. When motion is detected, a **trigger file** is created in `~/.clawdbot/overwatch/triggers/`
3. **OpenClaw detects the trigger** and analyzes the image using its configured vision model
4. If a person is detected, notifications are sent via Telegram
5. If no person, monitoring continues silently

## 🎯 Monitoring Modes

### 🔴 Overwatch Pro (Full-Featured)
```bash
./scripts/overwatch-pro start
```
- 🚨 Instant Telegram alerts on motion
- 🌐 Live MJPEG stream at http://localhost:8080
- 📱 Remote commands via Telegram replies
- 💾 Saves all captures to `~/.clawdbot/overwatch/`

**Telegram Commands (reply to motion alert):**
- `analyze` — Request AI analysis of the image
- `stream` — Get live stream link
- `capture` — Take a fresh photo

### 🟡 Smart Overwatch (Cost-Optimized)
```bash
./scripts/smart-overwatch start
```
- 👀 Local motion detection (zero API cost, runs always)
- 🚨 Motion detected → creates trigger file
- 🤖 AI analyzes only when trigger exists
- 👤 Person found? → AI starts continuous watching
- 📊 No person? → Back to local monitoring

### 🔵 One-Shot Capture
```bash
./scripts/capture.sh
```
Instant photo capture on demand. Great for quick checks.

## 📸 Multi-Camera Support

### USB Webcam (Instant)
Plug in any USB webcam and capture immediately.

```bash
./scripts/capture.sh --device /dev/video0
```

**Requirements:**
```bash
brew install imagesnap  # macOS
```

### Wyze Camera (RTSP)
Stream from Wyze PTZ or v3 cameras over your local network.

```bash
export WYZE_IP=192.168.1.100
./scripts/capture.sh --device wyze
```

**Setup:**
1. Enable RTSP in Wyze app → Camera Settings → Advanced Settings
2. Set RTSP password
3. Use the provided RTSP URL

### ESP32-CAM (Wireless)
Deploy an ESP32-CAM to remote locations with OV2640 sensor + WiFi.

```bash
# See guides/esp32-setup.md for full firmware & config
./scripts/capture-esp32.sh --ip 192.168.1.50
```

## 🔐 Security & Privacy

### ✅ No Secrets in Git

- Comprehensive .gitignore blocks all sensitive files
- API keys stored in .env (never committed)
- Credentials in credentials.h or config.json are ignored
- auth.json, secrets/ folder all blocked

### ✅ Local-First Architecture

- Motion detection runs locally (no cloud calls)
- Images stored in `~/.clawdbot/overwatch/` (local filesystem)
- AI analysis only happens when triggers are detected
- No continuous API usage or streaming to cloud

### ✅ Configurable Data Retention

Captures are stored locally. Add a cron job for cleanup:
```bash
# Delete captures older than 7 days
find ~/.clawdbot/overwatch -name "*.jpg" -mtime +7 -delete
```

## 🛠️ Requirements

- **macOS or Linux**
- **imagesnap** (`brew install imagesnap`) for USB webcams
- **imagemagick** (`brew install imagemagick`) for motion detection
- **Python 3** for Overwatch scripts
- **Telegram Bot Token** for notifications (optional)

## 📁 File Structure

```
ClawCamera/
├── scripts/
│   ├── capture.sh           # One-shot USB webcam capture
│   ├── overwatch-pro        # Full monitoring with Telegram
│   ├── smart-overwatch      # Cost-optimized AI escalation
│   ├── motion-detect.sh     # Basic motion detection
│   ├── wyze-dashboard       # Wyze camera management
│   └── capture-esp32.sh     # ESP32-CAM capture
├── firmware/
│   ├── espnow-base/         # ESP32 receiver firmware
│   └── espnow-cam-auto/     # ESP32-CAM transmitter firmware
├── guides/
│   ├── esp32-setup.md
│   ├── wyze-setup.md
│   └── troubleshooting.md
├── .env.example             # Environment template
├── .gitignore               # Prevents secrets in git
├── SKILL.md                 # OpenClaw integration guide
└── README.md                # This file
```

## 🤝 OpenClaw Integration

This skill is designed to work with OpenClaw. When properly configured:

- **"Show me the office"** → Instant photo + analysis
- **"Start overwatch"** → Begin monitoring
- **"Is anyone there?"** → One-shot capture + AI check

See [SKILL.md](/Snail3D/ClawCamera/blob/main/SKILL.md) for full OpenClaw integration details.

## License

MIT
