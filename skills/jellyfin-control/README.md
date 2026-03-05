# 🎬 Jellyfin Control for OpenClaw

Control your Jellyfin media server and TV with natural language through your AI assistant.

> *"Hey Francis, play Breaking Bad on the TV"*
> → TV turns on → Jellyfin launches → Next episode plays. Automatically.

## What's New in v1.2

- **📺 TV Control** — Turn on/off your TV, launch apps, all from the CLI
- **🎯 One-command play** — `tv play "Breaking Bad"` does everything: wake TV → launch Jellyfin → find episode → play
- **Two backends** — Home Assistant (any TV brand) or direct WebOS (LG TVs, no HA needed)
- **Wake-on-LAN** — Built-in, zero dependencies
- **Fail-fast** — Content is validated before the TV turns on

## Install

```bash
# In your OpenClaw skills directory
cd skills/jellyfin-control
npm install

# If using direct WebOS backend (LG TV without HA):
npm install ws

# If using direct ADB backend (Android TV / Fire TV):
sudo apt install adb    # Debian/Ubuntu
# or: brew install android-platform-tools   # macOS
```

## Setup

### 1. Jellyfin API Key

1. Open Jellyfin Dashboard → Advanced → API Keys
2. Create a new key (name it "OpenClaw")
3. Copy the key

### 2. Configure openclaw.json

**Minimal (Jellyfin only):**
```json
{
  "skills": {
    "entries": {
      "jellyfin-control": {
        "env": {
          "JF_URL": "http://YOUR_JELLYFIN_IP:8096",
          "JF_API_KEY": "your-api-key",
          "JF_USER": "your-username"
        }
      }
    }
  }
}
```

**With Home Assistant:**
```json
{
  "env": {
    "JF_URL": "http://192.168.1.50:8096",
    "JF_API_KEY": "your-jellyfin-api-key",
    "JF_USER": "victor",
    "HA_URL": "http://192.168.1.138:8123",
    "HA_TOKEN": "your-ha-long-lived-access-token",
    "HA_TV_ENTITY": "media_player.lg_webos_tv_oled48c34la",
    "TV_MAC": "AA:BB:CC:DD:EE:FF"
  }
}
```

**Direct WebOS (LG TV, no HA):**
```json
{
  "env": {
    "JF_URL": "http://192.168.1.50:8096",
    "JF_API_KEY": "your-jellyfin-api-key",
    "JF_USER": "victor",
    "TV_IP": "192.168.1.100",
    "TV_MAC": "AA:BB:CC:DD:EE:FF"
  }
}
```

**Direct ADB (Android TV / Fire TV / Chromecast with Google TV, no HA):**
```json
{
  "env": {
    "JF_URL": "http://192.168.1.50:8096",
    "JF_API_KEY": "your-jellyfin-api-key",
    "JF_USER": "victor",
    "ADB_DEVICE": "192.168.1.100:5555",
    "TV_MAC": "AA:BB:CC:DD:EE:FF"
  }
}
```

### 3. Finding your TV MAC address

- **Home Assistant:** Settings → Devices → Your TV → look for MAC in network info
- **Router admin:** Check DHCP leases for your TV's IP
- **TV Settings:** Network → WiFi/Ethernet → Advanced → MAC Address

### 4. Enabling ADB on Android TV (direct ADB backend only)

1. Go to **Settings → About** on your Android TV
2. Tap **Build Number** 7 times to enable Developer Options
3. Go back to **Settings → Developer Options**
4. Enable **Network debugging** (or USB debugging)
5. Note the IP address shown (or find it in Settings → Network)
6. Set `ADB_DEVICE` to `YOUR_TV_IP:5555`
7. First time you connect, the TV will show "Allow USB debugging?" — accept it

### 5. First-time WebOS pairing (direct WebOS backend only)

```bash
# Make sure TV is ON, then run:
node skills/jellyfin-control/cli.js tv apps

# TV will show "Allow connection?" prompt — accept it
# The skill prints a TV_CLIENT_KEY — add it to your env config
```

## Usage Examples

```bash
# The dream command — everything automated
node cli.js tv play "Star Trek"

# TV is already on with Jellyfin open
node cli.js resume "Breaking Bad"
node cli.js resume "Matrix" --device "Chromecast"

# TV control
node cli.js tv on
node cli.js tv off
node cli.js tv launch                    # Launch Jellyfin
node cli.js tv launch com.webos.app.netflix  # Launch Netflix
node cli.js tv apps                      # List installed apps

# Playback control
node cli.js control pause
node cli.js control play
node cli.js control vol 40

# Library
node cli.js search "Star Wars"
node cli.js stats
node cli.js scan
```

## How it works

```
"Play Star Trek on the TV"
        │
        ▼
  ┌─ Search Jellyfin ─── Found: Star Trek: SNW S2E05
  │
  ├─ Wake-on-LAN ──────── TV powers on
  │   └─ wait 10s
  │
  ├─ Launch App ────────── Jellyfin starts on TV
  │   ├─ (HA/WebOS)    POST webostv/command → system.launcher/launch
  │   ├─ (HA/Android)  POST androidtv/adb_command → monkey launch
  │   ├─ (WebOS direct) SSAP ws://TV:3000 → system.launcher/launch
  │   └─ (ADB direct)  adb shell monkey -p org.jellyfin.androidtv
  │   └─ wait 8s
  │
  └─ Play on Session ──── Episode starts, resumes where you left off
      └─ POST /Sessions/{id}/Playing
```

## Security

- Store all credentials in `openclaw.json` env config only
- Never commit API keys, tokens, or passwords to files
- Create a dedicated HA user with limited permissions for the token
- Admin commands (`scan`, `history`) fail gracefully if permissions are insufficient
- `TV_CLIENT_KEY` grants full TV control — treat it as sensitive

## Changelog

### v1.3.0
- Added Android TV / Fire TV / Chromecast with Google TV support via direct ADB backend
- Home Assistant backend now auto-detects WebOS vs Android TV entities (`TV_PLATFORM`)
- Auto-detection of Jellyfin app ID per platform (`org.jellyfin.webos` vs `org.jellyfin.androidtv`)
- Three connection modes: Home Assistant (any TV), direct WebOS (LG), direct ADB (Android TV)
- ADB backend uses system `adb` — no npm packages needed

### v1.2.0
- Added TV control module with Home Assistant and direct WebOS backends
- Added `tv play` composite command for full automation (wake → launch → play)
- Added `tv on`, `tv off`, `tv launch`, `tv apps` commands
- Built-in Wake-on-LAN (zero dependencies)
- Session detection retry (3 attempts) for `tv play`
- Content validation before TV startup (fail fast)
- `ws` package as optional dependency (only for WebOS direct)

### v1.1.0
- Security fixes: all env vars declared in SKILL.md metadata
- Removed hardcoded credentials and SECRETOS.md references
- `/Users/Me` preferred over `/Users` (no admin needed)
- Admin requirement warnings for `history` and `scan`

### v1.0.0
- Initial release: search, resume, remote control, stats, scan, history
