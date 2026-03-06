# Server install (required once per server)

ClawHub installs the **skill** (prompt/instructions). The `rr_jobs_search` tool is provided by an OpenClaw **gateway extension** that must be deployed on the server.

This folder contains the exact files you need for OpenClaw 2026.2.x (as in your setup).

## 1) Deploy the extension root

Copy these two files into:

- `~/.openclaw/extensions/openclaw.plugin.json`
- `~/.openclaw/extensions/index.ts`

## 2) Enable plugin entry in `~/.openclaw/openclaw.json`

Ensure:
```json5
"plugins": {
  "entries": {
    "index": { "enabled": true },
    "whatsapp": { "enabled": true }
  }
}
```

## 3) Set RR_API_KEY for the systemd service

```bash
sudo systemctl edit openclaw-gateway.service
```

Add:
```ini
[Service]
Environment="RR_API_KEY=YOUR_KEY_HERE"
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl restart openclaw-gateway.service
```

## 4) Restart gateway after skill updates too

```bash
openclaw gateway restart
```

## Verify

```bash
openclaw agent --to <your_number> --message "Find 2 UK remote product manager jobs" --json --verbose on
```
