---
name: tidbyt-status
description: HTTP API server that exposes OpenClaw agent status for Tidbyt LED displays. Use when creating integrations with Tidbyt devices, building status dashboards, or displaying agent activity on 64x32 pixel displays. Returns JSON with agent status, emoji, activity level, and task counts.
---

# Tidbyt Status - Scout Display

Complete integration for displaying Scout's status on Tidbyt 64x32 LED displays.

## Components

1. **Status API Server** (`scripts/status_server.py`) - Exposes Scout's status as JSON
2. **Tidbyt App** (`scout_status.star`) - Starlark app for rendering on Tidbyt

## Quick Start

### 1. Start the Status API Server

```bash
cd ~/.openclaw/workspace/skills/tidbyt-status
python3 scripts/status_server.py
```

API available at `http://localhost:8765/status`

### 2. Install Pixlet (Tidbyt Development Tool)

**macOS:**
```bash
brew install tidbyt/tidbyt/pixlet
```

**Linux:**
Download from [GitHub releases](https://github.com/tidbyt/pixlet/releases/latest)

### 3. Test Locally

Update the IP address in `scout_status.star` (line 10):
```python
DEFAULT_API_URL = "http://YOUR-LOCAL-IP:8765/status"
```

Render and serve:
```bash
pixlet serve scout_status.star
```

Visit http://localhost:8080 to preview.

### 4. Push to Your Tidbyt

First, login and get your device ID:
```bash
pixlet login
pixlet devices
```

Render the app:
```bash
pixlet render scout_status.star
```

Push to your Tidbyt:
```bash
pixlet push --installation-id Scout <YOUR-DEVICE-ID> scout_status.webp
```

## Display Features

- **Agent name + emoji** (🦅) at top with animated face
- **Status-specific faces:**
  - **CHAT** (green) - Casual chatting, eyes moving
  - **WORK** (yellow) - Working hard, yellow face with purple focused eyes
  - **THINK** (blue) - Thinking/processing, eyes blinking
  - **SLEEP** (gray) - Idle/sleeping, closed eyes
- **Task count** - Number of concurrent sub-agent tasks
- **Recent activity** - Scrolling text showing current activity

## API Response Format

The status server returns JSON:

```json
{
  "agent": "Scout",
  "emoji": "🦅",
  "status": "chatting|working|thinking|sleeping",
  "timestamp": "2026-02-06T14:30:00",
  "active_tasks": 0,
  "last_activity": "2026-02-06T14:25:00",
  "recent_activity": "Chatting with user..."
}
```

**Status Types:**
- `chatting` - Main session active, no background tasks
- `working` - Sub-agent sessions running (processing tasks)
- `thinking` - Some activity but unclear
- `sleeping` - No activity for >1 hour

## Configuration

### Custom API Port

```bash
PORT=9000 python3 scripts/status_server.py
```

### Custom API URL in Tidbyt App

When pushing to Tidbyt, configure via the mobile app:
1. Tap the Scout installation
2. Settings → API URL
3. Enter your full URL

## Running the API Server as a Service

### systemd (Linux)

Create `/etc/systemd/system/scout-status.service`:

```ini
[Unit]
Description=Scout Status API for Tidbyt
After=network.target

[Service]
Type=simple
User=<username>
WorkingDirectory=/home/<username>/.openclaw/workspace/skills/tidbyt-status
ExecStart=/usr/bin/python3 scripts/status_server.py
Restart=always
Environment="PORT=8765"

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable scout-status
sudo systemctl start scout-status
```

### Manual Background

```bash
nohup python3 scripts/status_server.py > /tmp/scout-status.log 2>&1 &
```

## Network Configuration

For Tidbyt to access the API:

1. **Find your local IP:**
   ```bash
   hostname -I | awk '{print $1}'
   ```

2. **Update firewall** (if needed):
   ```bash
   sudo ufw allow 8765/tcp
   ```

3. **Test from another machine:**
   ```bash
   curl http://YOUR-IP:8765/status
   ```

## Status Detection Logic

The server monitors `~/.openclaw/agents/main/sessions/*.jsonl`:

- **Active**: Any session modified within last 5 minutes
- **Idle**: No recent activity
- **Active tasks**: Count of sub-agent sessions (excludes main session)
- **Recent activity**: Shows time since last activity when idle

## Customization

### Change the Emoji

Edit `scripts/status_server.py` line 16:
```python
"emoji": "🦅",  # Change to any emoji
```

### Adjust Activity Threshold

Edit `scripts/status_server.py` line 34 (default 300 seconds):
```python
if age_seconds < 300:  # Change threshold here
```

### Modify Display Colors

Edit `scout_status.star` lines 39-40:
```python
status_color = "#00FF00" if status == "active" else "#888888"
```

## Troubleshooting

**API returns error:**
- Check if OpenClaw is running
- Verify `~/.openclaw/agents/main/sessions/` exists

**Tidbyt shows "API Error":**
- Verify API URL is accessible from Tidbyt's network
- Check firewall settings
- Test with: `curl http://YOUR-IP:8765/status`

**Display doesn't update:**
- Tidbyt apps refresh every ~30 seconds (see `ttl_seconds` in code)
- Check if the status API server is still running

## Files

- `SKILL.md` - This documentation
- `scripts/status_server.py` - HTTP API server
- `scout_status.star` - Tidbyt Starlark app
- `tidbyt-status.skill` - Packaged skill file
