# 🚨 ORef Alerts - OpenClaw Native

Real-time Israeli Home Front Command (פיקוד העורף) alert system.  
**No Home Assistant. No extra WhatsApp binary. OpenClaw handles everything.**

---

## Architecture

```
Pikud Ha-Oref API
       ↓
oref_native.py (polls every 5s)
       ↓
📱 openclaw message → WhatsApp group
📞 3CX outbound call → your extension
🔊 Home Assistant TTS → speaker (optional)
```

---

## Quick Install

```bash
git clone https://github.com/YOUR_USER/oref-native
cd oref-native
bash install.sh
```

The installer will:
- Pull `dmatik/oref-alerts` Docker proxy
- Install Python dependencies
- Ask for your config interactively
- Start the monitor + add to crontab

---

## Configuration (`.env`)

```env
# API
OREF_API_URL=http://localhost:49000/current
OREF_POLL_INTERVAL=5
OREF_COOLDOWN=60

# Areas to monitor (comma separated Hebrew names)
MONITORED_AREAS=הרצליה,הרצליה - גליל ים ומרכז

# WhatsApp (via OpenClaw)
WHATSAPP_GROUP_JID=120363417492964228@g.us

# 3CX Phone Call
CX3_API=http://localhost:3000/api/outbound-call
CX3_EXTENSION=12610
CX3_ENABLED=true        # false = disable calls

# Home Assistant TTS (optional)
HASS_SERVER=https://homeassistant.local
HASS_TOKEN=your_token_here
HA_TTS_SPEAKER=media_player.your_speaker
```

---

## Alert Routing

| Type | WhatsApp | 📞 3CX Call | 🔊 Speaker |
|------|----------|-------------|------------|
| 🚀 Rockets (cat=1) | ✅ | ✅ | ✅ |
| ✈️ Aircraft (cat=2) | ✅ | ✅ | ✅ |
| 🔴 Infiltration (cat=10) | ✅ | ✅ | ✅ |
| ✅ All clear (cat=13) | ✅ | ❌ | ✅ |
| ⚠️ Pre-alert (cat=14) | ❌ | ❌ | ✅ |

---

## vs. Old Stack

| | Before | Now |
|--|--------|-----|
| WhatsApp | wacli binary | openclaw message |
| Voice call | ❌ | 3CX outbound call |
| TTS | Home Assistant | HA (optional) |
| Services | 5 | 2 (proxy + monitor) |
| Dependencies | Docker + HA + wacli | **OpenClaw + Docker proxy** |

---

## Commands

```bash
# Live logs
tail -f /var/log/oref_native.log

# Stop monitor
pkill -f oref_native.py

# Restart
bash install.sh

# Test API
curl -s http://localhost:49000/current | python3 -m json.tool

# Test 3CX call manually
curl -X POST http://localhost:3000/api/outbound-call \
  -H "Content-Type: application/json" \
  -d '{"to":"12610","message":"בדיקת מערכת התרעות","language":"he"}'
```

---

## Requirements

- [OpenClaw](https://github.com/openclaw/openclaw) 
- Docker
- Python 3.8+
- `openclaw-3cx` (for phone calls, optional)
- Home Assistant (for speaker TTS, optional)

---

## ⚠️ Common Issue: Duplicate Monitor

If you get alerts from wrong areas, check for a rogue process:
```bash
ps aux | grep monitor.py | grep -v grep
# Kill any non-Docker monitor:
kill <PID>
```
Only `oref_native.py` should run. Not `monitor.py` directly.
