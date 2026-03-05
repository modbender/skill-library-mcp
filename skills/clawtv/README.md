# ClawTV

**AI-powered Apple TV remote that can see your screen.**

Tell it what you want in plain English and it navigates any app autonomously using vision + remote control. No per-app APIs needed — it works with every app on your Apple TV.

```
python clawtv.py do "open Plex and play Fight Club"
```

ClawTV takes screenshots of your Apple TV, sends them to Claude's vision API to understand what's on screen, then sends remote commands to navigate — just like a person would. It repeats this see-think-act loop until it accomplishes your goal.

## Demo

```
$ python clawtv.py do "find Fight Club on Plex and play it"

--- Step 1 ---
  AI: {"action": "launch", "app": "com.plexapp.plex"}
  -> launched: com.plexapp.plex

--- Step 2 ---
  AI: {"action": "remote", "commands": ["up"]}
  -> up
  (sees Plex sidebar, Search is highlighted)

--- Step 3 ---
  AI: {"action": "remote", "commands": ["select"]}
  -> select
  (sees search screen with keyboard)

--- Step 4 ---
  AI: {"action": "type", "text": "fight club"}
  -> typed: fight club
  (sees search results)

--- Step 5 ---
  AI: {"action": "remote", "commands": ["down", "down"]}
  -> down -> down
  (Fight Club 1999 is highlighted)

--- Step 6 ---
  AI: {"action": "remote", "commands": ["select"]}
  -> select
  (sees movie details page — 1080p, 5.1, R rated)

--- Step 7 ---
  AI: {"action": "remote", "commands": ["select"]}
  -> select

  Done: Fight Club is now playing in 1080p
```

## How It Works

```
┌─────────────┐    screenshot    ┌─────────────┐    analyze     ┌─────────────┐
│  Apple TV    │ ──────────────> │   ClawTV     │ ────────────> │   Claude     │
│  (screen)    │ <────────────── │   (agent)    │ <──────────── │   (vision)   │
└─────────────┘  remote control  └─────────────┘   commands     └─────────────┘
```

1. **See** — Takes a screenshot of the Apple TV
2. **Think** — Sends the screenshot to Claude, which analyzes the UI and decides what to do
3. **Act** — Sends remote commands (navigate, select, type) via pyatv
4. **Repeat** — Takes another screenshot to verify, continues until the goal is met

## Screenshot Methods

ClawTV supports three screenshot capture methods:

| Method | Speed | Requirements | DRM Apps |
|--------|-------|-------------|----------|
| **QuickTime** (default) | ~0.6s | QuickTime Player, pyobjc-framework-Quartz | Black screen — DRM apps kill the mirror |
| **Lookout** | ~0.1s | [Lookout tvOS app](https://github.com/akivasolutions/lookout-tvos) on Apple TV | Only captures Lookout's own UI |
| **Xcode** (legacy) | ~2.5s | Xcode Devices window open | Works with all apps |

### QuickTime (recommended)

Uses QuickTime Player's wireless mirroring + `screencapture -l` to capture a specific window by CGWindowID. Fastest method, no Xcode needed.

**First-time setup:**
1. Run `python clawtv.py screenshot --method quicktime`
2. QuickTime opens and selects your Apple TV as video source
3. Accept the AirPlay pairing on your Apple TV (one-time PIN)
4. Subsequent runs reuse the existing mirror instantly

**DRM limitation:** Apps that enforce HDCP (YouTube, Netflix, Disney+, HBO Max) will terminate the AirPlay mirror entirely. When this happens, ClawTV auto-detects the disconnection and falls back to Xcode in `auto` mode. Plex (local media), Settings, and the home screen work fine.

### Lookout

Fetches screenshots over HTTP from the [Lookout tvOS app](https://github.com/akivasolutions/lookout-tvos) running on your Apple TV. Fastest possible method (~100ms) but only captures Lookout's own UI — not other apps.

### Xcode (legacy)

Automates the "Take Screenshot" button in Xcode's Devices window via AppleScript. Slower but works universally with all apps including DRM-protected ones.

### Configuration

Set a default method in `~/.clawtv/config.json`:

```json
{
  "screenshot_method": "auto"
}
```

Values: `auto` (default — tries quicktime → lookout → xcode), `quicktime`, `lookout`, `xcode`

Override per-command: `python clawtv.py screenshot --method xcode`

## Requirements

- **macOS** (uses AppleScript for automation)
- **Apple TV 4K** (gen 2 or later, tvOS 16+) on the same network as your Mac
- **Python 3.9+**
- **Anthropic API key** for Claude vision (`claude-sonnet-4-5-20250929`)

For QuickTime method: `pip install pyobjc-framework-Quartz`
For Xcode method: Xcode installed (free from Mac App Store)

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Pair with your Apple TV (remote control)

```bash
python clawtv.py pair
```

This scans your network, finds your Apple TV, and pairs over the Companion protocol. You'll enter a 4-digit PIN displayed on your TV. Credentials are saved to `~/.clawtv/config.json`.

### 3. Set up screenshots

**QuickTime (recommended):** Just run `python clawtv.py screenshot` — it sets up automatically. Accept the AirPlay pairing on your TV the first time.

**Xcode (fallback):** One-time setup:

1. On your Apple TV: **Settings > Privacy & Security** — enable "Share with App Devs"
2. Then go to **Settings > Remotes and Devices > Remote App and Devices**
3. On your Mac, open Xcode and press **Cmd+Shift+2** (Devices and Simulators)
4. Your Apple TV appears in the sidebar — click to pair, enter the code shown on TV
5. Keep the Xcode Devices window open while using ClawTV

### 4. Set your API key

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

### AI Agent Mode

Tell ClawTV what you want and it figures out the rest:

```bash
python clawtv.py do "open Plex and play Fight Club"
python clawtv.py do "search for Stranger Things on Netflix"
python clawtv.py do "open YouTube and find lo-fi beats"
python clawtv.py do "go to settings and turn on subtitles"
python clawtv.py do "open Spotify and play my liked songs"
```

### Manual Commands

```bash
# Remote control — send one or more commands
python clawtv.py cmd up
python clawtv.py cmd down down right select
python clawtv.py cmd select sleep:1.5 down    # with timing

# Type into a focused search/text field
python clawtv.py type "breaking bad"

# Launch an app by bundle ID
python clawtv.py launch com.plexapp.plex

# Take a screenshot (auto-detect best method)
python clawtv.py screenshot
python clawtv.py screenshot --method quicktime
python clawtv.py screenshot --method xcode

# See what's currently playing
python clawtv.py playing

# List all installed apps with bundle IDs
python clawtv.py apps

# Scan for Apple TVs on your network
python clawtv.py scan
```

### Common App Bundle IDs

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

Run `python clawtv.py apps` for the full list on your device.

## Why ClawTV?

**Every other smart TV solution requires per-app API integrations.** Plex has an API. Netflix doesn't. YouTube has one but it's limited. HomeKit can turn the TV on but can't navigate menus.

ClawTV doesn't care what app you're using. It looks at the screen and figures it out, just like you would with a remote in your hand. This means it works with:

- Plex, Netflix, Hulu, HBO Max, Disney+, Prime Video
- YouTube, Twitch, Spotify, Apple Music
- Apple TV+, Fitness+, Podcasts
- Settings, App Store — literally any app

## Architecture

```
clawtv.py            — Single-file CLI: pairing, remote, screenshots, AI agent
~/.clawtv/
  config.json        — Device pairing credentials + screenshot_method setting
  screenshots/       — Screenshot history (timestamped PNGs)
```

**Stack:**
- [pyatv](https://github.com/postlund/pyatv) — Apple TV remote control (Companion protocol)
- [QuickTime Player](https://support.apple.com/guide/quicktime-player/) — AirPlay mirror for screenshots (primary)
- [Xcode](https://developer.apple.com/xcode/) — Developer device screenshots via AppleScript (fallback)
- [Claude](https://www.anthropic.com/) — Vision + reasoning for autonomous UI navigation

**Companion project:** [Lookout](https://github.com/akivasolutions/lookout-tvos) — tvOS app with built-in screenshot server

## Limitations

- **macOS only** — Requires QuickTime or Xcode for screenshots
- **DRM apps blank QuickTime mirror** — YouTube, Netflix, Disney+, HBO Max enforce HDCP which kills the AirPlay session. Use Xcode method for these apps.
- **~0.6-2.5s per screenshot** — QuickTime is fast, Xcode is slower. Plus API round-trip time.
- **Screenshots, not video** — Works frame-by-frame, not real-time (sufficient for navigation)
- **First-time QuickTime pairing is manual** — You need to accept the AirPlay PIN on your TV once

## Cost Notice

ClawTV uses Claude's API for vision and reasoning — **every see-think-act loop costs money**. Each step sends a screenshot to the API, so a task that takes 10 steps = 10 API calls.

To prevent runaway costs, `MAX_STEPS` defaults to **20** per command. A typical task costs a few cents, but complex navigation can add up.

**Tip:** Use manual commands (`cmd`, `type`, `launch`) when you know exactly what to do — they skip the AI and cost nothing.

## Contributing

PRs welcome! Some ideas:

- [ ] Linux/Windows support via alternative screenshot tools
- [ ] Voice control mode (Whisper STT + ClawTV)
- [ ] Web UI with live screenshot feed
- [ ] Multi-TV support (manage multiple Apple TVs)
- [ ] App-specific fast paths (use Plex API for search, etc.)
- [ ] Screenshot caching / diff detection (skip redundant API calls)
- [ ] Smart DRM detection (auto-switch to Xcode when mirror drops)

## License

MIT — see [LICENSE](LICENSE)
