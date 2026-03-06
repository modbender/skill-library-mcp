---
name: clawtime
description: >
  Install, configure, start, and troubleshoot ClawTime — a private self-hosted webchat UI for
  OpenClaw with passkey (Face ID) auth, Piper TTS voice, and 3D avatar. Requires Cloudflare tunnel
  for HTTPS (passkeys need a real domain). Use when the user wants to install ClawTime on a new
  machine, configure the tunnel, register a passkey, set up TTS, start/stop the server, or
  diagnose errors. Triggered by requests like "install clawtime", "set up clawtime",
  "start clawtime", "clawtime isn't working", "register passkey", "device auth issue".
metadata:
  openclaw:
    requires:
      bins:
        - node
        - git
        - cloudflared
        - npm
      optionalBins:
        - python3
        - ffmpeg
        - piper
    env:
      - PUBLIC_URL
      - GATEWAY_TOKEN
      - SETUP_TOKEN
    files:
      - scripts/install.sh
      - references/device-auth.md
      - references/troubleshooting.md
      - references/launchd.md
    permissions:
      - network (Cloudflare tunnel, git clone, npm install)
      - keychain (store/retrieve GATEWAY_TOKEN and SETUP_TOKEN)
      - filesystem (~/Projects/clawtime, ~/.clawtime, ~/.cloudflared, ~/Library/LaunchAgents)
---

# ClawTime — Local Installation with Cloudflare Tunnel

ClawTime is a private webchat UI connecting to the OpenClaw gateway via WebSocket.
Features: passkey (Face ID/Touch ID) auth, Piper TTS voice, 3D avatar.

**Why Cloudflare is required:** WebAuthn (passkeys) need HTTPS on a real domain.
`http://localhost` only works on the same machine — not from a phone on your network.

## Architecture

```
iPhone/Browser → https://portal.yourdomain.com → Cloudflare Tunnel → localhost:3000 (ClawTime) → ws://127.0.0.1:18789 (OpenClaw Gateway)
```

## Prerequisites

- Node.js v22+
- `cloudflared` CLI: `brew install cloudflared`
- A domain with DNS on Cloudflare (free tier works)
- OpenClaw running: `openclaw status`
- (Optional) Piper TTS + ffmpeg for voice

## Installation Steps

### 1. Clone & install

```bash
cd ~/Projects
git clone https://github.com/youngkent/clawtime.git
cd clawtime
npm install --legacy-peer-deps
```

### 2. Set up Cloudflare Tunnel

```bash
# Login to Cloudflare
cloudflared tunnel login

# Create named tunnel
cloudflared tunnel create clawtime

# Configure routing
# Edit ~/.cloudflared/config.yml:
```

**~/.cloudflared/config.yml:**
```yaml
tunnel: clawtime
credentials-file: /Users/YOUR_USER/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: portal.yourdomain.com
    service: http://localhost:3000
  - service: http_status:404
```

Then in Cloudflare DNS dashboard: add a CNAME record:
- Name: `portal` → Target: `<tunnel-id>.cfargotunnel.com` (Proxied ✅)

### 3. Configure OpenClaw gateway

The gateway must whitelist ClawTime's origin:

```bash
openclaw config patch '{"gateway":{"controlUi":{"allowedOrigins":["https://portal.yourdomain.com"]}}}'
openclaw gateway restart
```

⚠️ `PUBLIC_URL` must match this origin exactly — it's used as the WebSocket origin header for device auth.

### 4. Start ClawTime server

Minimum (no TTS):
```bash
cd ~/Projects/clawtime
PUBLIC_URL=https://portal.yourdomain.com \
SETUP_TOKEN=<your-setup-token> \
GATEWAY_TOKEN=<gateway-token> \
node server.js
```

With Piper TTS:
```bash
cd ~/Projects/clawtime
PUBLIC_URL=https://portal.yourdomain.com \
SETUP_TOKEN=<your-setup-token> \
GATEWAY_TOKEN=<gateway-token> \
BOT_NAME="Beware" \
BOT_EMOJI="🌀" \
TTS_COMMAND='python3 -m piper --data-dir ~/Documents/resources/piper-voices -m en_US-kusal-medium -f /tmp/clawtime-tts-tmp.wav -- {{TEXT}} && ffmpeg -y -loglevel error -i /tmp/clawtime-tts-tmp.wav {{OUTPUT}}' \
node server.js
```

⚠️ **TTS Security Note:** The `{{TEXT}}` placeholder is substituted into a shell command.
ClawTime's server **must** sanitize text before substitution to prevent command injection.
The server should strip or escape shell metacharacters (`; | & $ \` ( ) { } < >`) from user
input before passing it to the TTS command. If you're modifying the TTS pipeline, use
`child_process.execFile()` with argument arrays instead of `child_process.exec()` with string
interpolation.

### 5. Start Cloudflare tunnel

```bash
cloudflared tunnel run clawtime
```

### 6. Register passkey (first time only)

1. Open `https://portal.yourdomain.com/?setup=<your-setup-token>` in **Safari**
2. Follow the passkey (Face ID / Touch ID) prompt
3. ❌ Do NOT use private/incognito mode — Safari blocks passkeys there
4. ❌ Do NOT use Chrome on iOS — use Safari

After registration, access ClawTime at `https://portal.yourdomain.com`.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PUBLIC_URL` | ✅ | Public HTTPS URL (must match `allowedOrigins` in gateway config) |
| `GATEWAY_TOKEN` | ✅ | OpenClaw gateway auth token |
| `SETUP_TOKEN` | For registration | Passphrase for `?setup=<token>` passkey registration URL |
| `TTS_COMMAND` | For voice | Piper command with `{{TEXT}}` and `{{OUTPUT}}` placeholders |
| `BOT_NAME` | No | Display name (default: "Beware") |
| `BOT_EMOJI` | No | Avatar emoji (default: "🌀") |
| `PORT` | No | Server port (default: 3000) |

### Storing Tokens Securely (recommended)

Instead of passing tokens as plaintext env vars or in plist files, store them in macOS Keychain:

```bash
# Store tokens in Keychain
security add-generic-password -s "clawtime-gateway-token" -a "$(whoami)" -w "YOUR_GATEWAY_TOKEN"
security add-generic-password -s "clawtime-setup-token" -a "$(whoami)" -w "YOUR_SETUP_TOKEN"
```

Then retrieve them at launch time:

```bash
GATEWAY_TOKEN=$(security find-generic-password -s "clawtime-gateway-token" -a "$(whoami)" -w) \
SETUP_TOKEN=$(security find-generic-password -s "clawtime-setup-token" -a "$(whoami)" -w) \
PUBLIC_URL=https://portal.yourdomain.com \
node server.js
```

This avoids storing secrets in plaintext on disk.

---

## Device Authentication (Critical)

ClawTime authenticates with the OpenClaw gateway using Ed25519 keypair auth.
This is where most installs break — see details in `references/device-auth.md`.

**Quick summary:**
- Keypair auto-generated in `~/.clawtime/device-key.json` on first run
- Device ID = SHA-256 of raw 32-byte Ed25519 pubkey (NOT the full SPKI-encoded key)
- Signature payload format: `v2|deviceId|clientId|clientMode|role|scopes|signedAtMs|token|nonce`
- If device auth fails → delete `~/.clawtime/device-key.json` and restart

---

## Auto-Start on Boot (macOS launchd)

See `references/launchd.md` for plist templates for both the server and tunnel.

---

## Managing Services

```bash
# Stop server
pkill -f "node server.js"

# Stop tunnel
pkill -f "cloudflared"

# View logs (if backgrounded)
tail -f /tmp/clawtime.log
tail -f /tmp/cloudflared.log

# Restart after code/config changes
pkill -9 -f "node server.js"; sleep 2; # then re-run start command
```

---

## Getting the Gateway Token

```bash
# From macOS Keychain
security find-generic-password -s "openclaw-gateway-token" -a "$(whoami)" -w

# From config file
cat ~/.openclaw/openclaw.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('gateway',{}).get('token',''))"
```

---

## Passkey Operations

```bash
# Reset passkeys (re-register from scratch)
echo '[]' > ~/.clawtime/credentials.json
# Restart server, then visit /?setup=<token>

# Reset device key (new keypair on next restart)
rm ~/.clawtime/device-key.json
```

---

## Troubleshooting

See `references/troubleshooting.md` for all common errors and fixes.
See `references/device-auth.md` for deep-dive on gateway auth issues.
