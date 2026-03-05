# Setup Instructions

## Quick Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd play-music
   ```

2. **Install dependencies**
   ```bash
   pip install pygame
   ```

3. **Add music files**
   ```bash
   mkdir music
   # Copy your music files to the music directory
   ```

4. **Make executable**
   ```bash
   chmod +x play-music
   ```

5. **Test it**
   ```bash
   ./play-music play
   ```

## Configuration Options

### Using Environment Variables

```bash
# Set custom music directory
export MUSIC_DIR="/path/to/your/music"

# Set default song
export DEFAULT_SONG="my-favorite-song.mp3"

# These settings persist for your session
./play-music play
```

### One-time Configuration

```bash
# One-time use with custom directory
MUSIC_DIR=~/Music ./play-music play

# One-time use with custom default song
DEFAULT_SONG="background.mp3" ./play-music play
```

## Integration with OpenClaw

To use this as an OpenClaw skill:

1. Copy the `play-music` folder to your OpenClaw skills directory
2. Ensure the skill is enabled in your OpenClaw configuration
3. Use the skill for music playback tasks

## Testing

Run these commands to verify everything works:

```bash
# List available songs
./play-music list

# Play default song
./play-music play

# Pause playback
./play-music pause

# Resume playback
./play-music resume

# Stop playback
./play-music stop
```

## Troubleshooting

If you encounter issues:

1. **Check pygame installation**: `python -c "import pygame; print(pygame.version.ver)"`
2. **Verify music directory**: Ensure `music` folder exists and contains audio files
3. **Check permissions**: Make sure `play-music` is executable: `chmod +x play-music`
4. **Check port conflicts**: Port 12346 should be available