---
name: clawket
description: >-
  Generate QR codes for Clawket mobile app to pair with the local OpenClaw Gateway.
  Use when user mentions: Clawket pairing, login Clawket, QR code, mobile app connection,
  connect phone to Gateway, or scan to login.
---

# Clawket Gateway QR Code

Generate a QR code that the Clawket mobile app can scan to auto-configure Gateway connection (URL + auth token).

## Generate QR Code

Run the script:

```bash
bash SKILL_DIR/scripts/gateway-qr.sh
```

The script will:
1. Read `~/.openclaw/openclaw.json` for the auth token
2. Detect the local LAN IP address
3. Generate a QR code as a PNG image at `~/.openclaw/media/clawket-qr.png`
4. Also print an ASCII QR code to the terminal

Send the PNG to the user via the `message` tool (`filePath: ~/.openclaw/media/clawket-qr.png`).

## QR Payload Format

The QR code contains a JSON object:

```json
{
  "host": "192.168.1.100",
  "port": 18789,
  "token": "...",
  "tls": false
}
```

The Clawket app scans this and auto-fills Gateway URL + auth token, then connects.

## Troubleshooting

- If `qrencode` is not installed: `brew install qrencode` (macOS) / `sudo apt install qrencode` (Linux) / `choco install qrencode` (Windows)
- If the LAN IP detection fails, the script falls back to `127.0.0.1`
- The token is read directly from the JSON config file (not via `openclaw config get` which redacts it)
