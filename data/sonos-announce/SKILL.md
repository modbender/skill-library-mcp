---
name: sonos-announce
version: 1.0.2
description: Play audio on Sonos with intelligent state restoration - pauses streaming, skips Line-In/TV/Bluetooth, resumes everything.
metadata:
  {
    "openclaw":
      {
        "emoji": "🔊",
        "requires":
          {
            "bins": ["python3", "ffprobe"],
            "pip": ["soco"],
          },
      },
  }
---

# Sonos Announce

Play audio files on Sonos speakers with intelligent state restoration.

## When to use

- User wants to play an announcement on Sonos
- Soundboard effects (airhorn, rimshot, etc.)
- Any audio playback that should resume previous state

**This skill handles playback only** - audio generation (TTS, ElevenLabs, etc.) is separate.

## Quick Start

```python
import sys
import os
sys.path.insert(0, '/path/to/sonos-announce')
from sonos_core import announce

# Play audio and restore previous state
# Assumes audio is in default media_dir (~/.local/share/openclaw/media/outbound)
result = announce('my_audio.mp3')
```

## Installation

```bash
pip install soco
```

Requirements:
- `python3` - Python 3
- `ffprobe` - Part of ffmpeg, for audio duration detection
- `soco` - Python Sonos library

## Core Function

```python
announce(audio_file_path, wait_for_audio=True, media_dir=None)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `audio_file_path` | str | required | Filename (if using media_dir) or full path to audio file |
| `wait_for_audio` | bool | True | Wait for audio to finish playing before returning |
| `media_dir` | str | None | Directory where audio file is located (HTTP server will serve from here) |

### Returns

```python
{
  'coordinators': 2,
  'states': {
    '192.168.1.120': {
      'uri': 'x-sonos-spotify:spotify%3atrack%3a...',
      'position': '0:01:23',
      'queue_position': 5,
      'was_playing': True,
      'is_external': False,
      'transport_state': 'PLAYING',
      'speaker_name': 'Bedroom'
    }
  }
}
```

## Usage Examples

### Simple (file in default media directory)

```python
from sonos_core import announce

# File served from default media_dir
result = announce('announcement.mp3')
```

### With custom media directory

```python
from sonos_core import announce

# Full path to audio file
result = announce(
    'my_audio.mp3', 
    media_dir='/home/user/audio/announcements'
)
```

### Full path (no media_dir)

```python
from sonos_core import announce

# Uses directory of file as media_dir
result = announce('/full/path/to/audio.mp3')
```

## Environment Variables

Configure the HTTP server for streaming to Sonos:

| Variable | Default | Description |
|----------|---------|-------------|
| `SONOS_HTTP_HOST` | auto-detected | LAN IP address (auto-detected) |
| `SONOS_HTTP_PORT` | 8888 | HTTP server port |

```bash
# Set before running (optional)
export SONOS_HTTP_HOST=192.168.1.100  # Override auto-detected IP
export SONOS_HTTP_PORT=8888           # Override port

# Or set in code before importing
import os
os.environ['SONOS_HTTP_HOST'] = '192.168.1.100'

from sonos_core import announce
announce('audio.mp3')
```

## Supported Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| macOS | ✅ Supported | Full support |
| Linux | ✅ Supported | Full support |
| Windows | ✅ Supported | Uses `taskkill` and `start /b` |

The module automatically detects your platform and uses appropriate commands for:
- Killing the HTTP server
- Starting the HTTP server in background

## State Restoration

The module intelligently restores previous playback state:

| Source Type | Behavior |
|------------|----------|
| Spotify Track | Resumed at exact position (seek) |
| Spotify Playlist | Resumed at exact position (seek) |
| Spotify Radio | Resumed from start (no seek) |
| Internet Radio | Resumed from start (no seek) |
| Line-In | Re-connected to Line-In input |
| TV/HDMI | Re-connected to TV audio |
| Bluetooth | Re-connected to Bluetooth |
| Paused content | Left paused |

### Seeking Behavior

Some streaming services don't support seeking to a specific position:
- **Can seek**: Spotify tracks, Spotify playlists, local files, queue items
- **Cannot seek**: Spotify Radio, TuneIn radio, Pandora, Tidal radio

The module automatically detects these and handles accordingly.

## External Input Detection

Automatically detects inputs that cannot be paused:

- `x-rincon:RINCON_*` - Line-In
- `x-rincon-stream:RINCON_*` - Line-In stream  
- `x-sonos-htastream:*` - TV/HDMI (Sonos Home Theater)
- `x-sonos-vanished:*` - Vanished device
- `x-rincon-bt:*` - Bluetooth

## Soundboard Example

```python
from sonos_core import announce

SOUNDS = {
    'airhorn': '/path/to/sounds/airhorn.mp3',
    'rimshot': '/path/to/sounds/rimshot.mp3',
    'victory': '/path/to/sounds/victory.mp3',
}

def play_sound(name):
    """Play a sound effect."""
    if name in SOUNDS:
        announce(SOUNDS[name])
    else:
        print(f"Unknown sound: {name}")
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No speakers found | Ensure on same network as Sonos speakers |
| Resume not working | Check speakers were playing (not paused) before announcement |
| HTTP server failed | Check port 8888 is available, or set `SONOS_HTTP_PORT` |
| Module import error | Run: `pip install soco` |
| Duration detection fails | Ensure ffprobe is installed (part of ffmpeg) |

## Files

- `sonos_core.py` - Main module with `announce()` function
- `SKILL.md` - This documentation
