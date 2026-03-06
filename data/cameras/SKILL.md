---
name: Cameras
slug: cameras
version: 1.0.1
description: Connect to security cameras, capture snapshots, and process video feeds with protocol support.
changelog: User-driven credential model, declared tool requirements
metadata: {"clawdbot":{"emoji":"📷","requires":{"bins":["ffmpeg"]},"os":["linux","darwin"]}}
---

## Scope

This skill:
- ✅ Generates camera capture commands
- ✅ Guides integration with security systems
- ✅ Provides troubleshooting for camera issues

**User-driven model:**
- User provides camera credentials (RTSP URLs, passwords)
- User runs capture commands
- User installs required tools

This skill does NOT:
- ❌ Store camera credentials
- ❌ Run captures automatically without user request
- ❌ Access cameras without user-provided access info

## Requirements

**Required:**
- `ffmpeg` — for capture and recording

**Optional (user installs if needed):**
- `gphoto2` — for DSLR/mirrorless control
- `v4l2-ctl` — for USB cameras on Linux

## Quick Reference

| Topic | File |
|-------|------|
| Security camera integration | `security-integration.md` |
| USB/webcam capture | `capture.md` |
| DSLR control | `photography-control.md` |
| Video processing | `processing.md` |

## Core Rules

### 1. User Provides Camera Access
When user requests capture:
```
User: "Snapshot from my front door camera"
Agent: "I need the RTSP URL. Format: rtsp://user:pass@ip/stream
        Provide it or set CAMERA_FRONT_URL in env."
User: "rtsp://admin:pass@192.168.1.50/stream1"
→ Agent generates: ffmpeg -i "URL" -frames:v 1 snapshot.jpg
```

### 2. Common Commands
```bash
# Snapshot from RTSP (user provides URL)
ffmpeg -i "$RTSP_URL" -frames:v 1 snapshot.jpg

# Record 10s clip
ffmpeg -i "$RTSP_URL" -t 10 -c copy clip.mp4

# Webcam snapshot (macOS)
ffmpeg -f avfoundation -i "0" -frames:v 1 webcam.jpg

# Webcam snapshot (Linux)
ffmpeg -f v4l2 -i /dev/video0 -frames:v 1 webcam.jpg
```

### 3. Protocol Reference
| Protocol | Use Case | URL Format |
|----------|----------|------------|
| RTSP | IP cameras | `rtsp://user:pass@ip:554/stream` |
| HTTP | Simple cams | `http://ip/snapshot.jpg` |
| V4L2 | USB cameras | `/dev/video0` |

### 4. Integration Patterns
**With Home Assistant:**
```
GET /api/camera_proxy/camera.front_door
```
User provides HA URL and token.

**With Frigate:**
- MQTT: `frigate/events` for alerts
- HTTP: `/api/events/{id}/snapshot.jpg`

### 5. Security
- Never log camera URLs with credentials
- Recommend user stores URLs in env vars
- RTSP streams may be unencrypted — warn about LAN security
