---
name: sentinel
description: Transform an Android phone with IP Webcam into an intelligent Edge AI security system with OpenClaw.
metadata: {"clawdbot":{"emoji":"🛡️","requires":{"bins":["compare","curl","awk"]},"install":[{"id":"apt","kind":"apt","packages":["imagemagick"],"bins":["compare"],"label":"Install ImageMagick (apt)"}]}}
---

# Security monitoring over IP Camera Android app

Use the **Clawd Sentinel** pattern to turn any old Android smartphone into a sovereign, frugal, and intelligent motion detection system.

## Setup

1. **Android Side**: Install "IP Webcam" (by Pavel Khlebovich) and start the server.
2. **Connectivity**: Note the local IP (e.g., `192.168.1.100:8080`).
3. **OpenClaw Workspace**:
   - `bin/sentinel_ultra_frugal.sh`: The core logic for pixel comparison.
   - `bin/sentinel_runner.sh`: The background loop runner.

## Detailed API Interaction

The IP Webcam server provides a REST-like API for full remote control. Base URL: `http://<IP>:8080/`

### Visual Captures
- **Standard Snapshot**: `/shot.jpg` (Fastest, current frame)
- **Autofocus Snapshot**: `/photoaf.jpg` (Triggers autofocus before capture, highest quality)
- **Video Recording**:
  - Start: `/startvideo?name=alert_123`
  - Stop: `/stopvideo`
  - List recordings: `/list_videos` (returns JSON/HTML)
  - Download: `/v/<filename>.mp4`

### Camera Control & Settings
- **Focus Distance**: `/settings/focus_distance?set=<0.0-10.0>` (0.0 is often Infinity)
- **Torch (Flash)**: `/enabletorch` | `/disabletorch`
- **Focus Mode**: `/settings/focusmode?set=<on|off|macro|infinity|fixed>`
- **Scene Mode**: `/settings/scenemode?set=<auto|night|action|party...>`
- **White Balance**: `/settings/whitebalance?set=<auto|daylight|cloudy...>`

### Device Telemetry
- **Sensors Data**: `/sensors.json` (Battery, light level, proximity, accelerometer)
- **System Status**: `/status.json` (Camera state, recording status, uptime)

### Audio
- **Audio Feed**: `/audio.wav` or `/audio.opus` (Live audio stream)

### Integration Examples (curl)
```bash
# Get battery level via jq
curl -s http://<IP>:8080/sensors.json | jq '.battery_level[0][1][0]'

# Toggle flash remotely
curl http://<IP>:8080/enabletorch
```

## Recommended Thresholds

- **Daytime (Haze/Clouds)**: 2500
- **Nighttime (ISO noise)**: 1500

## Notes
- **Frugality**: No tokens are consumed unless the pixel differential exceeds the threshold.
- **Privacy**: Raw frames remain local. Only alert-triggered frames are sent to the AI.
- **Maintenance**: Periodically check phone battery and Wi-Fi stability.
- **Lens flare**: Long rainbow flares in night mode usually indicate static lights, not vehicles.
