# plexctl

> Standalone CLI for controlling Plex Media Server and clients via the Plex API

Fast, simple Plex control from the command line. No Apple TV, no vision, no automation — just direct Plex API calls.

## What It Does

- **Play content** — Movies, TV shows, music with fuzzy search
- **Control playback** — Pause, resume, stop, next, previous
- **Search library** — Find content across all your Plex libraries
- **Browse content** — Recently added, on-deck (continue watching)
- **Get info** — Detailed metadata about any title
- **Multi-client** — Control any Plex client on your network

## Quick Start

### 1. Install
```bash
pip install plexapi
```

### 2. Setup
```bash
chmod +x plexctl.py
./plexctl.py setup
```

You'll need:
- Plex server URL (e.g., `http://192.168.86.86:32400`)
- Plex token (see [Getting Your Plex Token](#getting-your-plex-token))
- Default client (auto-discovered during setup)

### 3. Use
```bash
./plexctl.py play "Fight Club"
./plexctl.py search "matrix"
./plexctl.py now-playing
./plexctl.py pause
```

## All Commands

### Playback
```bash
# Play a movie
plexctl play "Inception"
plexctl play "fight club"

# Play TV show episode
plexctl play "The Office" -s 3 -e 10
plexctl play "Breaking Bad" --season 5 --episode 14

# Play on specific client
plexctl play "Matrix" -c "Bedroom TV"
```

### Playback Control
```bash
plexctl pause              # Pause current playback
plexctl resume             # Resume playback
plexctl stop               # Stop playback
plexctl next               # Next track/episode
plexctl prev               # Previous track/episode
```

### Search & Discovery
```bash
# Search library
plexctl search "christopher nolan"
plexctl search "breaking"

# Recently added
plexctl recent             # Last 10 items
plexctl recent -n 20       # Last 20 items

# Continue watching
plexctl on-deck

# What's playing
plexctl now-playing

# Get detailed info
plexctl info "Inception"
```

### Library
```bash
plexctl libraries          # List all libraries
plexctl clients            # List available clients
```

## Setup Guide

### Getting Your Plex Token

**Option 1: Settings Page**
1. Log into [Plex Web](https://app.plex.tv)
2. Go to Settings → Account → Authorized Devices
3. Look for `X-Plex-Token` in the URL or page source

**Option 2: Browser URL**
1. Open any Plex Web page while logged in
2. Look for `X-Plex-Token=...` in the URL
3. Copy the token value

**Option 3: XML Direct Method**
```bash
# Navigate to this URL in your browser:
http://[your-plex-ip]:32400/?X-Plex-Token=

# View page source, look for "authToken" attribute
```

### Finding Your Plex Server URL

Your Plex server URL is typically:
```
http://[local-ip]:32400
```

Common patterns:
- `http://192.168.1.100:32400`
- `http://192.168.86.86:32400`
- `http://10.0.0.50:32400`

**Finding your server IP:**
1. Open Plex Web at app.plex.tv
2. Settings → Network → Show Advanced
3. Look for "LAN Networks" or check your router's device list

### Config File

Config is stored at `~/.plexctl/config.json`:

```json
{
  "plex_url": "http://192.168.86.86:32400",
  "plex_token": "your-plex-token-here",
  "default_client": "Apple TV"
}
```

You can manually edit this file or run `plexctl setup` to reconfigure.

## Features

### Fuzzy Search
The `play` and `info` commands use fuzzy matching:
- "fight club" → "Fight Club (1999)"
- "inception" → "Inception"
- "office" → "The Office (U.S.)"

Exact matches are prioritized.

### Multi-Client Support
Control any Plex client on your network:
- Apple TV
- Roku
- Shield TV
- Web browsers
- Mobile apps
- Smart TVs

Discovers clients via local GDM and cloud MyPlex (fallback).

### Smart Episode Navigation
For TV shows, specify season and episode:
```bash
plexctl play "Show Name" -s 2 -e 6
```

The tool searches for the show, navigates to the specific season and episode, then plays it.

### Now Playing Status
See what's playing across all clients:
```bash
plexctl now-playing
```

Shows:
- Client name
- Currently playing title
- Playback state (playing/paused)
- Progress (time position)

### Recently Added
Browse new content:
```bash
plexctl recent
```

Shows last 10 items added to your library (movies, TV episodes, music).

### On-Deck (Continue Watching)
Pick up where you left off:
```bash
plexctl on-deck
```

Shows all in-progress content with completion percentage.

### Detailed Info
Get metadata about any title:
```bash
plexctl info "Inception"
```

Shows:
- Year, rating, content rating
- Duration, genres, cast, director
- Full plot summary
- Season/episode counts (for TV shows)

## Examples

### Binge Watching
```bash
# Start a show
plexctl play "Breaking Bad" -s 1 -e 1

# Next episode
plexctl next

# Pause for snacks
plexctl pause

# Resume
plexctl resume

# Next episode
plexctl next
```

### Movie Night
```bash
# Browse recent additions
plexctl recent

# Get details
plexctl info "The Matrix"

# Play it
plexctl play "The Matrix"

# Pause for bathroom break
plexctl pause

# Resume
plexctl resume
```

### Search & Play
```bash
# Search for Nolan films
plexctl search "christopher nolan"

# Get info about one
plexctl info "Interstellar"

# Play it
plexctl play "Interstellar"
```

### Multi-Room Control
```bash
# List all clients
plexctl clients

# Play on bedroom TV
plexctl play "Movie" -c "Bedroom TV"

# Pause living room
plexctl pause -c "Living Room TV"

# Check what's playing everywhere
plexctl now-playing
```

## Troubleshooting

### Can't Connect to Plex Server
**Symptoms:**
```
Error connecting to Plex server: [Errno 61] Connection refused
```

**Solutions:**
- Verify Plex Media Server is running
- Check the URL (should be `http://`, not `https://`)
- Verify the IP address is correct
- Check firewall settings
- Try accessing the URL in a browser: `http://[ip]:32400/web`

### Client Not Found
**Symptoms:**
```
Error: Client 'Apple TV' not found
```

**Solutions:**
- Make sure the Plex app is open on the client device
- Run `plexctl clients` to see available clients
- Check client name spelling (case-sensitive)
- Restart the Plex app on the client
- Wait a few seconds for client to appear on network

### No Search Results
**Symptoms:**
```
No results found for: [query]
```

**Solutions:**
- Verify content exists in your library
- Try broader search terms
- Check library has been scanned recently
- Run `plexctl libraries` to verify library access
- Rescan library in Plex Web

### Playback Fails
**Symptoms:**
```
Error: Playback failed: [error]
```

**Solutions:**
- Verify client can play the content format
- Check client is still active: `plexctl clients`
- Try playing manually in Plex app first
- Check Plex server logs for errors
- Verify network connectivity

## Performance

All operations are direct Plex API calls:

| Operation | Typical Speed |
|-----------|---------------|
| Local client discovery | ~100ms |
| Cloud fallback discovery | ~500-1000ms |
| Search | ~200-500ms |
| Playback start | ~500ms |
| Control commands | ~100ms |

No vision processing, no screenshots, no AI inference — just fast API calls.

## Requirements

- Python 3.7+
- `plexapi` library (`pip install plexapi`)
- Plex Media Server (running on your network)
- At least one Plex client (Apple TV, Roku, etc.)

## Privacy

- **Local only**: All communication is with your local Plex server
- **No cloud APIs**: Direct network connection (cloud discovery is optional fallback)
- **No external services**: No data sent to third parties
- **No telemetry**: No usage tracking or analytics
- **Local config**: Token stored only on your machine

## Differences from ClawTV

**plexctl** is a focused, fast Plex control tool.  
**ClawTV** is a universal Apple TV automation tool with vision.

| Feature | plexctl | ClawTV |
|---------|---------|--------|
| Plex control | ✅ Direct API | ✅ API + Vision |
| Apple TV remote | ❌ | ✅ |
| Vision navigation | ❌ | ✅ |
| Any streaming app | ❌ | ✅ |
| Speed | ⚡ Instant | 🐢 Slower |
| Dependencies | plexapi only | pyatv, Anthropic, QuickTime |

**Use plexctl when**: You want fast, direct Plex control  
**Use ClawTV when**: You need universal TV automation or vision-based navigation

## License

MIT License — Copyright 2026 Akiva Solutions LLC

## Author

Built for the OpenClaw skill ecosystem.

Part of the Akiva Solutions AI agent toolkit.
