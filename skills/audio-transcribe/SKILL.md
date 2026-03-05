# Audio Transcription Skill

Auto-transcribe voice messages using faster-whisper (local, no API key needed).

## Requirements

```bash
pip install faster-whisper
```

Models download automatically on first use.

## Usage

### Transcribe a file

```bash
python3 /root/clawd/skills/audio-transcribe/scripts/transcribe.py /path/to/audio.ogg
```

### Change model (edit script)

Edit `transcribe.py` and change:
```python
model = WhisperModel('small', device='cpu', compute_type='int8')  # Options: tiny, base, small, medium, large-v3
```

## Models

| Model | Size | VRAM/RAM | Speed | Use Case |
|-------|------|----------|-------|----------|
| tiny | 39 MB | ~1 GB | ⚡⚡⚡ | Quick drafts |
| base | 74 MB | ~1 GB | ⚡⚡ | Basic accuracy |
| **small** | **244 MB** | **~2 GB** | **⚡** | **Recommended** |
| medium | 769 MB | ~5 GB | 🐢 | Better accuracy |
| large-v3 | 1.5 GB | ~10 GB | 🐢🐢 | Best accuracy |

## Integration

Clawdbot auto-transcribes incoming voice messages when this skill is enabled.

## Files

- `scripts/transcribe.py` — Main transcription script
- `SKILL.md` — This file
