# Telegram Mini App Canvas (OpenClaw Skill)

[![ClawHub](https://img.shields.io/badge/ClawHub-openclaw--tg--canvas-blue)](https://clawhub.ai/skills/openclaw-tg-canvas)

This skill provides a Telegram Mini App with three capabilities:

1. **Canvas rendering** — push HTML, markdown, or A2UI content to a live canvas in the Mini App.
2. **Interactive terminal** *(opt-in, JWT-gated)* — a browser-based terminal backed by a server-side PTY (bash shell). This is a significant privilege: it grants shell access to the machine running the server, scoped to the process user. Only users in `ALLOWED_USER_IDS` can open it.
3. **OpenClaw Control UI proxy** *(opt-in, off by default)* — proxies `/oc/*` to a local OpenClaw gateway. Requires `ENABLE_OPENCLAW_PROXY=true` and optionally `OPENCLAW_GATEWAY_TOKEN`. The server does **not** read any local credential files automatically.

Only approved Telegram user IDs (via `ALLOWED_USER_IDS`) can access any authenticated feature. Sessions are verified via Telegram `initData` HMAC-SHA256.

**Links:** [GitHub](https://github.com/clvv/openclaw-tg-canvas) · [ClawHub](https://clawhub.ai/skills/openclaw-tg-canvas)

## Quick Start

1. Clone or copy this folder into your OpenClaw workspace.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Set environment variables (or create a `.env` file):
   ```bash
   export BOT_TOKEN=...
   export ALLOWED_USER_IDS=123456789
   export JWT_SECRET=...
   export PORT=3721
   ```
4. Start the server and Cloudflare tunnel:
   ```bash
   bash scripts/start.sh
   ```
5. Configure the bot menu button:
   ```bash
   BOT_TOKEN=... MINIAPP_URL=https://xxxx.trycloudflare.com node scripts/setup-bot.js
   ```

## Security

**What the Cloudflare tunnel exposes publicly:**

| Endpoint | Public? | Auth |
| --- | --- | --- |
| `GET /` | ✅ | None (serves static Mini App HTML) |
| `POST /auth` | ✅ | Telegram `initData` HMAC-SHA256 + `ALLOWED_USER_IDS` check |
| `GET /state` | ✅ | JWT required |
| `GET /ws` | ✅ | JWT required (WebSocket upgrade) |
| `POST /push` | ❌ not public-safe by IP alone | **`PUSH_TOKEN` required** + loopback check |
| `POST /clear` | ❌ not public-safe by IP alone | **`PUSH_TOKEN` required** + loopback check |
| `GET /health` | ❌ loopback-only | Loopback check |
| `GET/WS /ws/terminal` | ✅ | JWT required — **opens a bash PTY on the server** |
| `GET/WS /oc/*` | ✅ (when enabled) | JWT required; only available when `ENABLE_OPENCLAW_PROXY=true` |

> ⚠️ **Cloudflared loopback bypass:** `cloudflared` connects to the server via local TCP, so all tunnel traffic appears as `127.0.0.1`. The loopback IP check does **not** protect `/push` or `/clear` from remote callers when a tunnel is active. `PUSH_TOKEN` is enforced at startup to compensate.

**Recommendations:**
- `PUSH_TOKEN` is **required** — the server refuses to start without it. Generate: `openssl rand -hex 32`
- Use a strong random `JWT_SECRET` (32+ bytes).
- Keep `BOT_TOKEN`, `JWT_SECRET`, and `PUSH_TOKEN` secret; rotate if compromised.
- The terminal feature grants shell access to the server as the process user. Ensure `ALLOWED_USER_IDS` is tightly controlled.
- `ENABLE_OPENCLAW_PROXY` is **off by default**. Only enable it intentionally.

## HTTPS via nginx + Let's Encrypt (domain-based, no Cloudflare)

Use this if you already have a subdomain pointing at your VPS.

**1) Nginx HTTP config (ACME + proxy):**

```nginx
server {
  listen 80;
  listen [::]:80;
  server_name canvas.example.com;

  location ^~ /.well-known/acme-challenge/ {
    root /var/www/certbot;
    default_type text/plain;
  }

  location / {
    proxy_pass http://127.0.0.1:3721;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
  }
}
```

```bash
sudo mkdir -p /var/www/certbot/.well-known/acme-challenge
sudo nginx -t && sudo systemctl reload nginx
```

**2) Certbot (webroot):**

```bash
sudo certbot certonly --webroot -w /var/www/certbot -d canvas.example.com \
  -m you@example.com --agree-tos --non-interactive
```

**3) Enable HTTPS + redirect (certbot can do this):**

```bash
sudo certbot --nginx -d canvas.example.com -m you@example.com --agree-tos --redirect --non-interactive
```

**4) Verify (IPv4/IPv6):**

```bash
curl -4 https://canvas.example.com/
curl -6 https://canvas.example.com/
```

If IPv6 fails, add `listen [::]:80` / `listen [::]:443` or remove the AAAA record.

## Interactive Terminal

The Mini App includes a browser-based terminal backed by a server-side PTY.

> ⚠️ **This is a high-privilege feature.** The terminal opens a bash session as the server process user. Anyone authenticated via `ALLOWED_USER_IDS` can run arbitrary shell commands on the server. Ensure `ALLOWED_USER_IDS` contains only users you trust with shell access.

**How it works:**
- The Mini App topbar shows a **Terminal** button once authenticated.
- Tapping it opens a full-screen xterm.js terminal connected to `/ws/terminal`.
- The WebSocket is JWT-authenticated (same `ALLOWED_USER_IDS` gate as the canvas).
- The PTY session runs as the server process user (set `User=` in the systemd unit).
- A mobile-friendly key toolbar is shown at the bottom: `Ctrl`, `Alt`, `Esc`, `Tab`, arrows.

The terminal feature is always compiled in but requires authentication — it is not separately togglable via env var.

## OpenClaw Control UI Proxy (opt-in)

This skill can optionally proxy the OpenClaw Control UI through the Mini App under `/oc/*`.

**This feature is off by default.** Enable it explicitly:

```env
ENABLE_OPENCLAW_PROXY=true
```

When enabled:
- `/oc/*` HTTP and WebSocket requests are proxied to the local OpenClaw gateway.
- If `OPENCLAW_GATEWAY_TOKEN` is set, it is injected as `Authorization: Bearer` on proxied requests.
- The server does **not** read `~/.openclaw/openclaw.json` or any other local credential file. The token must be supplied explicitly via env var.

Other proxy env vars (all optional, used only when proxy is enabled):

| Variable | Default | Description |
| --- | --- | --- |
| `OPENCLAW_PROXY_HOST` | `127.0.0.1` | Hostname of the local OpenClaw gateway |
| `OPENCLAW_PROXY_PORT` | `18789` | Port of the local OpenClaw gateway |
| `OPENCLAW_GATEWAY_TOKEN` | *(unset)* | Auth token injected into proxied requests |

For the proxied Control UI WebSocket to be accepted, add the Mini App origin to OpenClaw gateway config:

```json
{
  "gateway": {
    "controlUi": {
      "allowedOrigins": ["https://your-canvas-url.example.com"]
    }
  }
}
```

## Pushing Content from the Agent

Use the CLI or the HTTP `/push` API (loopback-only):

```bash
curl -X POST http://127.0.0.1:3721/push \
  -H 'Content-Type: application/json' \
  -d '{"html":"<h1>Hello Canvas</h1>"}'
```

Other formats:

```bash
curl -X POST http://127.0.0.1:3721/push \
  -H 'Content-Type: application/json' \
  -d '{"markdown":"# Hello"}'

curl -X POST http://127.0.0.1:3721/push \
  -H 'Content-Type: application/json' \
  -d '{"a2ui": {"type":"text","text":"Hello"}}'
```

CLI examples:

```bash
tg-canvas push --html "<h1>Hello</h1>"
tg-canvas push --markdown "# Hello"
tg-canvas push --a2ui @./a2ui.json
```

See `SKILL.md` for the agent command (`tg-canvas push`) and environment details.

## Health Endpoint

```bash
curl http://127.0.0.1:3721/health
```

Returns server uptime, active WebSocket client count, and whether a canvas state exists.

## Systemd (optional)

1) Copy the unit file and adjust paths if needed:

```bash
sudo cp tg-canvas.service /etc/systemd/system/tg-canvas.service
sudo systemctl daemon-reload
```

2) Create `/etc/default/tg-canvas` or use the existing `.env` in the repo:

```bash
sudo mkdir -p /etc/tg-canvas
sudo cp .env /etc/tg-canvas/.env
```

3) Update the unit file to point at the env file location:

```ini
EnvironmentFile=/etc/tg-canvas/.env
```

4) Enable and start:

```bash
sudo systemctl enable --now tg-canvas
sudo systemctl status tg-canvas
```

## Architecture

```
+-----------+        +------------------+        +---------------------+
|  Agent    |  push  |  Local server    |  HTTPS |  Telegram Mini App  |
| (OpenClaw)| -----> |  (localhost)     | -----> |  (Cloudflare URL)   |
+-----------+        +------------------+        +---------------------+
          ^                    |
          |                    | Telegram initData verification
          +--------------------+ (authorized users only)
```

## Publishing to ClawhHub

Ensure `SKILL.md`, scripts, and `.env.example` are included. Tag the repo with a version and publish according to ClawhHub guidelines.

## Security Summary

- **Auth:** Telegram `initData` HMAC-SHA256 verified against `BOT_TOKEN`; `auth_date` freshness enforced; access restricted to `ALLOWED_USER_IDS`.
- **JWTs** are short-lived (`JWT_TTL_SECONDS`, default 15 min).
- **`PUSH_TOKEN` is required** — the server exits at startup without it. The loopback IP check alone is insufficient when `cloudflared` is active.
- **Terminal** grants real shell access. Only list users in `ALLOWED_USER_IDS` who should have shell access to your server.
- **Proxy** is off by default (`ENABLE_OPENCLAW_PROXY` must be set to `"true"` explicitly). No local credential files are read automatically.
- Keep `.env` permissions tight (`chmod 600 .env`) and rotate secrets if compromised.

## Canvas Learnings (from live testing)

- **Inline scripts in injected HTML won't run** in Telegram WebView; the renderer re-inserts `<script>` tags to execute.
- **CORS can block direct fetches** from the Mini App; embed sanctioned widgets (e.g., TradingView) or proxy data server-side.
- **WebSocket upgrades require nginx headers** (`Upgrade`/`Connection`), or the app will show "Connecting" loops.
- **HTTPS is mandatory** for Mini Apps.
