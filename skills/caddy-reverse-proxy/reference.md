# Caddy Reverse Proxy — Reference

Self-hosted reverse proxy using Caddy. Routes `*.YOUR_DOMAIN` subdomains to local services over HTTPS. Designed for Tailscale-only access (no public exposure).

## Quick Reference

- **Binary:** `~/.local/bin/caddy` (custom build with `caddy-dns/vercel` plugin)
- **Caddyfile:** `~/.config/caddy/Caddyfile`
- **Ports:** 443 (HTTPS), 80 (HTTP redirect)
- **Bound to:** Tailscale IP only (`YOUR_TAILSCALE_IP`)
- **TLS:** Let's Encrypt via DNS-01 challenge (Vercel DNS API)
- **DNS:** `YOUR_DOMAIN` + `*.YOUR_DOMAIN` → A record → `YOUR_TAILSCALE_IP`

**Port 443 on macOS:** Non-root processes can't bind ports <1024. Use a system LaunchDaemon (runs as root) with HOME/XDG_DATA_HOME/XDG_CONFIG_HOME env vars so Caddy can find cert storage.

**Port 443 on Linux:** Grant the capability once: `sudo setcap 'cap_net_bind_service=+ep' ~/.local/bin/caddy` — then a user service works fine.

## Example Apps

Adapt this table to your own setup. The pattern: one subdomain per app, each proxied to a local port.

| URL | App | Local Port | Service |
|-----|-----|------------|---------|
| https://YOUR_DOMAIN | Dashboard | — (inline HTML in Caddyfile) | — |
| https://myapp.YOUR_DOMAIN | Your Web App | 3100 | `com.yourusername.myapp` |
| https://api.YOUR_DOMAIN | API Server | 3101 | `com.yourusername.api` |

**Port convention:** Permanent apps in the 3100 range, dev servers at 5200+ (managed by [dev-serve](https://clawhub.com/skills/dev-serve)).

**Vercel API Token:** Create a long-lived `vcp_*` token at https://vercel.com/account/tokens (no expiration — must be revoked if exposed). On macOS, store it in the LaunchDaemon plist env vars. On Linux, store it in an env file loaded by systemd (see Service Management below). You can push a new token to the live config without restart via `curl -X POST http://localhost:2019/load` with the token in the JSON config.

## Quick Dev Servers

Use `dev-serve` to spin up dev servers with automatic Caddy routing:

```bash
dev-serve up ~/projects/myapp        # → https://myapp.YOUR_DOMAIN
dev-serve down myapp              # clean up when done
dev-serve ls                      # list active dev servers
```

Companion skill: [dev-serve](https://clawhub.com/skills/dev-serve). Starts a tmux session, adds a Caddy route, reloads — one command.

## Architecture

```
Phone/Laptop (Tailscale)
  → DNS: *.YOUR_DOMAIN → YOUR_TAILSCALE_IP (Tailscale IP)
    → Caddy (port 443, HTTPS with Let's Encrypt certs via DNS-01 challenge)
      → reverse_proxy to localhost:<port>
```

## Key Files

| What | macOS | Linux |
|------|-------|-------|
| **Caddyfile** | `~/.config/caddy/Caddyfile` | `~/.config/caddy/Caddyfile` |
| **Caddy binary** | `~/.local/bin/caddy` | `~/.local/bin/caddy` |
| **Caddy service** | `/Library/LaunchDaemons/com.caddyserver.caddy.plist` | `~/.config/systemd/user/caddy.service` |
| **Vercel API token** | In LaunchDaemon plist env vars | `~/.secrets/vercel/.env` (EnvironmentFile) |
| **Caddy logs** | `/var/log/caddy.log`, `/var/log/caddy-error.log` | `journalctl --user -u caddy` |
| **DNS records** | Vercel DNS for `YOUR_DOMAIN` | Vercel DNS for `YOUR_DOMAIN` |

## How to Add a New App

### 1. Set up the app as a background process

Clone the repo, install deps, and create a service to keep it running.

Key points for any platform:
- **Bind to 0.0.0.0** so Caddy can proxy to it. Most frameworks need an explicit flag (Vite: `--host 0.0.0.0`, Next.js custom servers often default to 0.0.0.0).
- **Pick the next port** in the 3100 range (check the Apps table above).
- **Use direct binary paths**, not shell wrappers.

#### macOS (LaunchAgent)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.yourusername.APPNAME</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/node</string>
        <string>server/index.js</string>
    </array>
    <key>WorkingDirectory</key>
    <string>~/projects/APPNAME</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HOME</key>
        <string>~</string>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>PORT</key>
        <string>31XX</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>~/Library/Logs/APPNAME.log</string>
    <key>StandardErrorPath</key>
    <string>~/Library/Logs/APPNAME-error.log</string>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.yourusername.APPNAME.plist
```

#### Linux (systemd user service)

```ini
# ~/.config/systemd/user/APPNAME.service
[Unit]
Description=APPNAME
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/yourusername/projects/APPNAME
ExecStart=/usr/bin/node server/index.js
Environment=PORT=31XX
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now APPNAME
# Ensure services survive logout:
loginctl enable-linger $(whoami)
```

### 2. Add to Caddyfile

Add a server block and a dashboard link:

```caddy
# App Name
appname.YOUR_DOMAIN {
    import vercel_tls
    reverse_proxy localhost:31XX
}
```

Also add a `<li>` entry in the dashboard HTML block at the top of the Caddyfile.

### 3. Reload Caddy

```bash
# Preferred: reload via admin API (no sudo needed)
~/.local/bin/caddy reload --config ~/.config/caddy/Caddyfile --address localhost:2019

# Alternative: if admin API isn't listening
~/.local/bin/caddy reload --config ~/.config/caddy/Caddyfile
```

TLS cert provisioning takes 30–60 seconds for new subdomains (DNS-01 challenge via Vercel API).

### 4. (Optional) OpenClaw Gateway integration

If your app connects to the OpenClaw gateway, see `OPENCLAW.md` for additional config (trustedProxies, allowedOrigins, device pairing).

## Custom Caddy Build

You need Caddy built with the `caddy-dns/vercel` plugin. If you use a **personal** Vercel account (no team), the upstream plugin works as-is:

```bash
# Install xcaddy: https://github.com/caddyserver/xcaddy
xcaddy build --with github.com/caddy-dns/vercel
cp caddy ~/.local/bin/caddy
```

If you use a **Vercel team account**, the upstream plugin doesn't pass `teamId` in API calls (as of Feb 2026). You'll need to either:
1. Fork and patch `caddy-dns/vercel` to add `team_id` support, or
2. Use the `--with github.com/caddy-dns/vercel=./your-patched-version` flag with xcaddy

## Service Management

### macOS (LaunchDaemon — needs root for port 443)

```bash
# Check status
sudo launchctl list | grep caddy

# View logs
tail -f /var/log/caddy-error.log

# Stop + Start (use legacy load/unload — more reliable than bootout/bootstrap)
sudo launchctl unload /Library/LaunchDaemons/com.caddyserver.caddy.plist
sudo launchctl load /Library/LaunchDaemons/com.caddyserver.caddy.plist

# Reload config (no restart needed, no sudo needed)
~/.local/bin/caddy reload --config ~/.config/caddy/Caddyfile --address localhost:2019
```

**Note:** `sudo launchctl bootstrap system /Library/LaunchDaemons/...` can fail with `Input/output error` if the service is already loaded. Use `unload`/`load` as a more reliable alternative.

### Linux (systemd user service)

On Linux, Caddy can run as a user service (no root needed if binding to ports ≥1024, or if using `setcap`):

```bash
# Grant Caddy permission to bind low ports (once)
sudo setcap 'cap_net_bind_service=+ep' ~/.local/bin/caddy

# Service file: ~/.config/systemd/user/caddy.service
```

```ini
[Unit]
Description=Caddy Reverse Proxy
After=network.target

[Service]
Type=simple
EnvironmentFile=%h/.secrets/vercel/.env
ExecStart=%h/.local/bin/caddy run --config %h/.config/caddy/Caddyfile
ExecReload=%h/.local/bin/caddy reload --config %h/.config/caddy/Caddyfile
Restart=always
RestartSec=5
Environment=XDG_DATA_HOME=%h/.local/share
Environment=XDG_CONFIG_HOME=%h/.config

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now caddy

# Ensure Caddy survives logout
loginctl enable-linger $(whoami)

# Check status / logs
systemctl --user status caddy
journalctl --user -u caddy -f

# Reload config
~/.local/bin/caddy reload --config ~/.config/caddy/Caddyfile
```

**Secrets:** Store your Vercel API token and team ID in an env file (e.g., `~/.secrets/vercel/.env`):
```bash
VERCEL_API_TOKEN=vcp_your_token_here
VERCEL_TEAM_ID=team_your_id_here
```

## How HTTPS Works

Custom Caddy build with patched `vercel` DNS provider:
1. Requests Let's Encrypt cert per subdomain
2. Proves ownership via DNS-01 (creates `_acme-challenge` TXT via Vercel API with teamId)
3. Auto-renews before expiry

Works without public access — DNS-01 doesn't need inbound HTTP.

Vercel API token is stored in the Caddy service env vars (plist on macOS, EnvironmentFile on Linux). If expired, certs fail with `No TXT record found at _acme-challenge...`. Regenerate at Vercel dashboard and update the service config.

## Troubleshooting

**Cert not issuing:**
```bash
# macOS
tail -50 /var/log/caddy-error.log | grep -i error
# Linux
journalctl --user -u caddy --since "1 hour ago" | grep -i error
# Common: expired Vercel API token → update token, restart Caddy
```

**DNS not resolving:**
```bash
dig +short appname.YOUR_DOMAIN  # should be YOUR_TAILSCALE_IP
# Wildcard *.YOUR_DOMAIN covers all subdomains
```

**App not loading through Caddy (curl exit 35 / TLS error):**
Cert hasn't provisioned yet. Wait 30-60 seconds. Check Caddy error log for ACME failures.

**App showing 502:**
Check the app's logs. Common causes:
- App not running or crashed
- App bound to `127.0.0.1` instead of `0.0.0.0`
- Wrong port in Caddyfile
