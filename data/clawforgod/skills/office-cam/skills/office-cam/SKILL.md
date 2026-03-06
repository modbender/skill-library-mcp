---
name: office-cam
description: Multi-camera system for office/home monitoring. Supports USB webcams (Logitech), WiFi Wyze cameras (RTSP), and ESP32 cameras. Use to check rooms, capture photos on demand, or monitor multiple spaces.
metadata:
  clawdbot:
    emoji: 🎥
---

# Office Cam - Multi-Camera System

Whole-house camera network supporting multiple camera types.

## Supported Cameras

| Type | Reliability | Setup | Best For |
|------|-------------|-------|----------|
| 🖥️ **USB Webcam** | ⭐⭐⭐⭐⭐ Instant | Plug & play | Desk, office |
| 📹 **Wyze PTZ/v3** | ⭐⭐⭐⭐⭐ Reliable | RTSP stream | Rooms, garage, shed |
| 📡 **ESP32-CAM** | ⭐⭐⭐ Experimental | ESP-NOW wireless | DIY, battery-powered |

## Quick Start

```bash
# USB Webcam (instant)
~/clawd/skills/office-cam/scripts/capture.sh

# Wyze PTZ (one-time setup required)
~/clawd/skills/office-cam/scripts/wyze-dashboard add
~/clawd/skills/office-cam/scripts/wyze-dashboard capture shed

# ESP32-CAM (ESP-NOW wireless)
# Flash firmware, auto-discovers base station, sends photos wirelessly
```

---

## 🖥️ USB Webcam (Logitech)

**Most reliable - works instantly.**

### Basic Capture
```bash
cd ~/clawd/skills/office-cam
./scripts/capture.sh /tmp/office.jpg
```

### Motion Detection ⭐ NEW
```bash
# Start motion detection (runs continuously)
./scripts/motion-detect.sh

# Captures saved to ~/.clawdbot/motion-captures/
# Automatically triggers when motion detected
# 5-second cooldown between captures
```

### 🔥 OVERWATCH Mode (AI Monitoring) ⭐⭐⭐
```bash
# Start AI-powered continuous monitoring
./scripts/overwatch start

# Check status
./scripts/overwatch status

# Stop monitoring
./scripts/overwatch stop
```

**What Overwatch does:**
- 👀 Monitors webcam 24/7 in background
- 🚨 Detects motion and saves alert
- 🔔 Can trigger notifications (integrate with OpenClaw)
- 💾 Saves motion captures to `~/.clawdbot/overwatch/`

**Or say:** *"Start overwatch"* or *"Keep overwatch"*

### 🤖 SMART OVERWATCH (AI-Escalated) ⭐⭐⭐⭐⭐
```bash
# Start smart monitoring (zero cost until trigger)
./scripts/smart-overwatch start

# I will check for triggers and analyze when found
```

**How it works:**
1. **👀 Local motion detection** (file size comparison, zero API cost, runs always)
2. **🚨 Motion detected** → creates trigger file in `~/.clawdbot/overwatch/triggers/`
3. **🤖 I detect the trigger** → analyze image with vision model (only when motion happens)
4. **👤 Person found?** → Send alert & optionally continue watching
5. **📊 No person?** → Delete trigger, back to local monitoring

**What you can say:**
- *"Start smart overwatch"*
- *"Keep watch and tell me if you see anyone"*
- *"Monitor for people only"*
- *"Check overwatch triggers"* (to manually check for pending analysis)

**Cost:** Zero until motion detected, then only when I analyze the image

### 📸 Instant Telegram Photo ⭐⭐⭐⭐⭐
**Quick capture and send - the simplest way to check your camera**

**Just say:**
- *"Show me the office"*
- *"What's on camera?"*
- *"Send me a photo"*

**What happens:**
1. I instantly capture from your webcam
2. Analyze for clear faces/activity
3. Send best image directly to your Telegram

**No stream needed - just instant photos when you want them.**

### 🔥 OVERWATCH PRO (Full Control System) ⭐⭐⭐⭐⭐⭐
**The complete solution - Telegram alerts, live stream, remote control**

```bash
# Start the full system
./scripts/overwatch-pro start

# Setup Telegram (one-time)
./scripts/overwatch-pro setup

# Get live stream URLs
./scripts/overwatch-pro stream

# Take manual photo
./scripts/overwatch-pro capture

# Check status
./scripts/overwatch-pro status

# View live log
./scripts/overwatch-pro log

# Stop
./scripts/overwatch-pro stop
```

**Features:**
- 🚨 **Instant Telegram alerts** when motion detected
- 🌐 **Live MJPEG stream** at http://localhost:8080
- 📱 **Auto-refreshes** every 2 seconds
- 📸 **Saves all captures** to ~/.clawdbot/overwatch/
- 🤖 **Telegram bot replies** - respond to alerts with commands
- 🌅 **Morning report** (8 AM daily via cron)

**Telegram Commands (reply to motion alert):**
- `analyze` - I'll check the image and tell you what I see
- `stream` - I'll send you the live stream link
- `capture` - I'll take a fresh photo right now

**Network Access:**
```bash
# Local
http://localhost:8080

# From another device on same network
http://$(hostname -I | awk '{print $1}'):8080
```

**Morning Report (with Photo):**
- Auto-generated at 8 AM (America/Denver timezone)
- **Sends a fresh morning photo of your office**
- Summarizes overnight motion events
- Offers to analyze captures
- Provides quick command reference

**Requirements for motion detection:**
```bash
brew install imagemagick  # For image comparison
```

---

## 📹 Wyze Cameras

### One-Time Setup:

1. **Enable RTSP in Wyze App:**
   - Open Wyze app → Camera Settings → Advanced Settings
   - Enable RTSP, set password
   - Copy the RTSP URL

2. **Add to system:**
   ```bash
   ~/clawd/skills/office-cam/scripts/wyze-dashboard add
   # Enter camera name (e.g., "shed")
   # Enter RTSP URL
   ```

3. **Capture:**
   ```bash
   # Single camera
   ~/clawd/skills/office-cam/scripts/wyze-dashboard capture shed
   
   # All cameras
   ~/clawd/skills/office-cam/scripts/wyze-dashboard capture-all
   
   # Quick one-liner (after setup)
   ~/clawd/skills/office-cam/scripts/wyze-capture shed
   ```

---

## 📡 ESP32-CAM (ESP-NOW Wireless)

**No WiFi router needed!** Direct wireless between ESP32s.

### Architecture:
```
┌─────────────────┐      ESP-NOW      ┌─────────────────┐
│  ESP32-CAM      │  ═══════════════► │  ESP32 Base     │◄── USB ──► Mac
│  (Camera Node)  │   (100m range)    │  (Receiver)     │
└─────────────────┘                   └─────────────────┘
        Battery powered                  Plugged into computer
```

### Flashing:

**Base Station** (plain ESP32, plugged into Mac):
```bash
cd ~/clawd/skills/office-cam/firmware/espnow-base
pio run --target upload
```

**Camera Node** (ESP32-CAM with camera):
```bash
cd ~/clawd/skills/office-cam/firmware/espnow-cam-auto
pio run --target upload
```

### How it works:
1. Base station broadcasts "beacon" every 2 seconds
2. Camera auto-discovers base station
3. Camera captures and sends photo wirelessly
4. Base receives and saves to SD/outputs to serial

**Range:** 100+ meters (no WiFi needed!)

---

## Files

| Script | Purpose |
|--------|---------|
| `capture.sh` | USB webcam |
| `wyze-capture` | Quick Wyze capture |
| `wyze-dashboard` | Multi-cam management |
| `firmware/espnow-base/` | ESP32 receiver |
| `firmware/espnow-cam-auto/` | ESP32-CAM transmitter |

---

## Troubleshooting

**Wyze "Connection refused":**
- Verify RTSP enabled in Wyze app
- Check username/password
- Ensure same WiFi network

**ESP32-CAM not connecting:**
- Keep within 10 feet for testing
- Check LED: blinking = searching, solid = capturing
- Try resetting both boards

**USB webcam not working:**
- `brew install imagesnap`
- System Settings → Privacy → Camera
