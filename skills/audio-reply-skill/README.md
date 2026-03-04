# Audio Reply Skill for Claude Code

A Claude Code skill that generates spoken audio responses using local TTS. Runs entirely on your machine with [MLX Audio](https://github.com/Blaizzy/mlx-audio) - no cloud API calls, no usage limits.

## Features

- **"read it to me [URL]"** - Fetches public web content from a URL and reads it aloud
- **"talk to me [topic]"** - Generates a conversational spoken response
- **"speak" / "say it" / "voice reply"** - Converts any response to audio

## Requirements

- macOS with Apple Silicon (M1/M2/M3/M4)
- [Claude Code](https://claude.ai/claude-code) CLI
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

1. **Install uv** (prefer package manager install):
   ```bash
   brew install uv
   ```
   If Homebrew is unavailable, use the official Astral installer from [astral.sh](https://astral.sh/uv).

2. **Copy the skill to your Claude Code skills directory**:
   ```bash
   mkdir -p ~/.claude/skills/audio-reply
   cp SKILL.md ~/.claude/skills/audio-reply/
   ```

3. **First run will auto-download the model** (~500MB):
   ```bash
   uv run mlx_audio.tts.generate \
     --model mlx-community/chatterbox-turbo-fp16 \
     --text "Hello, testing audio." \
     --play
   ```

## Usage

Once installed, just use natural language in Claude Code:

```
> read it to me https://example.com/article
> talk to me about what's new in Python 3.12
> explain quantum computing, then speak it
```

## Security Notes

- URL fetch mode is for public `http(s)` pages only.
- Local/private targets (`localhost`, RFC1918 ranges, loopback, link-local, `.local`) should not be fetched.
- Do not use private/authenticated/signed URLs; prefer redacted public links or pasted text.
- The skill runs `uv` locally for TTS playback; install `uv` from a trusted source and verify with `command -v uv && uv --version`.
- Audio artifacts are temporary and cleaned up, but content/audio may still be retained in chat history by your client.

## How It Works

1. Claude Code detects trigger phrases ("read it to me", "talk to me", etc.)
2. For URLs: validates safety constraints, then fetches and extracts readable content
3. Generates natural conversational text
4. Runs MLX Audio TTS locally on your Mac's Neural Engine
5. Plays audio and cleans up temp files automatically

## Model

This skill uses [chatterbox-turbo-fp16](https://huggingface.co/mlx-community/chatterbox-turbo-fp16) - a fast, natural-sounding TTS model optimized for Apple Silicon via MLX.

- **Speed**: ~120 tokens/second on M-series chips
- **Quality**: Natural conversational voice with emotion support
- **Size**: ~500MB download (cached after first use)

## Links

- [MLX Audio](https://github.com/Blaizzy/mlx-audio) - The TTS framework powering this skill
- [Chatterbox Model](https://huggingface.co/mlx-community/chatterbox-turbo-fp16) - The voice model on Hugging Face
- [MLX](https://github.com/ml-explore/mlx) - Apple's ML framework for Apple Silicon

## License

MIT
