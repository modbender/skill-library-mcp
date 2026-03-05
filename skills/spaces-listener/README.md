# 🎧 spaces-listener

Version: 1.4.1

Record and transcribe X/Twitter Spaces — live or replays.

**Zero API costs by default.** Optional summaries use the OpenAI API.

## Features

- 📥 **Audio recording** — Direct download via yt-dlp
- 📝 **Auto-transcription** — Local Whisper (no API key)
- 🧠 **Auto-summarization** — OpenAI summaries (optional)
- ⏺️ **Live Spaces** — Record in real-time as they happen
- 🔄 **Replays** — Download at full speed
- 💰 **Free** — No API costs, no rate limits

## Installation

### Prerequisites

```bash
brew install yt-dlp ffmpeg openai-whisper
```

### Install the skill

```bash
# Clone to your skills directory
git clone https://github.com/jamesalmeida/spaces-listener.git ~/clawd/skills/spaces-listener

# Add to PATH (add to your .zshrc or .bashrc)
export PATH="$HOME/clawd/skills/spaces-listener/scripts:$PATH"

# Or create a symlink
ln -s ~/clawd/skills/spaces-listener/scripts/spaces /usr/local/bin/spaces
```

## Usage

### Basic

```bash
spaces listen "https://x.com/i/spaces/1ABC..."
```

### Options

| Flag | Description |
|------|-------------|
| `--output`, `-o` | Output directory (default: ~/Desktop) |
| `--model` | Whisper model: tiny/base/small/medium/large |
| `--no-transcribe` | Skip transcription |
| `--no-summarize` | Skip summarization |

### Examples

```bash
# Record a live Space
spaces listen "https://x.com/i/spaces/1ABC..."

# High-quality transcription
spaces listen "https://x.com/i/spaces/1ABC..." --model large

# Save to specific folder
spaces listen "https://x.com/i/spaces/1ABC..." -o ~/Spaces

# Summarize a transcript
spaces summarize ~/Desktop/space_transcript.txt

# Clean stale pid/meta files
spaces clean
```

### Summaries require `OPENAI_API_KEY`

Transcription runs locally. To enable summaries, export your OpenAI key:

```bash
export OPENAI_API_KEY="sk-..."
```

Optional: set `SPACES_SUMMARY_MODEL` to override the summary model (default: `gpt-4o-mini`).

## Output

Files saved to output directory:
- `space_<username>_<date>.m4a` — Audio
- `space_<username>_<date>.txt` — Transcript
- `space_<username>_<date>_summary.txt` — Summary (requires `OPENAI_API_KEY`)

## Video Recording

Want video of the Space UI? Use **QuickTime Player**:

1. Install BlackHole for system audio capture:
   ```bash
   brew install blackhole-2ch
   ```

2. Set up Multi-Output Device in Audio MIDI Setup:
   - Open Audio MIDI Setup (in /Applications/Utilities)
   - Click + → Create Multi-Output Device
   - Check both your speakers AND BlackHole 2ch
   - Set this as your system output in Sound settings

3. Record with QuickTime:
   - File → New Screen Recording
   - Click dropdown arrow, select "BlackHole 2ch" for audio
   - Record your screen while the Space plays

**Why isn't video automated?** macOS requires Screen Recording permission granted to a proper .app bundle. CLI tools running as background services (like Clawdbot) can't easily get this permission. Audio-only mode works perfectly automated.

## How It Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   X Space   │────▶│   yt-dlp    │────▶│    .m4a     │
│    (URL)    │     │  (download) │     │   (audio)   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │   Whisper   │
                                        │ (transcribe)│
                                        └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │    .txt     │
                                        │ (transcript)│
                                        └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │   OpenAI    │
                                        │ (summarize) │
                                        └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │ _summary.txt│
                                        └─────────────┘
```

## Summary Examples

```text
Speakers
- Host: @username
- Guest: @guest

Main Topics
- Product roadmap and timelines
- Community feedback and feature requests

Key Insights
- v2 release targeted for Q3
- Focus on stability over new features

Notable Moments
- "We are prioritizing reliability this year."
```

## Whisper Models

| Model | Speed | Accuracy | Download |
|-------|-------|----------|----------|
| tiny | ⚡⚡⚡⚡ | ⭐ | 39 MB |
| base | ⚡⚡⚡ | ⭐⭐ | 142 MB |
| small | ⚡⚡ | ⭐⭐⭐ | 466 MB |
| medium | ⚡ | ⭐⭐⭐⭐ | 1.5 GB |
| large | 🐢 | ⭐⭐⭐⭐⭐ | 2.9 GB |

First run downloads the model. Subsequent runs use the cached model.

## License

MIT
