---
name: vitavault
description: VitaVault iOS app integration - sync Apple Health data directly to your AI agent. Auto-setup webhook, token generation, and HTTPS exposure. Works with any iPhone, no Mac required.
license: Apache-2.0
compatibility: Any OpenClaw agent. Pairs with VitaVault iOS app (free on App Store).
metadata:
  category: health
  platforms: ios
  author: BrandonS7
---

# VitaVault - Your Health, Decoded

Sync Apple Health data from [VitaVault](https://vitavault.io) iOS app directly to your OpenClaw agent. No shared servers, no middleman - data flows phone to your agent only.

> **No Mac required.** Install VitaVault from [TestFlight](https://testflight.apple.com/join/A4G27HBt) (beta) or the App Store.

## Agent Setup Guide (DO THIS WHEN USER SAYS "set up VitaVault")

When your user asks to set up VitaVault sync, follow these steps automatically. Don't ask the user to do the technical parts - handle it yourself and hand them the URL + token at the end.

### Step 1: Generate a sync token

```bash
# Generate a secure random token
python3 -c "import secrets; print(secrets.token_hex(32))" > ~/.config/vitavault/sync-token
mkdir -p ~/.config/vitavault
TOKEN=$(cat ~/.config/vitavault/sync-token)
echo "Token: $TOKEN"
```

### Step 2: Start the webhook

```bash
VITAVAULT_SYNC_TOKEN="$TOKEN" nohup python3 scripts/webhook.py --host 0.0.0.0 --port 8787 > /tmp/vitavault-webhook.log 2>&1 &
```

The webhook listens for health data POSTs and saves snapshots to `~/vitavault/data/`.

### Step 3: Expose it over HTTPS

The VitaVault iOS app requires HTTPS (iOS App Transport Security). You MUST expose the webhook over HTTPS. Detect what's available and use the first option that works:

**Option A: Tailscale Funnel (recommended if Tailscale is installed)**
```bash
# Check if Tailscale is available
tailscale status 2>/dev/null
# If yes, expose via Funnel:
sudo tailscale funnel --bg --set-path /vitavault http://127.0.0.1:8787
# Your URL will be: https://<your-tailscale-hostname>/vitavault
tailscale funnel status  # to see the URL
```

**Option B: Cloudflare Tunnel (if cloudflared is installed)**
```bash
cloudflared tunnel --url http://localhost:8787
# Gives you a temporary https://*.trycloudflare.com URL
# For permanent: set up a named tunnel with a custom domain
```

**Option C: VPS with a domain + reverse proxy (nginx/caddy)**
If the host already has a domain with HTTPS (nginx, caddy, etc.), add a reverse proxy rule:
```nginx
location /vitavault {
    proxy_pass http://127.0.0.1:8787;
}
```
URL would be: `https://yourdomain.com/vitavault`

**Option D: ngrok (quick testing)**
```bash
ngrok http 8787
# Gives you a temporary https://*.ngrok-free.app URL
```

### Step 4: Verify it works

```bash
curl -s https://YOUR-URL/health
# Should return: {"ok": true}
```

### Step 5: Give the user their credentials

Tell your user:

> **Open VitaVault on your iPhone -> Settings -> OpenClaw**
>
> **Webhook URL:** `https://YOUR-URL`
> **Sync Token:** `<the token you generated>`
>
> Paste both in and tap Connect.

That's it. Once connected, VitaVault auto-syncs health data every time the app opens.

### Step 6: Make it persistent (recommended)

The webhook should survive reboots. Create a systemd service:

```bash
cat > /tmp/vitavault-webhook.service << 'EOF'
[Unit]
Description=VitaVault Webhook Receiver
After=network.target

[Service]
Type=simple
User=$USER
Environment=VITAVAULT_SYNC_TOKEN=<TOKEN>
ExecStart=/usr/bin/python3 /path/to/skills/vitavault/scripts/webhook.py --host 127.0.0.1 --port 8787
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
# Adjust paths and token, then:
sudo cp /tmp/vitavault-webhook.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now vitavault-webhook
```

## Querying Health Data

Once data is syncing, use these scripts to read it:

```bash
# Latest snapshot summary
python3 scripts/summary.py

# Raw latest JSON
python3 scripts/query.py latest

# Last 7 days
python3 scripts/query.py week

# Date range
python3 scripts/query.py range 2026-02-01 2026-02-28
```

Data is stored locally at `~/vitavault/data/` as timestamped JSON files.

## What You Can Do With the Data

Once synced, your agent can:
- Track trends in steps, sleep, HRV, resting HR, blood oxygen
- Compare current week vs prior week
- Detect unusual drops/spikes and flag risks
- Build morning health briefings
- Generate doctor appointment summaries
- Suggest habit changes based on actual data

## Working with Manual Exports

Users can also export data manually from VitaVault (no webhook needed):

### AI-Ready Format (Plain Text)
Pre-formatted for AI analysis. Users export from VitaVault and paste directly.

### JSON Format
Structured data with nested metrics, dates, and units.

### CSV Format
One row per day, opens in Excel/Google Sheets.

When a user shares an export:
1. Acknowledge the data
2. Highlight 2-3 key observations (positive and concerning)
3. Give 3 specific, actionable recommendations
4. Offer to dig deeper into any metric

## Privacy

VitaVault sync data flows directly: **iPhone -> your OpenClaw agent**. No shared backend, no central relay, no third-party storage. Data is saved on your agent's host at `~/vitavault/data/` and nowhere else.

## Links

- **App**: [VitaVault on TestFlight](https://testflight.apple.com/join/A4G27HBt) (beta)
- **Website**: [vitavault.io](https://vitavault.io)
- **Developers**: [vitavault.io/developers](https://vitavault.io/developers/)
- **Privacy**: [vitavault.io/privacy](https://vitavault.io/privacy/)
