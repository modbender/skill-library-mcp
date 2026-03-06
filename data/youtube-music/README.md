# YouTube Music Skill for OpenClaw 🎵

Control YouTube Music with natural language commands. Full playback control via browser automation.

## Features ✨

- 🎵 **Play tracks** - Search and play any song, artist, or album
- ⏯️ **Playback control** - Play, pause, skip, previous track
- 🔊 **Volume control** - Set volume levels, mute/unmute
- 📋 **Queue management** - View and manage playback queue
- 🎶 **Search** - Find tracks, artists, albums, playlists
- 💾 **Playlists** - Create and manage playlists
- 📝 **Lyrics** - Display lyrics for current track
- 🎯 **Smart recommendations** - Get suggestions based on current track

## Installation

The skill is located at: `~/.openclaw/workspace/skills/youtube-music/`

No additional setup required - uses OpenClaw's built-in browser automation.

## Usage

### Basic Commands

```bash
# Play a track
./scripts/youtube-music.sh play "Ye Tune Kya Kiya"

# Playback controls
./scripts/youtube-music.sh pause
./scripts/youtube-music.sh skip
./scripts/youtube-music.sh previous

# Volume control
./scripts/youtube-music.sh volume 75

# Search
./scripts/youtube-music.sh search "Arijit Singh"

# Get current track
./scripts/youtube-music.sh now-playing
```

### Natural Language Examples

When using with OpenClaw, you can use natural language:

```
"play Ye Tune Kya Kiya by Javed Bashir"
"pause the music"
"skip to next track"
"set volume to 75%"
"search for Arijit Singh hits"
"what's playing now?"
"show me the lyrics"
"queue some chill Bollywood songs"
"add this to my workout playlist"
```

## Scripts

### `youtube-music.sh`
Main bash script for controlling YouTube Music

```bash
./scripts/youtube-music.sh <command> [args]
```

### `control.js`
Node.js script for advanced control and automation

```bash
node scripts/control.js play "Ye Tune Kya Kiya"
node scripts/control.js search "Pritam"
node scripts/control.js pause
```

## Browser Integration

The skill uses OpenClaw's browser tool:
- **Profile**: `openclaw` (isolated browser)
- **Base URL**: `https://music.youtube.com`
- **CDP Port**: 18800

### Browser Commands

```bash
# Check browser status
openclaw browser status

# Start browser
openclaw browser start

# Open YouTube Music
openclaw browser open --targetUrl="https://music.youtube.com"

# Take snapshot (for automation)
openclaw browser snapshot
```

## Configuration

Add to your `TOOLS.md`:

```markdown
### YouTube Music
- Default profile: openclaw
- Preferred quality: high
- Auto-play: on
- Shuffle default: off
```

## Examples

### Play a Song
```
User: "play Tuna Kay Keya"
Assistant: Opens YouTube Music search for "Tuna Kay Keya"
```

### Control Playback
```
User: "pause"
Assistant: Pauses current track

User: "skip"
Assistant: Skips to next track
```

### Search & Discover
```
User: "find similar to this"
Assistant: Shows related tracks based on current song
```

## Troubleshooting

### Browser not starting
```bash
# Restart OpenClaw gateway
openclaw gateway restart

# Start browser manually
openclaw browser start
```

### No sound
- Check system volume
- Verify YouTube Music isn't muted in browser
- Check browser tab isn't muted

### Search not working
- Ensure internet connection
- Verify YouTube Music is accessible in your region
- Try alternative search terms

## Advanced Usage

### Automation Script Example

```bash
#!/bin/bash
# Auto-play morning playlist
cd ~/.openclaw/workspace/skills/youtube-music
./scripts/youtube-music.sh play "morning chill playlist"
./scripts/youtube-music.sh volume 50
```

### Integration with OpenClaw Messages

The skill can respond to natural language commands via OpenClaw's message system.

## Limitations

- Requires browser to be running
- Some features need YouTube Premium
- Lyrics availability varies by region
- Queue management limited to current session

## Future Enhancements

- [ ] YouTube Music API integration
- [ ] Offline mode with cached tracks
- [ ] Cross-platform sync
- [ ] Voice control integration
- [ ] Smart playlists based on mood/activity
- [ ] Multi-room audio support

## Contributing

Contributions welcome! Areas for improvement:
- Better selector detection for player controls
- Playlist management automation
- Enhanced search algorithms
- Regional support improvements

## License

MIT License - See SKILL.md for details

## Support

For issues or questions:
1. Check troubleshooting section
2. Verify browser is running
3. Ensure YouTube Music is accessible in your region
4. Check OpenClaw logs for errors

---

**Created for:** OpenClaw Community  
**Skill Version:** 1.0.0  
**Status:** Production Ready 🚀
