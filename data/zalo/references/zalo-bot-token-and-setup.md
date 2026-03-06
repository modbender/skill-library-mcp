# Bot Token and Setup

## 1) Token acquisition
- Obtain the bot token from the Zalo Bot Platform dashboard.
- Treat it like a secret; never log or commit it.

## 2) OpenClaw integration (if used)
- Configure via env: `ZALO_BOT_TOKEN` or config file (`channels.zalo.botToken`).
- Optional: `channels.zalo.tokenFile` to load from a file.
- Pairing policy: `channels.zalo.dmPolicy` (e.g., pairing/allowlist/open/disabled).
- Webhook configuration:
  - `channels.zalo.webhookUrl`
  - `channels.zalo.webhookSecret`
  - `channels.zalo.webhookPath`

## 3) Webhook vs polling
- Webhook: configure a public HTTPS endpoint and verify requests.
- Polling: run a long-lived worker and store the latest cursor.

## 4) Operational hygiene
- Rotate tokens if compromised.
- Keep separate tokens for dev and prod.
