---
name: lulu-monitor
description: AI-powered LuLu Firewall companion for macOS. Monitors firewall alerts, analyzes connections with AI, sends Telegram notifications with Allow/Block buttons. Use when setting up LuLu integration, handling firewall callbacks, or troubleshooting LuLu Monitor issues.
---

# LuLu Monitor

AI-powered companion for [LuLu Firewall](https://objective-see.org/products/lulu.html) on macOS.

![LuLu Monitor Screenshot](screenshot.png)

## What It Does

1. Monitors LuLu firewall alert popups
2. Extracts connection info (process, IP, port, DNS)
3. Spawns a fast AI (haiku) to analyze the connection
4. Sends Telegram notification with risk assessment
5. Provides 4 action buttons: Always Allow, Allow Once, Always Block, Block Once
6. Executes the action on LuLu when user taps a button

## Auto-Execute Mode (Optional)

For reduced interruptions, enable auto-execute mode. When the AI has high confidence (known safe programs like curl, brew, node, git connecting to normal destinations), it will:
1. Automatically execute the Allow action
2. Still send a Telegram notification explaining what was auto-allowed

**To enable:**
```bash
# Create config.json in install directory
cat > ~/.openclaw/lulu-monitor/config.json << 'EOF'
{
  "telegramId": "YOUR_TELEGRAM_ID",
  "autoExecute": true,
  "autoExecuteAction": "allow-once"
}
EOF
```

**Options:**
- `autoExecute`: `false` (default) - all alerts require manual button press
- `autoExecuteAction`: `"allow-once"` (default, conservative) or `"allow"` (permanent rule)

## Installation

### Prerequisites

Run the check script first:
```bash
bash scripts/check-prerequisites.sh
```

Required:
- **LuLu Firewall**: `brew install --cask lulu`
- **Node.js**: `brew install node`
- **OpenClaw Gateway**: Running with Telegram channel configured
- **Accessibility Permission**: System Settings > Privacy > Accessibility > Enable Terminal/osascript

### Gateway Configuration (Required)

The monitor calls `sessions_spawn` via OpenClaw's `/tools/invoke` HTTP API. This tool is blocked by default. Add it to the allowlist in `~/.openclaw/openclaw.json`:

```json5
{
  "gateway": {
    "tools": {
      "allow": ["sessions_spawn"]
    }
  }
}
```

Without this, alerts will be detected but fail to forward (404 in logs).

### Install

```bash
bash scripts/install.sh
```

This will:
1. Clone the repo to `~/.openclaw/lulu-monitor/`
2. Install npm dependencies
3. Set up launchd for auto-start
4. Start the service

### Verify

```bash
curl http://127.0.0.1:4441/status
```

Should return `{"running":true,...}`

## Sending Alerts with Inline Buttons

⚠️ **The `message` tool's `buttons`/`components` parameter does NOT work for Telegram inline buttons.** You must use the CLI via `exec`:

```bash
openclaw message send --channel telegram --target <chat_id> \
  --message "🔔 LuLu Alert: <summary>" \
  --buttons '[[{"text":"✅ Always Allow","callback_data":"lulu:allow"},{"text":"✅ Allow Once","callback_data":"lulu:allow-once"}],[{"text":"❌ Always Block","callback_data":"lulu:block"},{"text":"❌ Block Once","callback_data":"lulu:block-once"}]]'
```

After sending via CLI, reply with `NO_REPLY` to avoid duplicate messages.

## Handling Callbacks

When user clicks a Telegram button, OpenClaw receives a callback like:
```
callback_data: lulu:allow
callback_data: lulu:allow-once
callback_data: lulu:block
callback_data: lulu:block-once
```

To handle it, call the local endpoint:
```bash
curl -X POST http://127.0.0.1:4441/callback \
  -H "Content-Type: application/json" \
  -d '{"action":"allow"}'  # or "block", "allow-once", "block-once"
```

This will:
1. Click the appropriate button on LuLu alert
2. Set Rule Scope to "endpoint"
3. Set Rule Duration to "Always" or "Process lifetime"
4. Edit the Telegram message to show result

## Troubleshooting

### Service not running
```bash
# Check status
launchctl list | grep lulu-monitor

# View logs
tail -f ~/.openclaw/lulu-monitor/logs/stdout.log

# Restart
launchctl unload ~/Library/LaunchAgents/com.openclaw.lulu-monitor.plist
launchctl load ~/Library/LaunchAgents/com.openclaw.lulu-monitor.plist
```

### Accessibility permission issues
AppleScript needs permission to control LuLu. Go to:
System Settings > Privacy & Security > Accessibility
Enable: Terminal, iTerm, or whatever terminal you use

### Alert not detected
- Ensure LuLu is running: `pgrep -x LuLu`
- Check if alert window exists: `osascript -e 'tell application "System Events" to tell process "LuLu" to get every window'`

## Uninstall

```bash
bash ~/.openclaw/lulu-monitor/skill/scripts/uninstall.sh
```
