# 🎵 Play Music Skill

**Controlled music player with pause/resume/stop support**  
Single entry point, background server for full control

## Quick Start

1. **Place music files** in a `music` folder (default) or set `MUSIC_DIR` environment variable
2. **Install pygame** (recommended for full control): `pip install pygame`
3. **Use**: `./play-music play`

## Single Entry Point

The skill has **one clear entry point**: `./play-music`

### Command Interface
```
./play-music help          - Show this help
./play-music list          - List available songs
./play-music play          - Play default song
./play-music pause         - Pause currently playing music
./play-music resume        - Resume paused music
./play-music stop          - Stop currently playing music
./play-music status        - Show playback status
./play-music <filename>    - Play specific song (e.g., song.mp3)
./play-music server-start  - Start music server manually
./play-music server-stop   - Stop music server
```

## Examples

```bash
# Play the default song
./play-music play

# Play a specific song
./play-music song.mp3

# Control playback
./play-music pause
./play-music resume
./play-music stop

# See what's available
./play-music list
```

## Features

✅ **Single entry point** - No confusion about which script to use  
✅ **Full playback control** - Play, pause, resume, stop  
✅ **Resource-efficient** - Server auto-starts when needed, auto-stops when music stops  
✅ **Clean architecture** - Client-server separation  
✅ **Pygame-based** - High quality audio playback  
✅ **Cross-platform** - macOS/Windows/Linux compatible  

## Setup

### 1. Install Pygame (Recommended)
For full pause/resume/stop control:
```bash
pip install pygame
```

### 2. Add Music Files
Place your music files in:
- Default: `./music` (relative to script location)
- Custom: Set `MUSIC_DIR` environment variable

### 3. Configuration
```bash
# Set custom music directory
export MUSIC_DIR="/path/to/your/music"

# Set default song name
export DEFAULT_SONG="my-song.mp3"
```

## How It Works

The skill uses a clean client-server architecture:

1. **`play-music`** - Single entry point (Python script combining client functionality)
2. **`music-server.py`** - Background server that handles music playback
3. **Pygame mixer** - For high-quality audio with full control

**Resource-efficient design:** The server auto-starts when you play music and auto-shuts down when you stop music. This saves system resources while maintaining the convenience of the client-server architecture.

## Troubleshooting

**"No music playing" when trying to pause/resume/stop**  
Start playing music first: `./play-music play`

**"Music directory not found"**  
Create the directory: `mkdir music` or set `MUSIC_DIR` environment variable

**"Pygame not installed"**  
Install it: `pip install pygame`

**Server won't start**  
Check if port 12346 is available, or kill existing servers:
```bash
pkill -f "music-server.py"
./play-music server-start
```

## File Structure

```
play-music/
├── play-music           # Single entry point (Python script)
├── music-server.py      # Background server
├── SKILL.md            # This documentation
├── README.md           # User documentation
├── _meta.json          # Skill metadata
└── .gitignore          # Git ignore file
```

**Clean and minimal** - No redundant files, clear structure.

## Integration with OpenClaw

When this skill is registered with OpenClaw, use it for music playback tasks. The skill provides the knowledge and tools to control music playback with pause/resume/stop support.