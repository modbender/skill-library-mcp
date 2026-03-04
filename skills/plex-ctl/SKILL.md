# plexctl — Plex Media Server Control

> Standalone CLI for controlling Plex Media Server and clients via the Plex API

## When to Use

**Trigger phrases:**
- "play [title] on Plex"
- "search Plex for [query]"
- "what's playing on Plex"
- "pause/resume Plex"
- "show me what's on deck"
- "what's new on Plex"
- "list Plex clients"
- "tell me about [movie/show]"

**Use this skill when:**
- User wants to play specific content on Plex
- User wants to search their Plex library
- User wants to control playback (pause, resume, stop, next, prev)
- User wants to see what's currently playing
- User wants to browse recently added content
- User wants to see continue watching (on-deck)
- User wants detailed info about a title

**Don't use this skill when:**
- User wants Apple TV-specific navigation (use ClawTV instead)
- User wants vision-based automation (use ClawTV instead)
- User wants to manage Plex server settings (use Plex web UI)

## Commands

### Setup
```bash
plexctl setup
```
Interactive first-time setup:
- Plex server URL (e.g., http://192.168.86.86:32400)
- Plex token
- Default client selection

### Playback
```bash
# Play a movie (fuzzy search)
plexctl play "Fight Club"
plexctl play "inception"

# Play specific TV episode
plexctl play "The Office" -s 3 -e 10
plexctl play "Westworld" --season 2 --episode 6

# Play on specific client (overrides default)
plexctl play "Matrix" -c "Living Room TV"
```

### Playback Control
```bash
plexctl pause              # Pause current playback
plexctl resume             # Resume playback
plexctl stop               # Stop playback
plexctl next               # Skip to next track/episode
plexctl prev               # Go to previous track/episode
```

### Search & Discovery
```bash
# Search across all libraries
plexctl search "matrix"
plexctl search "breaking bad"

# Recently added content
plexctl recent             # Last 10 items
plexctl recent -n 20       # Last 20 items

# Continue watching (on-deck)
plexctl on-deck

# What's currently playing
plexctl now-playing

# Detailed info about a title
plexctl info "Inception"
plexctl info "The Office"
```

### Library Management
```bash
# List all libraries
plexctl libraries

# List available clients
plexctl clients
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install plexapi
```

### 2. Run Setup
```bash
plexctl setup
```

You'll need:
- **Plex server URL**: Usually `http://[local-ip]:32400`
- **Plex token**: Get from Settings → Account → Authorized Devices
  - Or from browser URL when logged into Plex Web
  - Look for `X-Plex-Token` parameter
- **Default client**: The tool will discover available clients

### 3. Verify
```bash
plexctl clients            # Should list your devices
plexctl libraries          # Should list your libraries
plexctl search "test"      # Should return results
```

## Required Credentials

Config stored in `~/.plexctl/config.json`:

```json
{
  "plex_url": "http://192.168.86.86:32400",
  "plex_token": "your-plex-token-here",
  "default_client": "Apple TV"
}
```

### Getting Your Plex Token

**Method 1: Settings Page**
1. Log into Plex Web (app.plex.tv)
2. Settings → Account → Authorized Devices
3. Look for your token in the page source or URL

**Method 2: Browser URL**
1. Open any Plex Web page while logged in
2. Check the URL for `X-Plex-Token=...`
3. Copy the token value

**Method 3: XML Direct Method**
1. Navigate to: `http://[your-plex-ip]:32400/?X-Plex-Token=`
2. View page source
3. Look for `authToken` attribute

## Privacy & Data

- **Local only**: Connects directly to your Plex Media Server on your local network
- **No cloud APIs**: All communication is local (unless using Plex cloud discovery as fallback)
- **No external services**: No data sent to third parties
- **No telemetry**: No usage tracking or analytics
- **Config storage**: Only stores Plex URL, token, and default client locally

**Note**: Plex cloud discovery (MyPlex) is only used as a fallback when local GDM discovery fails. All media playback is direct to your local server.

## Common Use Cases

### 1. Quick Movie Playback
```bash
plexctl play "Fight Club"
```
Searches library, finds best match, starts playing on default client.

### 2. Binge Watching TV Shows
```bash
plexctl play "Breaking Bad" -s 1 -e 1
# ... watch episode ...
plexctl next                    # Next episode
plexctl next                    # Next episode
```

### 3. Continue Watching
```bash
plexctl on-deck                 # See what's in progress
plexctl play "Show Name"        # Resume from where you left off
```

### 4. Browse New Content
```bash
plexctl recent                  # See what's new
plexctl info "Movie Title"      # Get details
plexctl play "Movie Title"      # Watch it
```

### 5. Multi-Client Control
```bash
plexctl clients                           # List all clients
plexctl play "Movie" -c "Bedroom TV"      # Play on specific client
plexctl pause -c "Living Room TV"         # Pause specific client
```

### 6. Library Search
```bash
plexctl search "christopher nolan"        # Find all Nolan films
plexctl search "breaking"                 # Fuzzy search
plexctl info "Inception"                  # Get details before watching
```

## Fuzzy Matching

The `play` and `info` commands use fuzzy search:
- "fight club" → "Fight Club (1999)"
- "inception" → "Inception"
- "office" → "The Office (U.S.)"

Exact matches are prioritized over partial matches.

## Error Handling

**Client not found:**
```
Error: Client 'Apple TV' not found

Available clients:
  Local:
    • Living Room TV (Plex for Apple TV)
    • Bedroom (Plex Web)
```

**No results:**
```
No results found for: xyz123
```

**Connection failed:**
```
Error connecting to Plex server: [Errno 61] Connection refused
URL: http://192.168.86.86:32400
Check your plex_url and plex_token in config
```

## Integration with OpenClaw

When a user asks to play something on Plex:

1. **Parse the request** — extract title, season, episode
2. **Choose command:**
   - Movie: `plexctl play "Title"`
   - TV show specific episode: `plexctl play "Show" -s N -e N`
   - Search first: `plexctl search "query"` then `plexctl play "Title"`
3. **Execute and report** — run command, share output with user

**Example agent flow:**
```
User: "Play Fight Club on Plex"
Agent: [exec] plexctl play "Fight Club"
Output: Found: Fight Club (1999) (movie)
        ✓ Playing on Apple TV
Agent: "Now playing Fight Club on your Apple TV"
```

## Troubleshooting

**Can't connect to Plex:**
- Verify server is running
- Check URL (should be http://IP:32400, not https)
- Verify token is correct
- Check firewall settings

**Client not found:**
- Make sure Plex app is open on the client device
- Run `plexctl clients` to see available clients
- Try cloud discovery (automatic fallback)
- Restart Plex app on client device

**Playback fails:**
- Verify client can play the content type
- Check client is still active (`plexctl clients`)
- Try playing manually in Plex app first
- Check Plex server logs

**Search returns no results:**
- Verify content exists in your library
- Try broader search terms
- Check library is scanned and up-to-date
- Run `plexctl libraries` to verify library access

## Performance

- **Local GDM discovery**: ~100ms
- **Cloud fallback discovery**: ~500-1000ms
- **Search**: ~200-500ms depending on library size
- **Playback start**: ~500ms
- **Control commands**: ~100ms

All operations are direct Plex API calls — no vision, no screenshots, no AI inference needed.

## Differences from ClawTV

| Feature | plexctl | ClawTV |
|---------|---------|--------|
| Plex control | ✅ Direct API | ✅ API + Vision |
| Apple TV remote | ❌ | ✅ |
| Vision-based navigation | ❌ | ✅ |
| Any streaming app | ❌ | ✅ |
| Speed | ⚡ Instant | 🐢 Slower (screenshots) |
| Dependencies | plexapi only | pyatv, Anthropic API, QuickTime |
| Use case | Plex-only control | Universal TV automation |

**When to use plexctl**: Fast, direct Plex control  
**When to use ClawTV**: Complex navigation, non-Plex apps, vision-based automation
