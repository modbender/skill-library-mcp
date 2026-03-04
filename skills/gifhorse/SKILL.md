---
name: gifhorse
description: Search video dialogue and create reaction GIFs with timed subtitles. Perfect for creating meme-worthy clips from movies and TV shows.
homepage: https://github.com/Coyote-git/gifhorse
metadata: {"clawdbot":{"emoji":"🐴","requires":{"bins":["gifhorse","ffmpeg"]},"install":[{"id":"gifhorse-setup","kind":"shell","command":"git clone https://github.com/Coyote-git/gifhorse.git ~/gifhorse && cd ~/gifhorse && python3 -m venv venv && source venv/bin/activate && pip install -e .","bins":["gifhorse"],"label":"Install gifhorse CLI tool"},{"id":"ffmpeg-full","kind":"shell","command":"brew install ffmpeg-full","bins":["ffmpeg"],"label":"Install FFmpeg-full (macOS)"}],"config":{"examples":[{"GIFHORSE_DB":"~/gifhorse/transcriptions.db"}]}}}
---

# GifHorse - Dialogue Search & GIF Creator

Create reaction GIFs from your video library by searching dialogue and adding timed subtitles.

## What GifHorse Does

1. **Transcribe videos** - Extract dialogue with timestamps by downloading subtitles, using local .srt files, or Whisper AI
2. **Search dialogue** - Find quotes across your entire video library instantly
3. **Preview clips** - See exactly what will be captured before creating the GIF
4. **Create GIFs** - Generate GIFs with perfectly timed subtitles and optional watermarks

## Setup

### First Time Setup

1. Install gifhorse (via install button above)
2. Install FFmpeg-full for subtitle rendering (via install button above)
3. Transcribe your video library (downloads subtitles automatically):

```bash
cd ~/gifhorse && source venv/bin/activate
gifhorse transcribe ~/Movies
```

The gifhorse command must be run from within its virtual environment. You can activate it with:

```bash
cd ~/gifhorse && source venv/bin/activate
```

Or use the activation helper:

```bash
source ~/gifhorse/activate.sh
```

## Available Commands

### Transcribe Videos

Extract dialogue from your videos (one-time per video):

```bash
# Default: downloads subtitles from online providers (fast, recommended)
gifhorse transcribe /path/to/videos

# Use only local .srt files (no downloading, no Whisper)
gifhorse transcribe /path/to/videos --use-subtitles

# Use Whisper AI (slow but works for any video)
gifhorse transcribe /path/to/video.mp4 --use-whisper

# Re-transcribe videos already in database
gifhorse transcribe /path/to/videos --force
```

### Download Subtitles Only

Download .srt files without storing in the database:

```bash
gifhorse fetch-subtitles /path/to/videos
gifhorse fetch-subtitles /path/to/videos --skip-existing
```

### Search Dialogue

Find quotes across your entire library:

```bash
# Basic search
gifhorse search "memorable quote"

# Search with surrounding context
gifhorse search "memorable quote" --context 2

# Show all results (no limit)
gifhorse search "memorable quote" --all

# Custom result limit (default: 100)
gifhorse search "memorable quote" --limit 50
```

### Preview Before Creating

See exactly what will be captured:

```bash
gifhorse preview "memorable quote" 1
gifhorse preview "quote" 1 --include-before 1 --include-after 1
```

### Create GIF

Generate the GIF with subtitles:

```bash
# Basic GIF (auto-named from dialogue, saved to exports/)
gifhorse create "memorable quote" 1

# Explicit output path
gifhorse create "memorable quote" 1 -o reaction.gif

# High quality for social media
gifhorse create "quote" 1 --width 720 --fps 24 --quality high

# Include conversation context
gifhorse create "quote" 1 --include-before 2 --include-after 1

# Substitute words in subtitles (repeatable, target segments by number from preview)
gifhorse create "the age of men" 1 --include-after 1 \
  -s 1 "men" "standardized software" \
  -s 2 "orc" "custom applications"

# Clean replace (no strikethrough)
gifhorse create "quote" 1 -r 1 "old word" "new word"

# Create and send via iMessage
gifhorse create "quote" 1 --send
gifhorse create "quote" 1 --send-to "+15551234567"
```

### Manage Database

```bash
# Remove videos by path pattern (SQL LIKE wildcards)
gifhorse remove "%Adventure Time%"
gifhorse remove "%S01%" --yes

# Check subtitle status for a directory
gifhorse subtitle-status ~/Videos
gifhorse subtitle-status ~/Videos --missing-only
```

### Check Status

```bash
# See transcription stats
gifhorse stats

# List all transcribed videos
gifhorse list
```

### Configuration

```bash
# Set phone number for iMessage sending
gifhorse config --set-phone "+15551234567"

# Show current configuration
gifhorse config --show
```

## Timing Options

Control exactly what gets captured:

- `--include-before N` - Include N dialogue segments before the match
- `--include-after N` - Include N dialogue segments after the match
- `--padding-before SECS` - Add buffer seconds before dialogue starts (default: 1.0)
- `--padding-after SECS` - Add buffer seconds after dialogue ends (default: 1.0)
- `--start-offset SECS` - Manual adjustment to start time (can be negative)
- `--end-offset SECS` - Manual adjustment to end time (can be negative)

**Important:** For reactions after dialogue, use `--padding-after` instead of `--include-after`. The include-after option captures ALL time until the next dialogue segment (could be 30+ seconds!).

## Quality Options

- `--quality low|medium|high` - Color palette quality (affects file size)
- `--fps N` - Frames per second (default: 15, use 24 for smooth)
- `--width N` - Width in pixels (default: 480, use 720 for HD)

## Subtitle Options

- `-s, --sub NUM OLD NEW` - Substitute words in a segment (repeatable). Replaced words render struck through in red, replacements in red. Segment numbers shown by `preview`.
- `-r, --replace NUM OLD NEW` - Replace words cleanly (no strikethrough). Repeatable.
- `--no-subtitles` - Create GIF without subtitle overlay

## Output

- Default output filename is auto-derived from dialogue text (e.g., `i_dont_think_so.gif`) and saved to `exports/`
- Use `-o PATH` to override. Collision handling appends `_2`, `_3`, etc.

## iMessage

- `--send` - Send created GIF to configured phone number via iMessage (macOS only)
- `--send-to NUMBER` - Send to a specific phone number (overrides config)

**Note:** All GIFs automatically include a subtle "gifhorse" watermark in the bottom-right corner.

## Common Workflows

### Quick Reaction GIF

```bash
gifhorse search "perfect"
gifhorse create "perfect" 1 --padding-after 2.0
```

### Full Conversation Exchange

```bash
gifhorse search "key phrase"
gifhorse preview "key phrase" 1 --include-before 2 --include-after 1
gifhorse create "key phrase" 1 --include-before 2 --include-after 1
```

### Meme with Word Substitution

```bash
gifhorse preview "the age of men" 1 --include-after 1
gifhorse create "the age of men" 1 --include-after 1 \
  -s 1 "men" "standardized software" \
  -s 2 "orc" "custom applications"
```

### High Quality for Twitter/X

```bash
gifhorse create "quote" 1 --width 720 --fps 24 --quality high -o tweet.gif
```

### Scene with Reaction After Dialogue

```bash
gifhorse create "memorable line" 1 --padding-after 3.0
```

### Create and Send via iMessage

```bash
gifhorse config --set-phone "+15551234567"
gifhorse create "quote" 1 --send
```

## Tips & Tricks

1. **Always preview first** - Use `preview` to verify timing before creating
2. **Default downloads subtitles** - Just run `gifhorse transcribe` and subtitles are fetched automatically
3. **Watch file sizes** - High quality + long duration = large files (20s can be 20+ MB)
4. **Padding vs Include** - For reactions, use `--padding-after` not `--include-after`
5. **Search with context** - Add `--context 2` to see surrounding dialogue
6. **Re-transcribe with --force** - Use `--force` to update transcriptions after getting better subtitles
7. **Check subtitle coverage** - Use `subtitle-status` to see which videos need subtitles

## File Size Guide

- **Low quality, 10s, 360p:** ~1-2 MB
- **Medium quality, 10s, 480p:** ~3-5 MB
- **High quality, 20s, 720p:** ~20+ MB

## Troubleshooting

### "command not found: gifhorse"

Activate the virtual environment:

```bash
cd ~/gifhorse && source venv/bin/activate
```

### Subtitle rendering errors

Make sure FFmpeg-full is installed:

```bash
brew install ffmpeg-full
```

### Video file not found

The database stores absolute paths. If you moved videos after transcription, re-transcribe in the new location.

## Network Share Support

GifHorse works with network-mounted videos:

```bash
# Mount network share (macOS)
open "smb://server-ip/share-name"

# Transcribe from network
gifhorse transcribe "/Volumes/server-ip/Movies"
```

## When to Use This Skill

Invoke gifhorse when the user wants to:
- Search for dialogue or quotes in their video library
- Create a reaction GIF from a movie or TV show
- Make a meme GIF with substituted words
- Add subtitles to a video clip
- Transcribe videos for searchable dialogue
- Preview what a GIF will look like before creating it
- Send a GIF via iMessage
- Remove videos from the database
- Check subtitle status for their video collection

## Learn More

- **GitHub:** https://github.com/Coyote-git/gifhorse
- **Usage Guide:** https://github.com/Coyote-git/gifhorse/blob/main/USAGE_GUIDE.md
- **Roadmap:** https://github.com/Coyote-git/gifhorse/blob/main/ROADMAP.md

## License

MIT
