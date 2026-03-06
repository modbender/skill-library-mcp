---
name: oref-native
description: >
  Israeli Home Front Command alerts - fully OpenClaw native.
  No Home Assistant. No wacli. No Docker monitor.
  OpenClaw handles everything: WhatsApp + TTS.
---

# ORef Native - OpenClaw Only 🚨

## Architecture

```
Pikud Ha-Oref API
       ↓
oref_native.py (cron every 5s)
       ↓
openclaw message → 📱 WhatsApp group
openclaw tts     → 🔊 Voice announcement
```

## vs. Old System

| | Old | Native |
|--|-----|--------|
| WhatsApp | wacli binary | openclaw message |
| TTS | Home Assistant | openclaw tts |
| Lights | Home Assistant | ❌ (not needed) |
| Dependencies | Docker + HA + wacli | **OpenClaw only** |

## Setup

```bash
# Install cron (every 5 seconds via loop)
nohup python3 /root/.openclaw/workspace/skills/oref-native/oref_native.py \
  >> /var/log/oref_native.log 2>&1 &

# Or add to crontab (restart on boot)
@reboot python3 /root/.openclaw/workspace/skills/oref-native/oref_native.py >> /var/log/oref_native.log 2>&1
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| OREF_API_URL | http://localhost:49000/current | oref-alerts proxy |
| MONITORED_AREAS | הרצליה,הרצליה - גליל ים ומרכז | Comma-separated areas |
| WHATSAPP_GROUP_JID | - | WhatsApp group JID |
| WHATSAPP_OWNER | - | Personal WhatsApp number |
| OPENCLAW_BIN | openclaw | Path to openclaw binary |

## Alert Routing

| Type | WhatsApp | TTS |
|------|----------|-----|
| 🚀 Rockets (cat=1) | ✅ | ✅ |
| ✈️ Aircraft (cat=2) | ✅ | ✅ |
| 🔴 Infiltration (cat=10) | ✅ | ✅ |
| ✅ All clear (cat=13) | ✅ | ✅ |
| ⚠️ Pre-alert (cat=14) | ❌ | ✅ |
