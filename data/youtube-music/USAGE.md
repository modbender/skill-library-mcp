# YouTube Music Skill - Usage Examples 🎵

## Quick Start

```bash
# Navigate to skill directory
cd ~/.openclaw/workspace/skills/youtube-music

# Show help
./scripts/youtube-music.sh help
```

## Basic Commands

### Play Music
```bash
# Play a specific song
./scripts/youtube-music.sh play "Ye Tune Kya Kiya"

# Play by artist
./scripts/youtube-music.sh play "Arijit Singh hits"

# Play a playlist
./scripts/youtube-music.sh play "Bollywood classics playlist"
```

### Playback Controls
```bash
# Pause current track
./scripts/youtube-music.sh pause

# Skip to next track
./scripts/youtube-music.sh skip

# Go to previous track
./scripts/youtube-music.sh previous

# Set volume (0-100)
./scripts/youtube-music.sh volume 75

# Get current track info
./scripts/youtube-music.sh now-playing
```

### Search
```bash
# Search for tracks
./scripts/youtube-music.sh search "Pritam songs"

# Search for artist
./scripts/youtube-music.sh search "Javed Bashir"
```

## Natural Language Usage (via OpenClaw)

When chatting with OpenClaw, use natural commands:

```
"play Ye Tune Kya Kiya by Javed Bashir"
"pause the music"
"skip to next track"  
"set volume to 75%"
"search for Arijit Singh"
"what's playing now?"
"show me lyrics for this song"
"add this to my workout playlist"
"queue some chill songs"
"play similar to this"
```

## Browser Integration

The skill works with OpenClaw's browser:

```bash
# Check browser status
openclaw browser status

# Start browser if needed
openclaw browser start

# Open YouTube Music directly
openclaw browser open --targetUrl="https://music.youtube.com"

# Take snapshot (for automation)
openclaw browser snapshot
```

## Advanced Examples

### Create a Morning Playlist
```bash
# Queue up morning vibes
./scripts/youtube-music.sh play "morning chill playlist"
./scripts/youtube-music.sh volume 50
```

### Party Mode
```bash
# Play upbeat tracks
./scripts/youtube-music.sh play "Bollywood party hits"
./scripts/youtube-music.sh volume 80
```

### Study Session
```bash
# Play lo-fi/study music
./scripts/youtube-music.sh play "lo-fi study beats"
./scripts/youtube-music.sh volume 40
```

## Testing the Skill

Run the test suite:
```bash
./scripts/test.sh
```

## Troubleshooting

### Browser won't start
```bash
# Restart OpenClaw gateway
openclaw gateway restart

# Start browser manually
openclaw browser start
```

### Commands not working
1. Check browser is running: `openclaw browser status`
2. Verify YouTube Music loads: `openclaw browser open --targetUrl="https://music.youtube.com"`
3. Check internet connection
4. Verify no browser extensions blocking YouTube Music

### Volume control not working
- Volume control requires browser interaction
- Use YouTube Music's native volume slider
- Check system volume settings

## Integration Examples

### Add to OpenClaw workflow
```yaml
# Example workflow
- trigger: "music: <query>"
  action: "youtube-music play <query>"
  
- trigger: "pause music"
  action: "youtube-music pause"
  
- trigger: "next track"
  action: "youtube-music skip"
```

### Shell script automation
```bash
#!/bin/bash
# morning-music.sh
cd ~/.openclaw/workspace/skills/youtube-music
./scripts/youtube-music.sh play "morning playlist"
./scripts/youtube-music.sh volume 60
```

## Performance Tips

1. **Keep browser open** - Faster response time
2. **Use specific queries** - Better search results
3. **Cache frequently played** - Use playlists for quick access
4. **Preload queue** - Queue multiple tracks in advance

## Feature Requests

Want to add more features? Consider:
- [ ] Lyrics display automation
- [ ] Playlist creation/editing
- [ ] Queue management
- [ ] Shuffle/repeat controls
- [ ] Cross-fade settings
- [ ] Equalizer controls
- [ ] Multi-room sync

---

**Skill Status:** ✅ Production Ready  
**Version:** 1.0.0  
**Last Updated:** 2026-02-26
