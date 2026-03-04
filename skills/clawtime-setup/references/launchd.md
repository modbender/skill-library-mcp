# ClawTime — Auto-Start with macOS launchd

Set up both ClawTime and the Cloudflare tunnel as launchd user agents.
They auto-start on login and restart automatically if they crash.

## Important: Token Security

**Do NOT put tokens directly in plist files** — plists are plaintext XML on disk.
Instead, store tokens in macOS Keychain and use a wrapper script to load them at launch.

### Store tokens in Keychain (one-time setup)

```bash
security add-generic-password -U -s "clawtime-gateway-token" -a "$(whoami)" -w "YOUR_GATEWAY_TOKEN"
security add-generic-password -U -s "clawtime-setup-token" -a "$(whoami)" -w "YOUR_SETUP_TOKEN"
```

### Create wrapper script

File: `~/Projects/clawtime/launchd-start.sh`

```bash
#!/usr/bin/env bash
# Wrapper script for launchd — loads tokens from Keychain securely
export GATEWAY_TOKEN=$(security find-generic-password -s "clawtime-gateway-token" -a "$(whoami)" -w)
export SETUP_TOKEN=$(security find-generic-password -s "clawtime-setup-token" -a "$(whoami)" -w)

if [ -z "$GATEWAY_TOKEN" ]; then
  echo "ERROR: Gateway token not found in Keychain" >&2
  exit 1
fi

export PUBLIC_URL="https://portal.yourdomain.com"
export BOT_NAME="Beware"
export BOT_EMOJI="🌀"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

# Optional: uncomment and edit for TTS
# export TTS_COMMAND='python3 -m piper --data-dir /Users/YOUR_USER/Documents/resources/piper-voices -m en_US-kusal-medium -f /tmp/clawtime-tts-tmp.wav -- {{TEXT}} && ffmpeg -y -loglevel error -i /tmp/clawtime-tts-tmp.wav {{OUTPUT}}'

cd /Users/YOUR_USER/Projects/clawtime
exec /opt/homebrew/bin/node server.js
```

```bash
chmod +x ~/Projects/clawtime/launchd-start.sh
```

---

## ClawTime Server Plist

File: `~/Library/LaunchAgents/com.clawtime.server.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.clawtime.server</string>
  <key>ProgramArguments</key>
  <array>
    <string>/Users/YOUR_USER/Projects/clawtime/launchd-start.sh</string>
  </array>
  <key>WorkingDirectory</key>
  <string>/Users/YOUR_USER/Projects/clawtime</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/tmp/clawtime.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/clawtime-error.log</string>
</dict>
</plist>
```

**Note:** No tokens in the plist — they're loaded from Keychain by the wrapper script.

---

## Cloudflare Tunnel Plist

File: `~/Library/LaunchAgents/com.clawtime.tunnel.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.clawtime.tunnel</string>
  <key>ProgramArguments</key>
  <array>
    <string>/opt/homebrew/bin/cloudflared</string>
    <string>tunnel</string>
    <string>run</string>
    <string>clawtime</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/tmp/cloudflared.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/cloudflared-error.log</string>
</dict>
</plist>
```

---

## Commands

```bash
# Load (start now + persist)
launchctl load ~/Library/LaunchAgents/com.clawtime.server.plist
launchctl load ~/Library/LaunchAgents/com.clawtime.tunnel.plist

# Unload (stop + remove from startup)
launchctl unload ~/Library/LaunchAgents/com.clawtime.server.plist
launchctl unload ~/Library/LaunchAgents/com.clawtime.tunnel.plist

# Check status
launchctl list | grep clawtime

# Reload after editing plist (unload then load)
launchctl unload ~/Library/LaunchAgents/com.clawtime.server.plist
launchctl load ~/Library/LaunchAgents/com.clawtime.server.plist

# View logs
tail -f /tmp/clawtime.log
tail -f /tmp/clawtime-error.log
tail -f /tmp/cloudflared.log
```

---

## Notes

- Services run as your user (not root) — start on login, not on cold boot
- `KeepAlive: true` → launchd auto-restarts if process dies
- Find node path: `which node` (use full path in wrapper script)
- If Mac restarts and auto-login is enabled, services start automatically
- To update tokens: update in Keychain (`security add-generic-password -U ...`), then unload/load the plist
