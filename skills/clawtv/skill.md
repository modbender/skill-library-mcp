---
name: clawtv
description: AI-powered Apple TV remote control with vision — navigate any app autonomously.
homepage: https://github.com/akivasolutions/clawtv
metadata:
  {
    "openclaw":
      {
        "emoji": "📺",
        "requires": { "bins": ["python3"], "env": ["ANTHROPIC_API_KEY"] },
        "primaryEnv": "ANTHROPIC_API_KEY",
        "configPaths": ["~/.clawtv/config.json"],
      },
  }
---

# ClawTV

AI-powered Apple TV remote that can see the screen and navigate any app autonomously using vision + remote control.

## When to use (trigger phrases)

Use this skill immediately when the user asks:

- "play [movie/show] on Apple TV"
- "search for [content] on [Netflix/Plex/YouTube/etc]"
- "open [app] on the TV"
- "turn on subtitles" / "go to TV settings"
- "what's playing on Apple TV?"
- "take a screenshot of the TV"
- Any Apple TV navigation or control task

## Quick start

```bash
# AI agent mode — tell it what you want in plain English
python3 ~/Developer/clawtv/clawtv.py do "open Plex and play Fight Club"
python3 ~/Developer/clawtv/clawtv.py do "search for Stranger Things on Netflix"
python3 ~/Developer/clawtv/clawtv.py do "go to settings and turn on subtitles"

# Direct Plex control (instant, no vision loop)
python3 ~/Developer/clawtv/clawtv.py plex play "Fight Club"
python3 ~/Developer/clawtv/clawtv.py plex play "Westworld" -s 2 -e 6

# Manual remote commands
python3 ~/Developer/clawtv/clawtv.py cmd up down select
python3 ~/Developer/clawtv/clawtv.py type "breaking bad"
python3 ~/Developer/clawtv/clawtv.py launch com.plexapp.plex

# Screenshot
python3 ~/Developer/clawtv/clawtv.py screenshot

# Status
python3 ~/Developer/clawtv/clawtv.py playing
```

## Required Credentials

### ANTHROPIC_API_KEY (Required for AI/Vision Mode)

The `do` command (AI agent mode) requires an Anthropic API key to access Claude's vision API for screenshot analysis and navigation decisions.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Or add to your shell profile (~/.zshrc, ~/.bashrc).

**Note:** This is only required for the `do` command. Manual commands (`cmd`, `type`, `launch`) and `plex` direct control do not use the API.

### Plex Credentials (Optional)

For instant Plex playback without the vision loop, add these to `~/.clawtv/config.json`:

```json
{
  "plex_url": "http://192.168.1.100:32400",
  "plex_token": "your-plex-token",
  "plex_client": "Living Room"
}
```

- **plex_url**: Your Plex server address (local or remote)
- **plex_token**: Authentication token from your Plex account
- **plex_client**: Name of the Plex client on your Apple TV

Get your Plex token: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/

## Privacy & Data

### What Data is Collected and Sent

**Screenshots:**
- ClawTV captures screenshots of your Apple TV screen using QuickTime Player or Xcode
- Screenshots are saved locally to `~/.clawtv/screenshots/` with timestamps
- When using the `do` command (AI agent mode), screenshots are sent to Anthropic's Claude API for vision analysis
- Screenshots may contain sensitive on-screen content including:
  - Content you're watching (movie/show titles, thumbnails)
  - Search queries
  - Account information visible in app UIs
  - Any other content displayed on your TV screen

**Anthropic API:**
- Only the `do` command sends data to Anthropic
- Data sent: screenshots (JPEG compressed) + your goal/instruction + conversation history
- Anthropic's data retention policy: https://support.anthropic.com/en/articles/7996885-how-long-do-you-store-personal-data
- Manual commands (`cmd`, `type`, `launch`) and Plex direct control do NOT send any data to external APIs

### Credential Storage

**Apple TV Pairing Credentials:**
- Stored unencrypted in `~/.clawtv/config.json` in your home directory
- Contains device identifiers and pairing tokens for remote control
- File permissions: readable only by your user account (standard Unix permissions)

**Plex Tokens (if configured):**
- Stored unencrypted in the same `~/.clawtv/config.json` file
- Grants full access to your Plex server and library
- Can be used to play, pause, search, and control any Plex client

**Anthropic API Key:**
- Stored in environment variables or your shell profile
- Grants access to your Anthropic account and incurs API usage charges

### Recommendations

1. **Use a budget-limited API key**: Set spending limits on your Anthropic account to prevent unexpected charges
2. **Review config file permissions**: Ensure `~/.clawtv/config.json` is only readable by your user
3. **Be aware of screenshot content**: Screenshots are sent to Anthropic's API and may contain sensitive information
4. **Monitor API usage**: The `do` command can make multiple API calls per task (5-20 steps typical)
5. **Use manual commands when possible**: `cmd`, `type`, and `launch` have zero API cost and send no data externally

## Security Considerations

### Plaintext Credential Storage

- **Apple TV pairing credentials** and **Plex tokens** are stored in plaintext in `~/.clawtv/config.json`
- The file is in your user home directory (`~/.clawtv/`) with standard Unix file permissions
- Any process running as your user can read these credentials
- If your Mac is compromised, these credentials are accessible
- Consider this when deciding whether to configure Plex integration

### Screenshot Privacy

- **Screenshots may contain sensitive content** visible on your TV screen
- Screenshots are saved locally to `~/.clawtv/screenshots/` and persist until manually deleted
- When using AI agent mode (`do`), screenshots are transmitted to Anthropic's servers
- DRM content (Netflix, Disney+, etc.) cannot be captured via QuickTime, but works with Xcode method
- Review screenshot history periodically and delete sensitive captures

### API Cost and Autonomous Behavior

- **The `do` command runs in a loop** (up to 20 steps) and makes Claude API calls automatically
- Each step = 1 API call with screenshot (~$0.01-0.02 per step depending on model)
- A stuck or confused agent could consume all 20 steps before giving up
- **Cost implications**: Complex tasks can cost $0.10-0.20; monitor your Anthropic usage dashboard
- **Recommendation**: Set spending limits on your Anthropic account

### Manual Commands are API-Free

- **`cmd`**, **`type`**, **`launch`**, and **`plex`** commands do not use the Claude API
- No screenshots are sent externally when using these commands
- Zero cost, zero external data transmission
- Use these for privacy-sensitive operations

### Network Exposure

- ClawTV communicates with your Apple TV over your local network using the Companion protocol
- Plex integration (if configured) communicates with your Plex server (local or remote)
- No external network access except:
  - Anthropic API (when using `do` command)
  - Plex server (if remote URL configured)

## Setup (first-time only)

### 1. Install dependencies

```bash
cd ~/Developer/clawtv
pip install -r requirements.txt
```

For QuickTime screenshot method (recommended):
```bash
pip install pyobjc-framework-Quartz
```

### 2. Pair with Apple TV (remote control)

```bash
python3 ~/Developer/clawtv/clawtv.py scan    # Find your Apple TV on network
python3 ~/Developer/clawtv/clawtv.py pair    # Enter 4-digit PIN shown on TV
```

Pairing credentials are saved to `~/.clawtv/config.json`.

### 3. Set up screenshots

**QuickTime (recommended):**
```bash
python3 ~/Developer/clawtv/clawtv.py screenshot --method quicktime
```

- QuickTime Player opens and selects your Apple TV as video source
- Accept the AirPlay pairing on your TV (one-time PIN)
- Subsequent runs reuse the existing mirror instantly (~0.6s per screenshot)

**Xcode (fallback for DRM apps):**
1. On Apple TV: **Settings > Privacy & Security** → enable "Share with App Devs"
2. Then **Settings > Remotes and Devices > Remote App and Devices**
3. On Mac: Open Xcode, press **Cmd+Shift+2** (Devices)
4. Click your Apple TV in sidebar, enter pairing code
5. Keep Xcode Devices window open while using ClawTV

### 4. Set API key

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Or add to your shell profile (~/.zshrc, ~/.bashrc).

### 5. Optional: Plex direct control setup

For instant Plex playback without vision loop, add to `~/.clawtv/config.json`:

```json
{
  "plex_url": "http://192.168.1.100:32400",
  "plex_token": "your-plex-token",
  "plex_client": "Living Room"
}
```

Get your Plex token: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/

## Commands

### AI Agent Mode (`do`)

Tell ClawTV what you want and it figures out the rest using vision + reasoning.

```bash
python3 ~/Developer/clawtv/clawtv.py do "<goal>"
```

**How it works:**
1. Takes screenshot of Apple TV
2. Sends to Claude vision API to analyze UI
3. Decides what to do (navigate, select, type, launch app)
4. Sends remote commands
5. Takes another screenshot to verify
6. Repeats until goal is accomplished (max 20 steps)

**Examples:**
```bash
python3 ~/Developer/clawtv/clawtv.py do "open Plex and play Fight Club"
python3 ~/Developer/clawtv/clawtv.py do "search for Stranger Things on Netflix"
python3 ~/Developer/clawtv/clawtv.py do "open YouTube and find lo-fi beats"
python3 ~/Developer/clawtv/clawtv.py do "go to settings and turn on subtitles"
python3 ~/Developer/clawtv/clawtv.py do "open Spotify and play my liked songs"
```

**Token optimizations (automatic):**
- Plex goals bypass vision entirely via direct API (instant, pennies)
- Sliding window: only last 2 screenshots kept in context (~70% token reduction)
- Images compressed to JPEG 800px q50 (~40% fewer image tokens)
- System prompt cached via `cache_control` (90% savings on steps 2+)
- Haiku 4.5 for routine steps, auto-escalates to Sonnet 4.5 when stuck

**Playback pattern:** Navigate → start playback → verify playing → skip intro if visible → `disconnect` → report done

### Remote Commands (`cmd`)

Send direct remote control commands without AI.

```bash
python3 ~/Developer/clawtv/clawtv.py cmd <commands...>
```

**Available commands:**
`up`, `down`, `left`, `right`, `select`, `menu`, `home`, `play`, `pause`, `play_pause`, `next`, `previous`, `volume_up`, `volume_down`, `top_menu`

**Examples:**
```bash
python3 ~/Developer/clawtv/clawtv.py cmd up
python3 ~/Developer/clawtv/clawtv.py cmd down down right select
python3 ~/Developer/clawtv/clawtv.py cmd select sleep:1.5 down    # with timing
```

**Timing:** Insert `sleep:X` between commands to add delays (in seconds).

### Type Text (`type`)

Type text into a focused search/text field on the TV.

```bash
python3 ~/Developer/clawtv/clawtv.py type "<text>"
```

**Example:**
```bash
python3 ~/Developer/clawtv/clawtv.py type "breaking bad"
```

**Note:** The text field must already be focused. Use `cmd` to navigate to search first, or use `do` for full automation.

### Launch App (`launch`)

Launch an app by bundle ID.

```bash
python3 ~/Developer/clawtv/clawtv.py launch <bundle_id>
```

**Example:**
```bash
python3 ~/Developer/clawtv/clawtv.py launch com.plexapp.plex
```

**Common bundle IDs:**

| App | Bundle ID |
|-----|-----------|
| Plex | `com.plexapp.plex` |
| YouTube | `com.google.ios.youtube` |
| HBO Max | `com.wbd.stream` |
| Prime Video | `com.amazon.aiv.AIVApp` |
| Apple TV | `com.apple.TVWatchList` |
| Spotify | `com.spotify.client` |
| ESPN | `com.espn.ScoreCenter` |
| Twitch | `tv.twitch` |
| Pluto TV | `tv.pluto.ios` |
| NFL | `com.nfl.gamecenter` |
| Disney+ | `com.disney.disneyplus` |
| Hulu | `com.hulu.plus` |
| Netflix | `com.netflix.Netflix` |

Use `python3 ~/Developer/clawtv/clawtv.py apps` for the full list on your device.

### Plex Direct Control (`plex`)

Bypass the entire vision loop using Plex API directly. Searches your library and tells the Plex client on Apple TV to play. **Instant playback, zero vision cost.**

```bash
# Play a movie
python3 ~/Developer/clawtv/clawtv.py plex play "Fight Club"

# Play a specific episode
python3 ~/Developer/clawtv/clawtv.py plex play "Westworld" -s 2 -e 6

# Search your library
python3 ~/Developer/clawtv/clawtv.py plex search "matrix"

# List Plex clients
python3 ~/Developer/clawtv/clawtv.py plex clients

# List libraries
python3 ~/Developer/clawtv/clawtv.py plex libraries
```

**Requirements:**
- `plex_url`, `plex_token`, and `plex_client` in `~/.clawtv/config.json`
- Plex server running and accessible from Mac
- Plex client running on Apple TV

**Auto-detection:** The `do` command automatically detects Plex goals (e.g., "play Fight Club on Plex") and routes through this path without any vision API calls.

### Screenshot (`screenshot`)

Take a screenshot of the Apple TV and save to `~/.clawtv/screenshots/`.

```bash
python3 ~/Developer/clawtv/clawtv.py screenshot [--method auto|quicktime|lookout|xcode]
```

**Screenshot methods:**

| Method | Speed | DRM Apps | Requires |
|--------|-------|----------|----------|
| **QuickTime** (default) | ~0.6s | ❌ Kills mirror (DRM) | QuickTime Player, pyobjc-framework-Quartz |
| **Lookout** | ~0.1s | ❌ Only captures Lookout app | [Lookout tvOS app](https://github.com/akivasolutions/lookout-tvos) running on Apple TV |
| **Xcode** (legacy) | ~2.5s | ✅ Works with all apps | Xcode Devices window open |

**DRM apps (YouTube, Netflix, Disney+, HBO Max)** enforce HDCP and terminate the QuickTime AirPlay mirror entirely. Use Xcode method for these apps, or use Lookout for its own UI.

**Configuration:** Set default method in `~/.clawtv/config.json`:
```json
{
  "screenshot_method": "auto"
}
```

Values: `auto` (tries quicktime → lookout → xcode), `quicktime`, `lookout`, `xcode`

### Disconnect QuickTime (`disconnect`)

Close the QuickTime mirror and auto-resume playback on the TV.

```bash
python3 ~/Developer/clawtv/clawtv.py disconnect
```

**Why:** QuickTime mirroring shows a red recording border on the TV and routes audio to the Mac. After starting playback, always `disconnect` to remove the border and restore audio to the TV.

**Auto-resume:** Sends `play` command twice to ensure playback resumes.

### Status Commands

```bash
# What's currently playing
python3 ~/Developer/clawtv/clawtv.py playing

# Find Apple TVs on network
python3 ~/Developer/clawtv/clawtv.py scan

# List installed apps with bundle IDs
python3 ~/Developer/clawtv/clawtv.py apps
```

## Important Notes

### DRM Limitations

**DRM apps (YouTube, Netflix, Disney+, HBO Max) terminate the QuickTime AirPlay mirror entirely.** When this happens:

- QuickTime method shows a black screen
- ClawTV auto-detects the disconnection in `auto` mode
- Falls back to Xcode method automatically
- Or manually use: `--method xcode`

**Apps that work with QuickTime:** Plex (local media), Settings, home screen, Apple TV+, most non-DRM apps.

### QuickTime Side Effects

When QuickTime mirror is active:
- Red recording border appears on TV
- Audio routes to Mac instead of TV speakers
- DRM apps may refuse to play

**Solution:** Always run `disconnect` after starting playback. The `do` command does this automatically.

### Cost

**Vision loop (AI agent mode):** Uses Claude API for every see-think-act step. Each step = 1 API call with screenshot.

- Typical task: 5-10 steps = few cents
- Complex navigation: up to 20 steps = ~$0.10-0.20
- Uses Haiku 4.5 (cheap) with auto-escalation to Sonnet 4.5 when stuck

**Plex direct control:** 2 API calls total (pennies) — no vision loop.

**Manual commands (`cmd`, `type`, `launch`):** Zero API cost.

### Config File

`~/.clawtv/config.json` stores:

```json
{
  "devices": {
    "Living Room": {
      "identifier": "...",
      "credentials": "..."
    }
  },
  "screenshot_method": "auto",
  "plex_url": "http://192.168.1.100:32400",
  "plex_token": "your-plex-token",
  "plex_client": "Living Room"
}
```

## Companion Project

[**Lookout**](https://github.com/akivasolutions/lookout-tvos) — tvOS app with built-in HTTP screenshot server at port 8080. Fastest possible screenshot method (~100ms) but only captures Lookout's own UI, not other apps.

## Requirements

- **macOS** (uses AppleScript for automation)
- **Apple TV 4K** (gen 2 or later, tvOS 16+) on same network as Mac
- **Python 3.9+**
- **Anthropic API key** for Claude vision
- **QuickTime Player** (built-in) or **Xcode** (free from App Store)

## Troubleshooting

**"No Apple TV found"**
- Run `python3 ~/Developer/clawtv/clawtv.py scan` to verify device is on network
- Check that Apple TV and Mac are on same WiFi/LAN
- Verify Apple TV is awake (not in sleep mode)

**"QuickTime mirror disconnected"**
- DRM app killed the mirror — use `--method xcode` instead
- Or use Plex direct control to bypass vision entirely

**"Screenshot failed"**
- QuickTime: Ensure AirPlay pairing is accepted on TV
- Xcode: Verify Devices window is open and Apple TV is connected
- Try `--method auto` to fall back automatically

**"API key not found"**
- Set `export ANTHROPIC_API_KEY=sk-ant-...` in your shell
- Or add to ~/.zshrc or ~/.bashrc

**"Plex not found"**
- Verify `plex_url`, `plex_token`, and `plex_client` in config
- Run `python3 ~/Developer/clawtv/clawtv.py plex clients` to verify client name
- Ensure Plex server is running and accessible

## Architecture

```
clawtv.py            — Single-file CLI: pairing, remote, screenshots, AI agent
~/.clawtv/
  config.json        — Device pairing credentials + settings
  screenshots/       — Screenshot history (timestamped PNGs)
```

**Stack:**
- [pyatv](https://github.com/postlund/pyatv) — Apple TV remote control (Companion protocol)
- [QuickTime Player](https://support.apple.com/guide/quicktime-player/) — AirPlay mirror for screenshots (primary)
- [Xcode](https://developer.apple.com/xcode/) — Developer device screenshots (fallback)
- [Claude](https://www.anthropic.com/) — Vision + reasoning for autonomous navigation
- [python-plexapi](https://github.com/pkkid/python-plexapi) — Plex direct control

## License

MIT — see [LICENSE](LICENSE)
