---
name: spotify-connect
description: Control Spotify playback on remote Spotify Connect devices (speakers, TVs, Echo, phone, desktop). Use when user wants to play music, pause, skip, adjust volume, list audio devices, or transfer playback to a specific device. Supports multiple Spotify accounts with named profiles. Requires Spotify Premium.
metadata:
  openclaw:
    emoji: "🎵"
    requires:
      bins: ["uv"]
      env:
        SPOTIFY_CLIENT_ID: "required"
        SPOTIFY_CLIENT_SECRET: "required"
---

# Spotify Connect

Control Spotify playback on any Spotify Connect device. Supports multiple authenticated accounts.

## Setup (one-time)

1. Create a Spotify app at https://developer.spotify.com/dashboard
   - Set redirect URI to `http://127.0.0.1:8888/callback`
   - Enable "Web API" and "Web Playback SDK"
   - Note the Client ID and Client Secret
2. Set environment variables (or add to OpenClaw config under `env.vars`):
   ```bash
   export SPOTIFY_CLIENT_ID="your-client-id"
   export SPOTIFY_CLIENT_SECRET="your-client-secret"
   ```
3. Run initial auth (opens browser):
   ```bash
   uv run {baseDir}/scripts/spotify.py auth --name "alice"
   ```
   This creates a named account profile with auto-refreshing token.

4. (Optional) Add more accounts:
   ```bash
   uv run {baseDir}/scripts/spotify.py auth --name "bob"
   ```

5. (Optional) Configure device aliases in `~/.openclaw/spotify-connect/devices.json`:
   ```json
   {
     "kitchen": "Kitchen Echo",
     "kids": "Kids Room Echo",
     "office": "Office Speaker"
   }
   ```

## Dependencies

Python dependencies are managed inline via [PEP 723](https://peps.python.org/pep-0723/) — `uv run` handles installation automatically. No manual `pip install` needed.

## Account Management

```bash
# Authenticate a new account (opens browser)
uv run {baseDir}/scripts/spotify.py auth --name "alice"

# List all authenticated accounts
uv run {baseDir}/scripts/spotify.py accounts

# Switch active account (by name or email)
uv run {baseDir}/scripts/spotify.py switch alice
uv run {baseDir}/scripts/spotify.py switch bob@example.com

# Remove an account
uv run {baseDir}/scripts/spotify.py logout alice
```

The active account is used for all playback commands. Account data is stored in `~/.openclaw/spotify-connect/accounts.json`.

## Commands

All commands use: `uv run {baseDir}/scripts/spotify.py <command> [args]`

### List devices

```bash
# Current account only
uv run {baseDir}/scripts/spotify.py devices

# All accounts in parallel (recommended before playing on a specific device)
uv run {baseDir}/scripts/spotify.py devices --all-accounts
```

### Play

```bash
# Resume playback (current device or specify one)
uv run {baseDir}/scripts/spotify.py play
uv run {baseDir}/scripts/spotify.py play --device "kitchen"

# Play a song, artist, album, or playlist (searches Spotify)
uv run {baseDir}/scripts/spotify.py play --query "Bohemian Rhapsody"
uv run {baseDir}/scripts/spotify.py play --query "artist:Radiohead"
uv run {baseDir}/scripts/spotify.py play --query "album:OK Computer"
uv run {baseDir}/scripts/spotify.py play --query "playlist:Chill Vibes"
uv run {baseDir}/scripts/spotify.py play --uri "spotify:track:6rqhFgbbKwnb9MLmUQDhG6"

# Play on a specific device
uv run {baseDir}/scripts/spotify.py play --query "Daft Punk" --device "office"
```

### Playback control

```bash
uv run {baseDir}/scripts/spotify.py pause
uv run {baseDir}/scripts/spotify.py next
uv run {baseDir}/scripts/spotify.py prev
uv run {baseDir}/scripts/spotify.py volume 75
uv run {baseDir}/scripts/spotify.py volume 75 --device "kitchen"
uv run {baseDir}/scripts/spotify.py shuffle on
uv run {baseDir}/scripts/spotify.py shuffle off
uv run {baseDir}/scripts/spotify.py repeat track   # track, context, or off
```

### Transfer playback

```bash
uv run {baseDir}/scripts/spotify.py transfer "kitchen"
```

### Now playing

```bash
uv run {baseDir}/scripts/spotify.py status
```

## Device matching

Device names are fuzzy-matched. Use aliases from `devices.json` or partial Spotify device names. If ambiguous, the script lists matches.

**IMPORTANT — Cross-account device discovery:** When the user requests playback on a specific room or device, run `devices --all-accounts` first to see ALL devices across ALL accounts in one parallel call. Then switch to the account that owns the target device before issuing the play command. Don't assume which account a device belongs to.

## Common errors

- **"No active device"** — Open Spotify on any device first, or specify `--device`
- **"Premium required"** — Spotify Premium account needed for Connect control
- **"Device not found"** — Run `devices` to see available devices; sleeping devices may not appear (play something on the device first to wake it)
- **"No active account"** — Run `auth --name <name>` to authenticate, or `switch <name>` to select one
