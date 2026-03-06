---
name: browser-vps-setup-skill
description: Set up a remote-controlled Chrome browser on a Linux VPS with noVNC visual access (via SSH tunnel) and optional authenticated HTTP proxy. Use when the user wants to run a browser on a VPS, control it remotely, view it via noVNC, or route browser traffic through a proxy.
license: MIT
compatibility: Requires apt package manager (Ubuntu/Debian), sudo/root access, internet access. Designed for OpenClaw agents.
metadata:
  author: osipov-anton
  version: "1.0"
---

# Browser on VPS — Setup

Set up Chrome on a Linux VPS so:
- The agent can control it (open pages, click, fill forms, take screenshots) via OpenClaw browser tool
- The user can watch and interact via noVNC in their local browser (over SSH tunnel)
- Optionally: all traffic routes through an authenticated HTTP proxy (for anti-captcha)

---

## Step 1: Install dependencies

```bash
apt-get install -y xvfb x11vnc novnc

# Install real Google Chrome (NOT snap — snap breaks automation)
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/chrome.deb
apt-get install -y /tmp/chrome.deb || apt --fix-broken install -y
```

---

## Step 2: Start the browser stack

```bash
# Clean stale locks
rm -f /tmp/.X99-lock ~/.openclaw/browser/openclaw/user-data/SingletonLock 2>/dev/null

# Virtual display
Xvfb :99 -screen 0 1280x800x24 &
sleep 2

# VNC server (localhost only, no password)
x11vnc -display :99 -forever -nopw -localhost -quiet &
sleep 1

# noVNC web UI on port 6080 (localhost only)
websockify --web /usr/share/novnc 6080 localhost:5900 &
sleep 1

# Chrome with CDP on port 18800
DISPLAY=:99 google-chrome-stable --no-sandbox --disable-gpu \
  --remote-debugging-port=18800 \
  --user-data-dir=~/.openclaw/browser/openclaw/user-data \
  --window-size=1280,800 &
```

---

## Step 3: Connect visually from your laptop

```bash
ssh -L 6080:localhost:6080 root@YOUR_VPS_IP
```

Then open **http://localhost:6080/vnc.html** → click **Connect**.

You'll see the Chrome window live. You and the agent control it simultaneously.

---

## Step 4: Configure OpenClaw

In `~/.openclaw/openclaw.json` add:

```json
{
  "browser": {
    "enabled": true,
    "executablePath": "/usr/bin/google-chrome-stable",
    "attachOnly": true,
    "headless": false,
    "noSandbox": true
  }
}
```

Then restart: `openclaw gateway restart`

The agent can now use the `browser` tool to navigate, click, type, screenshot, etc.

---

## Step 5 (Optional): Authenticated HTTP proxy

If you need a proxy (e.g. mobile proxy for anti-captcha), Chrome can't pass username/password in `--proxy-server`. Solution: run a local Python bridge that forwards with auth injected automatically.

```bash
python3 -c "
import socket, threading, base64, select

UPSTREAM_HOST = 'PROXY_IP'      # e.g. 87.236.22.82
UPSTREAM_PORT = PROXY_PORT       # e.g. 19423
USERNAME = 'PROXY_USER'
PASSWORD = 'PROXY_PASS'
LOCAL_PORT = 18801

auth = base64.b64encode(f'{USERNAME}:{PASSWORD}'.encode()).decode()

def handle(client):
    try:
        data = b''
        while b'\r\n\r\n' not in data:
            data += client.recv(4096)
        upstream = socket.create_connection((UPSTREAM_HOST, UPSTREAM_PORT))
        if b'Proxy-Authorization' not in data:
            data = data.replace(b'\r\n\r\n', f'\r\nProxy-Authorization: Basic {auth}\r\n\r\n'.encode(), 1)
        upstream.sendall(data)
        while True:
            r, _, _ = select.select([client, upstream], [], [], 30)
            if not r: break
            for s in r:
                d = s.recv(65536)
                if not d: return
                (upstream if s is client else client).sendall(d)
    except: pass
    finally:
        try: client.close()
        except: pass
        try: upstream.close()
        except: pass

srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(('127.0.0.1', LOCAL_PORT))
srv.listen(50)
print('Local proxy on 127.0.0.1:18801')
while True:
    c, _ = srv.accept()
    threading.Thread(target=handle, args=(c,), daemon=True).start()
" &
```

Then restart Chrome with proxy:

```bash
pkill -9 chrome
rm -f ~/.openclaw/browser/openclaw/user-data/SingletonLock
DISPLAY=:99 google-chrome-stable --no-sandbox --disable-gpu \
  --remote-debugging-port=18800 \
  --user-data-dir=~/.openclaw/browser/openclaw/user-data \
  --window-size=1280,800 \
  --proxy-server="http://127.0.0.1:18801" &
```

Verify: ask the agent to open `https://api.ipify.org` — it should show the proxy IP, not the VPS IP.

---

## Firewall (recommended)

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
```

noVNC (6080), VNC (5900), and CDP (18800) are all localhost-only — never exposed publicly.

---

## After reboot

All processes (Xvfb, x11vnc, websockify, Chrome) must be restarted. Ask the agent:
> "Start the browser stack on the VPS"

The agent should run Step 2 commands from this skill.
