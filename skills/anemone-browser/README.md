# 🌊 Anemone

<p align="center">
  <img src="assets/anemone-banner.png" alt="Anemone - Managed browser for OpenClaw" width="600">
</p>

<p align="center">
  <em>A managed Chrome environment for <a href="https://github.com/openclaw/openclaw">OpenClaw</a> that just works — anywhere.</em>
</p>

---

## The Problem

OpenClaw agents need a browser. But getting one that reliably works is harder than it should be:

- **Mac/Desktop** — Browser Relay extension disconnects, requires manual re-attach
- **Docker/VPS** — Headless Chrome gets blocked by Google, Cloudflare, CAPTCHA walls
- **Remote servers** — No GUI, no way for humans to intervene when things go wrong

You shouldn't have to fight your browser. You should be building agents.

## The Solution

Anemone gives OpenClaw a **managed Chrome that runs anywhere** — Mac, Docker, Ubuntu, VPS — with:

- 🐟 **Anti-detection** — Headful Chrome, clean fingerprint, no "HeadlessChrome" leaks
- 🖥️ **Remote access** — Web-based VNC (noVNC) so you can see and control the browser from anywhere
- 🤖 **Agent-native** — CDP integration, OpenClaw controls Chrome directly
- 🔒 **Secure** — SSL, password auth, Chrome Policy locks down file access and extensions
- 🔄 **Persistent** — Cookies and login sessions survive restarts
- 👤 **Human-in-the-loop** — When CAPTCHA hits, open VNC in your browser and solve it. Done.

No more relay disconnects. No more blocked searches. No more blind headless Chrome.

## Quick Start

### Docker / VPS / Remote Server

```bash
# 1. Install dependencies (once)
docker exec <container> bash /path/to/setup.sh

# 2. Start Anemone
docker exec <container> bash /root/start.sh

# Output:
# ==========================================
#   VNC Browser Environment Ready!
# ==========================================
#   noVNC:    https://<IP>:6080/vnc.html?password=Ax7kM2pQr9nB3w&autoconnect=true&resize=scale
#   Password: Ax7kM2pQr9nB3w
#   CDP:      http://127.0.0.1:9222/json/version
# ==========================================
```

### Ubuntu (bare metal)

```bash
# Same scripts work directly on Ubuntu
bash setup.sh
bash start.sh
```

### macOS

```bash
# One command — configures OpenClaw to use managed Chrome
bash setup-mac.sh

# Then use it:
openclaw browser start
openclaw browser open https://www.google.com
```

No VNC needed on Mac (you have a display). The agent's `browser` tool works automatically after setup.

## How It Works

```
 You (any browser, anywhere)           OpenClaw Agent
      │                                      │
      │ HTTPS + password                     │ CDP (localhost)
      ▼                                      ▼
 ┌──────────────────────────────────────────────────┐
 │                   Anemone                        │
 │                                                  │
 │   noVNC ──► x11vnc ──► Xvfb (virtual display)   │
 │                              │                   │
 │                     Chrome (headful, real)        │
 │                        CDP :9222                  │
 │                              │                   │
 │                  ~/.chrome-profile                │
 │                (persistent cookies)               │
 └──────────────────────────────────────────────────┘
```

**Human-in-the-loop flow:**
1. Agent browses normally via CDP
2. Hits a CAPTCHA or login wall
3. Agent sends you the VNC link
4. You open it in your browser, solve the CAPTCHA
5. Agent continues automatically

## Configuration

```bash
bash start.sh [password] [novnc_port] [cdp_port] [resolution]

# Random password (default):
bash start.sh

# Fixed password:
bash start.sh "my-secure-password"

# Custom ports + resolution:
bash start.sh "my-password" 6080 9222 1920x1080x24
```

## OpenClaw Integration

Add to your OpenClaw config (`~/.openclaw/openclaw.json`):

```json
{
  "browser": {
    "headless": false,
    "noSandbox": true,
    "executablePath": "/usr/bin/google-chrome-stable"
  }
}
```

Then use `browser` tool normally. No relay needed.

## Security

| Layer | Protection |
|-------|-----------|
| Network | SSL/TLS encryption (self-signed cert) |
| Auth | Random 14-char password (or custom) |
| CDP | Localhost only — not exposed to network |
| Chrome Policy | `file://` blocked, extensions blocked, DevTools disabled, `data:text/html` blocked |
| Isolation | Docker container separation from host |

## Tested

| Environment | IP Type | Google | Scholar | Cloudflare |
|-------------|---------|:------:|:-------:|:----------:|
| Docker (home server, Taiwan) | Residential | ✅ | ✅ | ✅ |
| Docker (OVH, France) | Datacenter | ✅ | ✅ | ✅ |

## Files

| File | Purpose |
|------|---------|
| `setup.sh` | One-time: installs Chrome, Xvfb, VNC, noVNC |
| `start.sh` | Starts Anemone (safe to re-run) |
| `test.py` | Verifies Google/Scholar access works |

## Why "Anemone"?

Sea anemones and crabs are natural symbionts — the anemone protects the crab, the crab carries the anemone. Just like Anemone protects OpenClaw's browser from detection. And yes, it sounds a bit like "anonymous" 🌊

## License

MIT

---

<p align="center">
  Part of the <a href="https://github.com/openclaw/openclaw">OpenClaw</a> ecosystem 🦀
</p>
