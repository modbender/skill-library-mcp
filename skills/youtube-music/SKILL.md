---
name: youtube-music
version: 1.0.0
description: "Control YouTube Music with natural language. Play, pause, skip, search, manage playlists, and queue tracks. Full playback control via browser automation."
homepage: "https://github.com/paragshah/openclaw-youtube-music"
metadata:
  {"clawdbot":{"emoji":"🎵","category":"media","requires":{"bins":["node"],"env":["YOUTUBE_MUSIC_BROWSER_PROFILE"]}}}
---

# YouTube Music Control Skill 🎵

Control YouTube Music with natural language commands. Uses browser automation for full playback control.

## Quick Start

```bash
# No setup needed - uses OpenClaw browser
# Optional: Set default profile in TOOLS.md
```

## Commands

### Playback Control
- **Play**: "play [song name]" / "play [artist]" / "play [playlist]"
- **Pause**: "pause" / "stop"
- **Resume**: "resume" / "continue"
- **Skip**: "skip" / "next"
- **Previous**: "previous" / "back"
- **Volume**: "volume 50%" / "set volume to 80"
- **Mute**: "mute" / "unmute"

### Search & Discovery
- **Search**: "search for [query]" / "find [artist]"
- **Trending**: "what's trending" / "trending now"
- **Recommendations**: "recommend similar" / "more like this"

### Library & Playlists
- **Playlists**: "show my playlists" / "create playlist [name]"
- **Add to Playlist**: "add this to [playlist]"
- **Liked Songs**: "show liked songs" / "like this"

### Queue Management
- **Queue**: "show queue" / "what's next"
- **Add to Queue**: "queue [song]"
- **Clear Queue**: "clear queue"

### Information
- **Now Playing**: "what's playing" / "current track"
- **Lyrics**: "show lyrics" / "lyrics"
- **Artist Info**: "about [artist]"

## Usage Examples

```
"play Ye Tune Kya Kiya by Javed Bashir"
"pause the music"
"skip to next track"
"set volume to 75%"
"search for Arijit Singh hits"
"add this to my workout playlist"
"what's playing now?"
"show me the lyrics"
"queue some chill Bollywood songs"
```

## Implementation Notes

### Browser Automation
Uses OpenClaw's browser tool with YouTube Music:
- Profile: `openclaw` (isolated browser)
- Base URL: `https://music.youtube.com`
- CDP Port: 18800

### Key Selectors (Dynamic)
Selectors are resolved via snapshot refs, not hardcoded:
- Player controls: pause, play, skip, previous
- Search box: combobox with placeholder
- Volume slider: range input
- Queue: up next panel
- Lyrics: lyrics tab

### Error Handling
- Browser not running → Auto-start
- Video unavailable → Suggest alternatives
- Network issues → Retry with backoff
- No search results → Show spelling suggestions

## Advanced Features

### Smart Search
- Fuzzy matching for song names
- Artist/album disambiguation
- Auto-play top result if exact match

### Context Awareness
- Remembers last played track
- Tracks listening history
- Suggests based on time of day

### Multi-Room Support
- Cast to different devices
- Sync playback across tabs
- Group control (future)

## Configuration

Add to `TOOLS.md`:
```markdown
### YouTube Music
- Default profile: openclaw
- Preferred quality: high
- Auto-play: on
- Shuffle default: off
```

## Dependencies
- OpenClaw browser tool
- YouTube Music (music.youtube.com)
- No API keys required

## Limitations
- Requires browser to be running
- Some features need YouTube Premium
- Lyrics availability varies by region
- Queue management limited to current session

## Future Enhancements
- YouTube Music API integration (if available)
- Offline mode with cached tracks
- Cross-platform sync
- Voice control integration
- Smart playlists based on mood/activity

## Examples

### Play a Song
```
User: "play Tuna Kay Keya"
Assistant: "Found 'Ye Tune Kya Kiya' by Javed Bashir. Playing now! 🎵"
```

### Control Playback
```
User: "pause"
Assistant: "Paused. Press play to resume. ⏸️"

User: "skip"
Assistant: "Skipping to next track. ⏭️"
```

### Search & Discover
```
User: "find similar to this"
Assistant: "Based on 'Ye Tune Kya Kiya', you might like:
- 'Kaise Hua' by Vishal Mishra
- 'Aankhon Se Batana' by Dikshant
- 'Kali Kali Zulfon Ke' by Madhur Sharma"
```

### Playlist Management
```
User: "add this to my Bollywood Classics"
Assistant: "Added 'Ye Tune Kya Kiya' to 'Bollywood Classics' playlist. ✓"
```

## Testing

Test the skill with:
```bash
# Test search
"search for Pritam songs"

# Test playback
"play a sample track"
"pause"
"skip"

# Test volume
"set volume to 50%"
"mute"
"unmute"
```

---

**Skill Author:** Your AI Assistant  
**License:** MIT  
**Status:** Ready for production 🚀
