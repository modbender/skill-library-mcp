---
name: perplexity-pro-openclaw
description: Connect Perplexity PRO to OpenClaw with anti-bot browser automation, bypassing Cloudflare protection via Xvfb and VNC authentication
homepage: https://github.com/Hantok/Perplexity-PRO-to-OpenClaw
metadata:
  clawdbot:
    emoji: "🔍"
  requires:
    env: ["DISPLAY"]
  files: ["scripts/*"]
version: 1.0.0
---

# Perplexity PRO for OpenClaw

This skill enables OpenClaw to search Perplexity PRO with persistent authenticated sessions, bypassing Cloudflare protection through undetectable browser automation.

## What This Skill Does

- ✅ Bypasses Cloudflare bot detection (Xvfb + stealth Chrome)
- ✅ Maintains persistent Perplexity PRO sessions across reboots
- ✅ Provides VNC access for manual OAuth authentication
- ✅ Creates automated search capability for OpenClaw agents

## Prerequisites

- Ubuntu Server (headless or with display)
- OpenClaw installed and configured
- Google Chrome (NOT Snap version)
- Xvfb package
- x11vnc for remote access

## Interactive Setup Steps

During installation, the agent will guide you through:

### Step 1: Chrome Installation
The agent will help you remove Snap Chromium and install proper Google Chrome:
```bash
sudo snap remove chromium
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
```

### Step 2: Browser Launcher Setup
The agent creates `start-stealth-browser.sh` with anti-bot settings:
- Xvfb virtual display (bypasses headless detection)
- Persistent profile in `~/.openclaw/browser-profile/`
- Stealth flags to mask automation

### Step 3: VNC Configuration
The agent sets up x11vnc for remote browser access:
```bash
sudo apt-get install -y x11vnc
x11vnc -storepasswd openclaw /tmp/vncpass
```

**⚠️ Security Note:** Default VNC password is "openclaw" - change this in production!

### Step 4: Manual Authentication (Required)
**You must authenticate manually through VNC:**

1. Connect via VNC (macOS: `open vnc://your-server:5900`, Windows: RealVNC Viewer)
2. Open Perplexity.ai in the browser
3. Click "Sign in with Google"
4. Enter your email and password directly
5. Complete 2FA if enabled

**Important:** App Passwords do NOT work for web authentication. Use your actual Google password.

## How to Use

After setup, the agent can search Perplexity:

```bash
# Via skill script
./scripts/start-stealth-browser.sh

# Search Perplexity
openclaw browser open "https://www.perplexity.ai/search?q=your+query"
```

## File Structure

```
perplexity-pro-openclaw/
├── SKILL.md          # This file - skill metadata and setup
├── README.md         # Detailed installation guide
├── scripts/
│   └── start-stealth-browser.sh  # Browser launcher
└── CHANGELOG.md      # Version history
```

## Anti-Bot Techniques (7 Levels)

1. **Browser Fingerprint Masking** - `--disable-blink-features=AutomationControlled`
2. **Session Persistence** - Profile in `~/.openclaw/browser-profile/` (not /tmp)
3. **Xvfb Virtual Display** - Real Chrome window, not headless
4. **Realistic Viewport** - 1920x1080 resolution
5. **Disabled Automation Flags** - Background throttling disabled
6. **Persistent Cookies** - Survives browser restarts
7. **FlareSolverr** (optional) - For extreme cases

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Chrome shows "HeadlessChrome" | Ensure Xvfb is running, not `--headless` flag |
| Cloudflare still blocking | Update Chrome, verify all stealth flags |
| VNC connection refused | Check `ss -tlnp \| grep 5900`, verify firewall |
| Perplexity asks to login again | Profile directory issue - re-authenticate via VNC once |

## Security Considerations

- VNC password should be changed from default "openclaw"
- Profile stored in `~/.openclaw/browser-profile/` (user home, not /tmp)
- OAuth tokens persist - secure your server appropriately
- VNC traffic is unencrypted by default - use SSH tunnel for remote access

## Author

Created by [rundax.com](https://rundax.com)

Part of the OpenClaw ecosystem - [ClawHub](https://clawhub.com)
