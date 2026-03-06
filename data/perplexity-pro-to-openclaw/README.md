# Perplexity PRO for OpenClaw

🔍 **Undetectable Perplexity PRO integration for OpenClaw with persistent sessions**

This skill enables OpenClaw agents to search Perplexity PRO while bypassing Cloudflare protection through stealth browser automation.

## ⚠️ What the Agent Will Ask You To Do

**Before installing, understand that this skill requires:**

1. **System modifications:** Installing Google Chrome, Xvfb, x11vnc
2. **Manual OAuth authentication:** You must log into Perplexity via VNC (cannot be automated)
3. **VNC access:** Remote desktop to the server for authentication
4. **Time investment:** ~15-20 minutes for initial setup

If you're not comfortable with these steps, do not proceed with installation.

## Quick Start

```bash
# Install the skill
clawdhub install perplexity-pro-openclaw

# Or manually clone
git clone https://github.com/Hantok/Perplexity-PRO-to-OpenClaw.git
```

## Detailed Installation

### Step 1: Install Google Chrome

**⚠️ Remove Snap Chromium first (it doesn't work with this setup):**

```bash
sudo snap remove chromium

# Download and install proper Chrome
cd /tmp
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f -y

# Verify
google-chrome --version
```

### Step 2: Install Dependencies

```bash
sudo apt-get update
sudo apt-get install -y Xvfb x11vnc
```

### Step 3: Configure Browser Launcher

The skill creates `~/.openclaw/workspace/start-stealth-browser.sh`:

```bash
#!/bin/bash
# Kill existing instances
pkill -f "Xvfb :99" 2>/dev/null
pkill -f "google-chrome.*remote-debugging-port=18800" 2>/dev/null
sleep 1

# Create persistent profile (NOT in /tmp!)
mkdir -p ~/.openclaw/browser-profile

# Start Xvfb virtual display
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
sleep 2

# Start Chrome with anti-bot flags
google-chrome \
    --no-sandbox \
    --disable-setuid-sandbox \
    --disable-dev-shm-usage \
    --disable-gpu \
    --remote-debugging-port=18800 \
    --user-data-dir=~/.openclaw/browser-profile \
    --window-size=1920,1080 \
    --disable-blink-features=AutomationControlled \
    --no-first-run \
    --password-store=basic \
    > /tmp/chrome.log 2>&1 &

echo "Chrome started on http://127.0.0.1:18800"
```

### Step 4: Start VNC Server

```bash
# Set VNC password (default: openclaw - CHANGE THIS!)
x11vnc -storepasswd openclaw /tmp/vncpass

# Start VNC
x11vnc -display :99 -rfbauth /tmp/vncpass -listen 0.0.0.0 -xkb -forever -shared
```

**VNC Details:**
- **Address:** `your-server-ip:5900`
- **Password:** `openclaw` (default - change recommended)

### Step 5: CRITICAL - Manual Authentication

**You MUST authenticate through VNC:**

#### macOS Users:
```bash
open vnc://your-server-ip:5900
```
Or use Finder → Cmd+K → `vnc://your-server-ip:5900`

#### Windows Users:
1. Download [RealVNC Viewer](https://www.realvnc.com/en/connect/download/viewer/)
2. Enter: `your-server-ip:5900`
3. Password: `openclaw`

#### Authentication Steps:
1. Connect to VNC
2. See Chrome with Perplexity
3. Click "Sign in with Google"
4. **Use your actual Google password** (not App Password)
5. Complete 2FA if enabled
6. ✅ Session persists permanently!

## Usage

After setup, your OpenClaw agent can search:

```bash
# Start browser
~/.openclaw/workspace/start-stealth-browser.sh

# Search Perplexity
openclaw browser open "https://www.perplexity.ai/search?q=latest+AI+news"
```

## How It Works

### Anti-Bot Strategy

| Level | Technique | Purpose |
|-------|-----------|---------|
| 1 | `--disable-blink-features=AutomationControlled` | Remove webdriver flag |
| 2 | `~/.openclaw/browser-profile` | Persistent cookies (survives reboot) |
| 3 | Xvfb virtual display | Real window, not headless |
| 4 | 1920x1080 viewport | Realistic resolution |
| 5 | Multiple stealth flags | Disable automation signals |
| 6 | Cookie persistence | Auth survives browser restarts |
| 7 | FlareSolverr (optional) | Extreme bypass |

### Why Xvfb + VNC?

- `--headless` flag is easily detected by Cloudflare
- Xvfb creates real X11 display
- Chrome thinks it's running normally
- VNC lets you interact for OAuth flows

## File Structure

```
.
├── SKILL.md              # Skill metadata (ClawHub)
├── README.md             # This file
├── scripts/
│   └── start-stealth-browser.sh
└── CHANGELOG.md
```

## Security Notes

⚠️ **Important:**
- Default VNC password is "openclaw" - change in production
- Profile stored in `~/.openclaw/browser-profile/` (persistent)
- OAuth tokens survive reboots - secure your server
- VNC is unencrypted - use SSH tunnel for remote access

## Troubleshooting

### Chrome shows "HeadlessChrome"
**Fix:** Ensure Xvfb is running before Chrome, not `--headless` flag

### Cloudflare still blocking
**Fix:** Update Chrome, verify all anti-bot flags present

### VNC won't connect
**Fix:** Check `ss -tlnp | grep 5900`, verify firewall rules

### Perplexity asks to log in again
**Fix:** Re-authenticate via VNC once. Profile persists after that.

## Requirements

- Ubuntu 20.04+ (headless OK)
- 2GB+ RAM (Chrome + Xvfb)
- OpenClaw 2026.2.17+
- Google Chrome (not Chromium Snap)

## Author

Created by [rundax.com](https://rundax.com) for the OpenClaw community.

Part of [ClawHub](https://clawhub.com) - the OpenClaw skill registry.

## License

MIT License - See LICENSE file for details.
