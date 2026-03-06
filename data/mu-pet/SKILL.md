---
name: desktop-pet
description: Animated pixel art desktop pet that roams the screen as an always-on-top Electron overlay. The pet avoids the cursor and active windows, walks along screen edges, climbs walls and ceilings, and responds to agent state changes via a local HTTP API. Use when a user wants a desktop companion, screen buddy, desktop mascot, virtual pet, or visual indicator of agent activity. Supports states like idle, walking, working, thinking, sleeping, and talking (faces user with speech bubble). macOS only.
---

# Desktop Pet

A pixel art desktop pet (default: lobster 🦞) that roams the screen as a transparent Electron overlay.

## Quick Start

```bash
cd <skill-dir>/assets/app
npm install
npx electron .
```

The pet starts at the bottom center of the screen and begins roaming.

## HTTP API

Local API on **port 18891** (127.0.0.1 only):

- `GET /state` - returns `{"state":"idle","statusText":""}`
- `POST /state` - set state: `{"state":"talking","bubble":"hello!"}`

### States

| State | Behavior |
|-------|----------|
| `idle` | Gentle bob, occasional claw snap |
| `walking` | Moves along current surface |
| `climbing` | Transitions between floor/walls/ceiling |
| `fleeing` | Running from cursor or active window |
| `working` | Sits at tiny laptop with sparkle particles |
| `thinking` | Slow sway, thought dots appear |
| `sleeping` | Eyes closed, zzz bubbles float up |
| `talking` | Faces user, shows speech bubble, auto-returns to idle |
| `snapping` | Claw snap animation |

### Agent Integration

Hit the API at the start of responses to make the pet face the user:

```bash
curl -s -X POST http://127.0.0.1:18891/state \
  -H 'Content-Type: application/json' \
  -d '{"state":"talking","bubble":"working on it..."}'
```

Set to `working` during long operations, `thinking` while reasoning.

The `talking` state auto-returns to `idle` after the bubble duration expires.

## Auto-Launch (macOS)

Create a LaunchAgent for auto-start on login. Use label `ai.openclaw.desktop-pet`.

```bash
# Install as LaunchAgent
cat > ~/Library/LaunchAgents/ai.openclaw.desktop-pet.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>ai.openclaw.desktop-pet</string>
  <key>ProgramArguments</key><array>
    <string>APP_PATH/node_modules/.bin/electron</string>
    <string>APP_PATH</string>
  </array>
  <key>WorkingDirectory</key><string>APP_PATH</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>/tmp/desktop-pet.log</string>
  <key>StandardErrorPath</key><string>/tmp/desktop-pet.log</string>
  <key>EnvironmentVariables</key><dict>
    <key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
  </dict>
</dict></plist>
EOF
```

Replace `APP_PATH` with the absolute path to the app directory.

## Customization

The pet is drawn programmatically via Canvas pixel art in `index.html`. To change the creature:

- Edit `lobsterBase()` and `lobsterFront()` functions with new pixel layouts
- Colors are defined as constants at the top of the script block
- Each pixel is `{x, y, w, h, color}` at 3x scale

## Features

- Transparent overlay, always-on-top, click-through (except on the pet itself)
- Roams full desktop: floor, walls, ceiling
- Avoids cursor (250px radius) and frontmost window
- Right-click context menu for manual state control
- Speech bubbles with auto-sizing duration
- Pixel art drawn via Canvas (no external images needed)
