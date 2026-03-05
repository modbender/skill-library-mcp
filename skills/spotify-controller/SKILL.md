---
name: spotify-controller
description: Control Spotify playback and devices from an AI agent using spotify.py and the official Spotify Web API. Use when users ask to check current track, play/pause, next/prev, set volume, search tracks, play first search result, list devices, switch active device, or play a specific Spotify URL. Works on headless VPS and Docker setups.
homepage: https://developer.spotify.com
metadata: {"clawdbot":{"emoji":"🎵","requires":{"env":["SPOTIFY_CLIENT_ID","SPOTIFY_CLIENT_SECRET","SPOTIFY_REFRESH_TOKEN"],"bins":["python3"]},"primaryEnv":"SPOTIFY_CLIENT_ID"}}
---

# Spotify Controller Skill

Control Spotify playback from your AI agent using the official Spotify Web API.

This works across setups (local machine, Docker, VPS, and hybrid environments). It is especially useful for fixing Spotify control pain in headless VPS deployments. The server does **not** need a browser or a local Spotify client.

---

## What this skill provides

- A CLI workflow around `spotify.py`
- Playback control (`play`, `pause`, `next`, `prev`)
- Track lookup (`search`) and quick play (`playsearch`)
- Direct URI playback (`playtrack spotify:track:...`)
- Device management (`devices`, `setdevice`)
- Volume control (`volume 0-100`, where supported)

---

## Requirements

- Python 3 available in runtime/container
- `requests` package installed
- Spotify Premium account
- Spotify Developer app credentials
- Environment variables:
  - `SPOTIFY_CLIENT_ID`
  - `SPOTIFY_CLIENT_SECRET`
  - `SPOTIFY_REFRESH_TOKEN`

Install dependency:

```bash
uv pip install requests --system
```

(Alternative: `pip install requests`)

If you build OpenClaw in Docker, add this to your `Dockerfile` when `requests` is not already present:

```dockerfile
RUN uv pip install requests --system
```

---

## Setup (Step-by-step)

### 1) Create a Spotify Developer App

1. Go to: https://developer.spotify.com/dashboard
2. Click **Create App**
3. Enter any app name/description
4. Add Redirect URI:
   - `http://127.0.0.1:8888/callback`
5. Enable **Web API** access
6. Save and copy:
   - **Client ID**
   - **Client Secret**

### 2) Get a refresh token (one-time, on local machine)

Open this URL in your browser (replace `YOUR_CLIENT_ID`):

```text
https://accounts.spotify.com/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://127.0.0.1:8888/callback&scope=user-modify-playback-state%20user-read-playback-state%20user-read-currently-playing
```

Approve access, then copy the `code` value from the redirected URL.

Exchange code for tokens:

```bash
curl -s -X POST "https://accounts.spotify.com/api/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code&code=YOUR_CODE&redirect_uri=http://127.0.0.1:8888/callback&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET"
```

From response JSON, copy `refresh_token`.

> `refresh_token` is typically long-lived, but can be invalidated if app access is revoked, app settings change, or credentials rotate.

### 3) Add credentials to `.env`

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REFRESH_TOKEN=your_refresh_token
```

### 4) Pass env vars to Docker compose service

In `docker-compose.yml` service `environment:` section:

```yaml
- SPOTIFY_CLIENT_ID=${SPOTIFY_CLIENT_ID}
- SPOTIFY_CLIENT_SECRET=${SPOTIFY_CLIENT_SECRET}
- SPOTIFY_REFRESH_TOKEN=${SPOTIFY_REFRESH_TOKEN}
```

### 5) Restart service/container

```bash
docker compose down
docker compose up -d openclaw-gateway
```

```bash
chown <runtime_user>:<runtime_group> /path/to/workspace/spotify.py
chmod 664 /path/to/workspace/spotify.py
```

---

## Usage

Run commands from workspace:

```bash
python3 spotify.py <command>
```

| Command                                          | Description |
|--------------------------------------------------|---|
| `python3 spotify.py status`                      | Show current playback state and track |
| `python3 spotify.py play`                        | Resume playback |
| `python3 spotify.py pause`                       | Pause playback |
| `python3 spotify.py next`                        | Skip to next track |
| `python3 spotify.py prev`                        | Go to previous track |
| `python3 spotify.py volume 80`                   | Set volume (0–100) where supported |
| `python3 spotify.py search track`                | Search tracks (top results) |
| `python3 spotify.py playsearch "track"`          | Search and play first result |
| `python3 spotify.py playtrack spotify:track:URI` | Play specific track URI |
| `python3 spotify.py devices`                     | List available Spotify devices |
| `python3 spotify.py setdevice "BEDROOM-SPEAKER"` | Set active device by name or id |

---

## VPS / Headless behavior notes

- Headless server control works because playback is executed on Spotify Connect devices (phone/desktop/web), not the server audio output.
- You still need at least one **active Spotify device session**.

If you see `NO_ACTIVE_DEVICE`:
1. Open Spotify on target device
2. Start any track manually once
3. Run `python3 spotify.py devices`
4. Retry command

---

## Known Spotify API limitations (expected)

- Some devices/content contexts may return `403 Restriction violated` for `play`, `prev`, or other controls.
- Some devices may reject remote volume changes (`VOLUME_CONTROL_DISALLOW`).
- Device handoff can lag; immediate `status` after transfer may briefly show stale state.

These are Spotify-side constraints, not necessarily script bugs.

---

## Operational guidance for automations

- Treat non-zero exit codes as command failures.
- Validate environment vars at startup.
- Log command + status code for troubleshooting.
- Retry once for transient network errors.
- Don’t hardcode real credentials in files.

---

## Security notes

- Never commit `.env` with live secrets.
- Rotate app credentials if leaked.
- Use least-access scopes required for your workflow.
- The script only communicates with accounts.spotify.com and api.spotify.com

---

## Quick troubleshooting checklist

1. `python3 spotify.py devices` shows your target device?
2. Device is active in Spotify app?
3. Env vars loaded inside container/runtime?
4. Premium account confirmed?
5. Refresh token still valid?
6. Any Spotify 403 restriction reason in response?

---

## Claim accuracy

- Uses official Spotify Web API ✅
- Works on headless VPS ✅
- Practical for personal usage ✅
- Subject to normal Spotify API behavior/limits ✅
