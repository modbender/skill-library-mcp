# Scout Status - Tidbyt Display

Display your OpenClaw agent Scout's real-time status on a Tidbyt 64x32 LED matrix!

![Scout on Tidbyt](https://via.placeholder.com/128x64/000000/FFA500?text=🦅+Scout)

## What It Does

- Shows Scout's current status (ACTIVE/IDLE)
- Displays active task count
- Pulses green when working
- Shows recent activity in scrolling text
- Updates every 30 seconds

## Installation

### 1. Start the Status API

```bash
cd ~/.openclaw/workspace/skills/tidbyt-status
python3 scripts/status_server.py
```

### 2. Install Pixlet

**macOS:** `brew install tidbyt/tidbyt/pixlet`  
**Linux:** [Download](https://github.com/tidbyt/pixlet/releases)

### 3. Configure & Push

Edit `scout_status.star` with your local IP:
```python
DEFAULT_API_URL = "http://YOUR-IP:8765/status"
```

Test locally:
```bash
pixlet serve scout_status.star  # Visit http://localhost:8080
```

Push to Tidbyt:
```bash
pixlet render scout_status.star
pixlet push --installation-id Scout <DEVICE-ID> scout_status.webp
```

## Features

✅ Real-time status monitoring  
✅ Activity detection (5min window)  
✅ Task counting  
✅ Animated status bar  
✅ Customizable colors  
✅ Runs as a service  

## Requirements

- OpenClaw agent
- Python 3.7+
- Tidbyt device
- Local network access

## Documentation

See [SKILL.md](SKILL.md) for complete documentation, configuration, and troubleshooting.

## Sharing

Built for OpenClaw agents! Share on [Moltbook](https://moltbook.ai) or [ClawHub](https://clawhub.com).

## License

MIT - Built by Scout 🦅
