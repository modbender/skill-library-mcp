---
name: anemone-browser
description: >
  Managed headful Chrome browser for OpenClaw agents with anti-bot-detection,
  human-in-the-loop VNC takeover, and multi-session window isolation.
  Use when: (1) setting up browser automation on a new machine (Mac/Linux/Docker),
  (2) browser gets blocked by Google, Cloudflare, or CAPTCHAs,
  (3) need human to intervene via VNC (login, CAPTCHA solving),
  (4) multiple agent sessions need independent browser windows without conflicts,
  (5) configuring OpenClaw's browser tool for headful Chrome.
  Triggers: "set up browser", "browser blocked", "CAPTCHA", "VNC",
  "Google Scholar blocked", "headless detected", "anti-detection",
  "browser setup", "Chrome for agent".
---

# Anemone Browser — Managed Browser for OpenClaw Agents

Headful Chrome with anti-detection, VNC takeover, and multi-session isolation.
Works on Mac, Linux, Docker — anywhere OpenClaw runs.

## Setup

### macOS

```bash
bash scripts/setup-mac.sh
```

Detects Chrome, configures OpenClaw browser profile. After setup:
```bash
openclaw browser start
# Agent's browser tool works automatically
```

> **Note:** macOS setup does NOT include VNC/noVNC. The user is expected to access
> the Mac via their own remote desktop solution (e.g. macOS Screen Sharing, Tailscale,
> or physical access). VNC takeover with noVNC links is only available on Linux.

### Linux / Docker

```bash
# Install deps (once)
bash scripts/setup.sh

# Start browser + VNC environment
bash scripts/start.sh [password] [novnc_port] [cdp_port] [resolution]
```

`start.sh` outputs the noVNC URL, password, and CDP port. Safe to re-run.

## OpenClaw Config

Setup scripts configure this automatically. Manual reference:

**macOS:**
```json
{
  "browser": {
    "enabled": true,
    "defaultProfile": "openclaw",
    "headless": false,
    "executablePath": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  }
}
```

**Linux:**
```json
{
  "browser": {
    "enabled": true,
    "headless": false,
    "noSandbox": true,
    "executablePath": "/usr/bin/google-chrome-stable"
  }
}
```

## Multi-Session Window Isolation

Multiple sessions share one Chrome (same cookies/logins) but each gets its own window.

### Rules (MUST follow):

1. **On session start — open your own tab, save the targetId:**
   ```
   browser action=open targetUrl="https://example.com" profile=openclaw
   # Returns targetId — THIS IS YOURS, save it
   ```

2. **ALL subsequent calls — always include your targetId:**
   ```
   browser action=snapshot profile=openclaw targetId="<your-targetId>"
   browser action=navigate profile=openclaw targetId="<your-targetId>" targetUrl="..."
   browser action=act profile=openclaw targetId="<your-targetId>" ...
   ```

3. **On session end — close your tab:**
   ```
   browser action=close targetId="<your-targetId>"
   ```

4. **NEVER operate without targetId** — you'll land on another session's tab.

5. **NEVER pick another session's tab** from `browser action=tabs`.

### Opening a new window (not tab) via CDP:

```python
import json, asyncio, websockets, urllib.request

async def open_new_window(cdp_port, url):
    version = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json/version").read())
    async with websockets.connect(version["webSocketDebuggerUrl"]) as ws:
        await ws.send(json.dumps({
            "id": 1, "method": "Target.createTarget",
            "params": {"url": url, "newWindow": True}
        }))
        resp = json.loads(await ws.recv())
        return resp["result"]["targetId"]
```

### Architecture:
```
Chrome (one instance, one profile, shared cookies)
├── Window targetId=AAA → Session A
├── Window targetId=BBB → Session B
└── Window targetId=CCC → Session C
```

## VNC Takeover (CRITICAL)

When hitting a CAPTCHA, login wall, or any blocker, **send the user a noVNC link:**

```
https://<IP>:<NOVNC_PORT>/vnc.html?password=<PASSWORD>&autoconnect=true&resize=scale
```

### Constructing the link:

**Linux/Docker** (from start.sh output):
```
https://57.129.90.145:10150/vnc.html?password=e0GGP4xeMUL5ga&autoconnect=true&resize=scale
```
- IP: server's public or Tailscale IP
- Port + password: from start.sh output

**macOS:** VNC takeover is NOT available. The user must access the Mac directly
(physical access, macOS Screen Sharing, or their own remote desktop solution).

### Takeover flow:

1. Agent detects blocker (CAPTCHA, login, 2FA)
2. Agent sends noVNC link to user
3. User opens link → sees Chrome → solves the problem
4. User confirms done → agent continues

## Anti-Detection

- **Headful Chrome** — no `HeadlessChrome` in UA
- **`--disable-blink-features=AutomationControlled`** — no `navigator.webdriver=true`
- **UA override via CDP** if needed:
  ```json
  {"method": "Network.setUserAgentOverride", "params": {
    "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"
  }}
  ```

## Security

- SSL/TLS on noVNC (self-signed cert)
- Random 14-char password (Linux) or system auth (macOS)
- CDP: localhost only, never exposed to network
- Chrome Policy: `file://`, `javascript:`, `data:text/html` blocked; extensions blocked; DevTools disabled

## Important: No Kiosk Mode

Do NOT use Chrome's `--kiosk` flag. It hides the tab bar and address bar, making multi-window unusable via VNC. Use `--start-maximized` instead.
