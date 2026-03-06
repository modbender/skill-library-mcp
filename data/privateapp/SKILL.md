---
name: privateapp
description: "Personal PWA dashboard server with plugin apps. Use when: (1) installing or setting up PrivateApp, (2) starting/stopping/restarting the service, (3) building frontends after changes, (4) adding new app plugins, (5) configuring push notifications. Requires Python 3.9+, Node.js 18+. Runs as systemd user service or launchd plist."
---

# PrivateApp

Personal PWA dashboard — FastAPI backend + React/Vite frontend with plugin apps.

## Screenshots

![Home](assets/screenshots/home.png)
![System](assets/screenshots/system.png)
![Files](assets/screenshots/files.png)

## Setup

```bash
# Clone and install (creates venv, builds frontends, sets up systemd/launchd)
git clone https://github.com/camopel/PrivateApp.git ~/Workspace/PrivateApp
cd ~/Workspace/PrivateApp
bash scripts/install.sh [--port 8800]
```

Copy `scripts/config.example.json` → `scripts/config.json` and edit:
```json
{
  "host": "0.0.0.0",
  "port": 8800,
  "data_dir": "~/.local/share/privateapp",
  "file_browser": { "root": "~" },
  "push": { "vapid_email": "you@example.com" }
}
```

## Service Management

```bash
# Linux (systemd user service)
systemctl --user start privateapp
systemctl --user stop privateapp
systemctl --user restart privateapp
systemctl --user status privateapp

# macOS (launchd)
launchctl load ~/Library/LaunchAgents/com.privateapp.server.plist
launchctl unload ~/Library/LaunchAgents/com.privateapp.server.plist

# Manual
.venv/bin/python3 scripts/server.py --host 127.0.0.1 --port 8800
```

## Build Frontends

After any frontend change, rebuild:
```bash
# Build shell (home screen)
cd frontend && npm run build

# Build all app frontends
for app_dir in apps/*/frontend; do
  [ -f "$app_dir/package.json" ] && (cd "$app_dir" && npm install && npm run build)
done

# Or use the install script which builds everything
bash scripts/install.sh
```

Then restart the service.

## Built-in Apps

| App | Shortcode | Description |
|-----|-----------|-------------|
| 📊 System | `sysmon` | CPU, RAM, disk, GPU stats and service health |
| 📁 Files | `files` | Browse, preview, and share files |

## Adding a New App

Create `apps/{app-id}/` with:
- `app.json` — metadata (id, name, shortcode, icon, description)
- `backend/routes.py` — FastAPI router (mounted at `/api/app/{shortcode}/`)
- `frontend/` — React SPA (Vite, builds to `frontend/dist/`)

Shortcode must be unique. The app loader auto-discovers on startup.

See the existing apps for reference patterns. Key conventions:
- All routes `async def`, return plain dicts
- Frontend uses CSS custom properties for dark mode
- Input font-size ≥ 16px (prevents iOS auto-zoom)
- Every app has a back button linking to `/`

## Push Notifications

Apps can send push via `commons.push_client`:
```python
from commons.push_client import send_push
await send_push(title="Alert", body="Something happened", url="/app/my-app/")
```

## Data

```
~/.local/share/privateapp/
├── privateapp.db       # Settings, preferences, push subscriptions
├── vapid_private.pem   # VAPID signing key
└── vapid_public.txt    # VAPID public key
```

## Key APIs

- `GET /api/apps` — list installed apps
- `GET /api/settings/preferences` — get preferences (timezone, language, app_order)
- `POST /api/settings/preferences` — save preferences
- `POST /api/push/send` — send push notification
- `GET /api/push/test` — test push
