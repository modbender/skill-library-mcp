---
name: jellyfin-control
description: Control Jellyfin media server and TV. Search content, resume playback, manage sessions, control TV power and apps. Supports Home Assistant and direct WebOS backends. One command to turn on TV, launch Jellyfin, and play content.
metadata: {"version": "1.3.0", "author": "Titunito", "openclaw": {"emoji": "🎬", "requires": {"env": ["JF_URL", "JF_API_KEY"]}, "optionalEnv": ["JF_USER", "JF_PASS", "JF_USER_ID", "TV_BACKEND", "TV_PLATFORM", "HA_URL", "HA_TOKEN", "HA_TV_ENTITY", "TV_IP", "TV_MAC", "TV_CLIENT_KEY", "ADB_DEVICE", "TV_JELLYFIN_APP", "TV_BOOT_DELAY", "TV_APP_DELAY"], "tags": ["media", "streaming", "tv", "smart-home", "jellyfin", "webos", "androidtv", "home-assistant"]}}
---

# Jellyfin Control

A robust skill to control Jellyfin playback and TV power via CLI.

## Features

- **🎯 One-Command Play:** `tv play "Breaking Bad"` — turns on TV, launches Jellyfin, finds the next episode, and plays it.
- **Smart Resume:** Automatically finds the next unplayed episode for series.
- **Resume Position:** Resumes Movies/Episodes exactly where left off (with `Seek` fallback for LG WebOS/Tizen).
- **Device Discovery:** Auto-detects controllable sessions (TVs, Phones, Web).
- **Remote Control:** Full playback control (play, pause, stop, next, prev, volume, mute).
- **TV Power & Apps:** Turn TV on/off, launch apps — works with or without Home Assistant.
- **Two TV Backends:** Home Assistant integration or direct WebOS (LG TVs, no HA needed).
- **Android TV Support:** Direct ADB backend for Chromecast w/ Google TV, Nvidia Shield, Fire TV, Mi Box — no HA needed.
- **Three connection modes:** Home Assistant (any TV), direct WebOS (LG), direct ADB (Android TV/Fire TV).

## Quick Start

### Minimal setup (Jellyfin only, no TV control)

```json
{
  "skills": {
    "entries": {
      "jellyfin-control": {
        "env": {
          "JF_URL": "http://YOUR_IP:8096",
          "JF_API_KEY": "your-api-key-here",
          "JF_USER": "your-username"
        }
      }
    }
  }
}
```

### With Home Assistant (recommended for TV control)

```json
{
  "skills": {
    "entries": {
      "jellyfin-control": {
        "env": {
          "JF_URL": "http://192.168.1.50:8096",
          "JF_API_KEY": "your-jellyfin-api-key",
          "JF_USER": "victor",
          "HA_URL": "http://192.168.1.138:8123",
          "HA_TOKEN": "your-ha-long-lived-token",
          "HA_TV_ENTITY": "media_player.lg_webos_tv_oled48c34la",
          "TV_MAC": "AA:BB:CC:DD:EE:FF"
        }
      }
    }
  }
}
```

### Direct WebOS (LG TV, no Home Assistant needed)

```json
{
  "skills": {
    "entries": {
      "jellyfin-control": {
        "env": {
          "JF_URL": "http://192.168.1.50:8096",
          "JF_API_KEY": "your-jellyfin-api-key",
          "JF_USER": "victor",
          "TV_IP": "192.168.1.100",
          "TV_MAC": "AA:BB:CC:DD:EE:FF"
        }
      }
    }
  }
}
```

> **First time with WebOS direct:** The TV will show a pairing prompt. Accept it and save the `TV_CLIENT_KEY` the skill prints — add it to your env to skip the prompt next time.

### Direct ADB (Android TV / Fire TV / Chromecast with Google TV, no HA needed)

```json
{
  "skills": {
    "entries": {
      "jellyfin-control": {
        "env": {
          "JF_URL": "http://192.168.1.50:8096",
          "JF_API_KEY": "your-jellyfin-api-key",
          "JF_USER": "victor",
          "ADB_DEVICE": "192.168.1.100:5555",
          "TV_MAC": "AA:BB:CC:DD:EE:FF"
        }
      }
    }
  }
}
```

> **First time with ADB:** Enable Developer Options on your TV (Settings → About → tap Build Number 7 times), then enable Network/USB debugging. First connection will show "Allow debugging?" on the TV — accept it. Requires `adb` installed on the OpenClaw host (`sudo apt install adb`).

## Environment Variables

### Jellyfin (required)

| Variable      | Required | Description                                                       |
| ------------- | -------- | ----------------------------------------------------------------- |
| `JF_URL`      | **Yes**  | Base URL of your Jellyfin server, e.g. `http://192.168.1.50:8096` |
| `JF_API_KEY`  | **Yes**  | API key from Jellyfin Dashboard → Advanced → API Keys             |
| `JF_USER`     | No       | Username — used to resolve user ID for user-specific endpoints    |
| `JF_USER_ID`  | No       | User ID directly — avoids needing to call `/Users`                |
| `JF_PASS`     | No       | Password — only if authenticating by user session                 |

### TV Control (optional — choose one backend)

| Variable           | Backend   | Description                                                           |
| ------------------ | --------- | --------------------------------------------------------------------- |
| `TV_BACKEND`       | All       | Force backend: `homeassistant`, `webos`, `androidtv`, or `auto`       |
| `TV_PLATFORM`      | HA        | Force platform: `webos` or `androidtv` (auto-detected from entity)    |
| `HA_URL`           | HA        | Home Assistant URL, e.g. `http://192.168.1.138:8123`                  |
| `HA_TOKEN`         | HA        | HA long-lived access token (Profile → Long-Lived Access Tokens)       |
| `HA_TV_ENTITY`     | HA        | Entity ID of your TV, e.g. `media_player.lg_webos_tv_oled48c34la`     |
| `TV_IP`            | WebOS     | LG TV IP address for direct WebOS SSAP connection                     |
| `TV_CLIENT_KEY`    | WebOS     | Pairing key (printed on first connection — save it!)                  |
| `ADB_DEVICE`       | AndroidTV | TV address for ADB, e.g. `192.168.1.100:5555`                        |
| `TV_MAC`           | All       | TV MAC address for Wake-on-LAN (needed to turn on TV)                 |
| `TV_JELLYFIN_APP`  | All       | Override Jellyfin app ID (auto: `org.jellyfin.webos` / `org.jellyfin.androidtv`) |
| `TV_BOOT_DELAY`    | All       | Seconds to wait after TV wake (default: 10)                           |
| `TV_APP_DELAY`     | All       | Seconds to wait after launching Jellyfin (default: 8)                 |

**Auto-detection:** If `TV_BACKEND` is `auto` (default):
1. `HA_URL` + `HA_TOKEN` + `HA_TV_ENTITY` set → Home Assistant backend
2. `ADB_DEVICE` set → direct ADB (Android TV)
3. `TV_IP` set → direct WebOS (LG)
4. Nothing set → TV commands disabled, Jellyfin-only mode

## Usage

### 🎯 One-Command Play (the magic)

Turn on TV → launch Jellyfin → find next episode → play it. All in one command:

```bash
node skills/jellyfin-control/cli.js tv play "Breaking Bad"
node skills/jellyfin-control/cli.js tv play "The Matrix"
```

The skill validates the content exists BEFORE turning on the TV (fail fast).

### Resume / Play Smart

If TV and Jellyfin are already running:

```bash
node skills/jellyfin-control/cli.js resume "Breaking Bad"
node skills/jellyfin-control/cli.js resume "Matrix" --device "Chromecast"
```

### TV Control

```bash
node skills/jellyfin-control/cli.js tv on           # Turn on (Wake-on-LAN)
node skills/jellyfin-control/cli.js tv off          # Turn off
node skills/jellyfin-control/cli.js tv launch       # Launch Jellyfin app
node skills/jellyfin-control/cli.js tv launch com.webos.app.hdmi1  # Launch specific app
node skills/jellyfin-control/cli.js tv apps         # List installed apps
```

### Remote Control

```bash
node skills/jellyfin-control/cli.js control pause
node skills/jellyfin-control/cli.js control play
node skills/jellyfin-control/cli.js control next
node skills/jellyfin-control/cli.js control vol 50
```

### Search Content

```bash
node skills/jellyfin-control/cli.js search "Star Wars"
```

### Library Stats & Scan

```bash
node skills/jellyfin-control/cli.js stats
node skills/jellyfin-control/cli.js scan            # requires admin API key
```

### User History (requires admin API key)

```bash
node skills/jellyfin-control/cli.js history
node skills/jellyfin-control/cli.js history jorge --days 7
```

## Choosing a TV Backend

| Feature             | Home Assistant        | Direct WebOS            | Direct ADB (Android TV)     | No Backend     |
| ------------------- | --------------------- | ----------------------- | --------------------------- | -------------- |
| TV brands           | Any (via HA)          | LG only                 | Android TV, Fire TV, CCwGTV | —              |
| Turn on (WoL)       | ✅                    | ✅                      | ✅ (WoL or ADB wakeup)     | —              |
| Turn off            | ✅                    | ✅                      | ✅                          | —              |
| Launch apps         | ✅                    | ✅                      | ✅                          | —              |
| List apps           | ✅ (via HA logs)      | ✅ (direct output)      | ✅ (direct output)          | —              |
| Extra dependency    | None                  | `npm install ws`        | `apt install adb`           | None           |
| Setup complexity    | Medium (need HA)      | Low (TV IP + MAC)       | Low (enable ADB on TV)      | None           |
| Jellyfin playback   | ✅                    | ✅                      | ✅                          | ✅             |

**Recommendation:**
- Already have Home Assistant? → Use HA backend (most versatile, any TV brand)
- LG WebOS TV, no HA? → Use direct WebOS backend
- Android TV / Fire TV / Chromecast with Google TV, no HA? → Use direct ADB backend
- No smart TV control needed? → Skip TV config, `resume` works if Jellyfin app is already open

## Security Notes

- **API keys only in `openclaw.json` env** — never in workspace files, `.env` files, or markdown docs.
- **HA tokens** are long-lived and powerful. Create a dedicated HA user with limited permissions if possible.
- **TV_CLIENT_KEY** (WebOS) is sensitive — it allows full control of your TV. Treat it like a password.
- **ADB access** grants full control of your Android TV. Ensure your network is secured — anyone on the same network could connect via ADB if debugging is enabled.
- **Admin operations** (`history`, `scan`) require an admin-level Jellyfin API key and will fail gracefully with 403 if permissions are insufficient.

## Architecture

- `lib/jellyfin.js` — Jellyfin REST API (auth, search, sessions, playback control)
- `lib/tv.js` — TV control abstraction (HA backend, WebOS backend, Wake-on-LAN)
- `cli.js` — User-friendly CLI with all commands

## Workflow: Agent says "Play Star Trek on TV"

```
Agent → cli.js tv play "Star Trek"
         │
         ├── 1. Search Jellyfin for "Star Trek" (fail fast)
         ├── 2. Find next unplayed episode
         ├── 3. Wake-on-LAN → TV turns on
         ├── 4. Wait 10s for boot
         ├── 5. Launch Jellyfin app (HA or WebOS)
         ├── 6. Wait 8s for session registration
         ├── 7. Find Jellyfin session (retry 3x)
         └── 8. Play episode on session
```
