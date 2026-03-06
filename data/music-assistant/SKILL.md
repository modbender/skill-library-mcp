---
name: music-assistant
description: Control Music Assistant (Home Assistant music server) - playback, volume, queue management, and library search. Use when user wants to play/pause music, skip tracks, adjust volume, search their music library, check what's playing, manage the queue, or control any Music Assistant player. Works with Spotify, Plex, local files, and other music providers integrated with Music Assistant.
metadata:
  openclaw:
    requires:
      env:
        - MA_URL
        - MA_TOKEN
      env_optional:
        - MA_PLAYER
---

# Music Assistant

Control your Music Assistant server for music playback, queue management, and library browsing.

## Setup

Before using this skill, you need to configure your Music Assistant connection:

```bash
# Required
export MA_URL="http://YOUR_SERVER_IP:8095/api"
export MA_TOKEN="YOUR_BEARER_TOKEN"

# Optional - auto-detected if not set
export MA_PLAYER="your_player_id"
```

**Finding your token:**
1. Open Music Assistant web UI
2. Go to Settings → Security
3. Create or copy your Long-Lived Access Token

**Finding your player ID:**
```bash
./scripts/mactl.py players
```

## Quick Start

```bash
# Basic controls
./scripts/mactl.py play          # Play/pause toggle
./scripts/mactl.py next          # Skip track
./scripts/mactl.py volume 75     # Set volume to 75%

# Search and play
./scripts/mactl.py search "nirvana"
./scripts/mactl.py play-search "pink floyd"  # Search and play first result

# Check what's playing
./scripts/mactl.py status
./scripts/mactl.py queue
```

## Playback Controls

```bash
./scripts/mactl.py play          # Play/pause toggle
./scripts/mactl.py pause         # Pause
./scripts/mactl.py stop          # Stop playback
./scripts/mactl.py next          # Next track
./scripts/mactl.py prev          # Previous track
```

## Volume

```bash
./scripts/mactl.py volume 75     # Set volume 0-100
./scripts/mactl.py mute          # Mute
./scripts/mactl.py unmute        # Unmute
```

## Queue Management

```bash
./scripts/mactl.py shuffle true  # Enable shuffle
./scripts/mactl.py shuffle false # Disable shuffle
./scripts/mactl.py repeat all    # Repeat mode (off|all|one)
./scripts/mactl.py clear         # Clear queue
./scripts/mactl.py queue-items   # List queue contents
```

## Search & Play

```bash
# Search library
./scripts/mactl.py search "pink floyd"
./scripts/mactl.py search "nirvana" --type track album
./scripts/mactl.py search "metallica" --limit 5

# Search and immediately play first result
./scripts/mactl.py play-search "smells like teen spirit"
./scripts/mactl.py ps "comfortably numb"  # shorthand

# Play by URI (for scripts/advanced use)
./scripts/mactl.py play-uri "spotify://track/4gHnSNHs8RyVukKoWdS99f"
```

## Status & Info

```bash
./scripts/mactl.py status        # Show player status + now playing
./scripts/mactl.py queue         # Queue status
./scripts/mactl.py recent        # Recently played items
./scripts/mactl.py players       # List all available players
```

## Library

```bash
./scripts/mactl.py sync          # Trigger library sync
```

## Examples

**"Play some Nirvana"**
```bash
./scripts/mactl.py play-search "nirvana"
```

**"What's playing?"**
```bash
./scripts/mactl.py status
```

**"Skip this track"**
```bash
./scripts/mactl.py next
```

**"Set volume to 50%"**
```bash
./scripts/mactl.py volume 50
```

**"Turn on shuffle"**
```bash
./scripts/mactl.py shuffle true
```

## Direct API Access

For operations not covered by the CLI, use the JSON-RPC API directly:

```bash
curl -s "http://YOUR_SERVER:8095/api" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MA_TOKEN" \
  -d '{"message_id":"1","command":"player_queues/all"}'
```

API documentation is available at: `http://YOUR_SERVER:8095/api-docs`

### Key API Commands

| Command | Args | Description |
|---------|------|-------------|
| `players/all` | - | List all players |
| `player_queues/all` | - | List all queues |
| `player_queues/play_pause` | `queue_id` | Toggle play/pause |
| `player_queues/next` | `queue_id` | Next track |
| `player_queues/previous` | `queue_id` | Previous track |
| `player_queues/stop` | `queue_id` | Stop playback |
| `player_queues/shuffle` | `queue_id`, `shuffle_enabled` | Set shuffle |
| `player_queues/repeat` | `queue_id`, `repeat_mode` | Set repeat (off/all/one) |
| `player_queues/clear` | `queue_id` | Clear queue |
| `player_queues/items` | `queue_id`, `limit`, `offset` | Get queue items |
| `player_queues/play_media` | `queue_id`, `uri` | Play by URI |
| `music/search` | `search`, `media_types`, `limit` | Search library |
| `music/recently_played_items` | `limit` | Recent items |
| `music/sync` | `media_types`, `providers` | Sync library |
| `config/players/get` | `player_id` | Get player settings |
