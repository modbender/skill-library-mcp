# Approvals UI

A web dashboard for managing OpenClaw device pairings, channel approvals, and a live terminal — all from your browser.

## Install

Place this folder at:

```
~/.openclaw/workspace/projects/p1
```

Your file structure should look like:

```
~/.openclaw/workspace/projects/p1/
├── SKILL.md
├── server.py
└── templates/
    ├── channel_approvals.html
    ├── dashboard.html
    ├── device_pairings.html
    ├── index.html
    ├── login.html
    └── terminal.html
```

## Requirements

Install Python dependencies:

```bash
pip install flask flask-socketio
```

## ⚠️ Important — Change These Before Running

This skill ships with **placeholder credentials** that you **must** change before using:

Open `server.py` and update the following values near the top of the file:

| What | Variable | Default | Action |
|---|---|---|---|
| Dashboard login username | `ADMIN_USERNAME` | `Drinnas` | Change to your own username |
| Dashboard login password | `ADMIN_PASSWORD` | `admin` | Change to a strong password |
| API auth password | `AUTH_PASSWORD` / env `SERVER_AUTH_PASSWORD` | `Bb7766!server` | Change to a strong password or set the env var |
| Flask secret key | env `FLASK_SECRET_KEY` | dev placeholder | Set to a random string in your environment |

**Example:**

```bash
export FLASK_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
export SERVER_AUTH_PASSWORD="your-strong-api-password-here"
```

> **Do not run with the defaults.** Anyone who knows the defaults can log in and access your terminal and gateway token.

### Credential Explanation

There are **two separate auth layers**:

1. **Dashboard login** (`ADMIN_USERNAME` / `ADMIN_PASSWORD`) — protects the web UI pages (dashboard, device pairings, channel approvals, terminal).
2. **API password** (`AUTH_PASSWORD` / env `SERVER_AUTH_PASSWORD`) — protects the backend API endpoints (`/pair`, `/sync`, `/approve`) used for programmatic access. These endpoints are not exposed in the web UI but exist for automation/scripting.

Both should be set to strong, unique values.

## Usage

Start the server:

```bash
cd ~/.openclaw/workspace/projects/p1
python3 server.py
```

Then open **http://127.0.0.1:9100** in your browser.

## Features

- **Dashboard** — Landing page with quick navigation to all sections.
- **Device Pairings** — View pending and paired browser/device connections. Approve or reject pairing requests. Copy your gateway token to clipboard.
- **Channel Approvals** — Review and approve pending channel pairing requests (Telegram, Discord, WhatsApp, etc). Real-time updates via Socket.IO.
- **Terminal** — Full interactive terminal session in the browser using xterm.js.

## How It Works

- Reads device pairings directly from `~/.openclaw/devices/pending.json` and `~/.openclaw/devices/paired.json`.
- Reads channel pairing requests from `~/.openclaw/credentials/*-pairing.json`.
- Reads the gateway token from `~/.openclaw/openclaw.json` → `gateway.auth.token`.
- Approve/reject actions use the `openclaw devices approve` and `openclaw devices reject` CLI commands.
- No external database needed — everything reads from OpenClaw's own state files.

## Security Notes

- **Localhost only** — The server binds to `127.0.0.1` by default. Do not change this to `0.0.0.0` unless you put it behind a reverse proxy with TLS and strong auth.
- **Terminal access** — The terminal feature gives full shell access to your machine. If you don't need it, you can remove the `/terminal` route and `terminal.html` template.
- **Sensitive files** — The app reads your `openclaw.json` (gateway token), device pairing files, and credential pairing files. Anyone who can access the web UI can see this data.
- **API endpoints** — `POST /pair`, `POST /sync`, and `POST /approve` accept JSON with a password field. These are protected by `AUTH_PASSWORD` and are intended for scripting/automation, not the web UI.

## Configuration

| Setting | Location | Default |
|---|---|---|
| Server port | `server.py` bottom | `9100` |
| Dashboard login | `server.py` `ADMIN_USERNAME` / `ADMIN_PASSWORD` | `Drinnas` / `admin` |
| API password | `server.py` `AUTH_PASSWORD` / env `SERVER_AUTH_PASSWORD` | `Bb7766!server` |
| Flask secret key | env `FLASK_SECRET_KEY` | dev placeholder |
| OpenClaw state dir | env `OPENCLAW_STATE_DIR` | `~/.openclaw` |

## Tags

`ui` `dashboard` `pairings` `approvals` `terminal` `web`
