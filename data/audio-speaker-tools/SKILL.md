---
name: audio-speaker-tools
description: "Speaker separation, voice comparison, and audio processing tools. Use when working with multi-speaker audio, voice cloning, or speaker verification tasks including: (1) separating speakers from audio files via Demucs and pyannote diarization, (2) comparing voice samples for speaker verification or voice clone quality assessment using Resemblyzer, (3) extracting audio segments, (4) preparing samples for ElevenLabs voice cloning, or (5) validating speaker diarization results."
---

# Audio Speaker Tools

Tools for speaker separation, voice comparison, and audio processing using Demucs, pyannote, and Resemblyzer.

## Overview

This skill provides three main workflows:

1. **Speaker separation** - Extract per-speaker audio from multi-speaker recordings
2. **Voice comparison** - Measure speaker similarity between two audio files
3. **Audio processing** - Segment extraction and voice isolation

## Prerequisites

### Setup Virtual Environment

Run once to create the venv and install dependencies:

```bash
bash scripts/setup_venv.sh
```

Default venv location: `./.venv`

**Requirements:**
- Python 3.9+
- ffmpeg (`brew install ffmpeg`)
- HuggingFace token (set as env var `HF_TOKEN`)

## Scripts

### 1. Speaker Separation: `diarize_and_slice_mps.py`

Separate speakers from multi-speaker audio:

```bash
# Basic usage
HF_TOKEN=<your-hf-token> \
  /path/to/venv/bin/python scripts/diarize_and_slice_mps.py \
  --input audio.mp3 \
  --outdir /path/to/output \
  --prefix MyShow

# With speaker constraints
HF_TOKEN=$TOKEN python scripts/diarize_and_slice_mps.py \
  --input audio.mp3 \
  --outdir ./out \
  --min-speakers 2 \
  --max-speakers 5 \
  --pad-ms 100
```

**Process:**
1. Converts input to 16kHz mono WAV
2. Runs Demucs vocal/background separation (optional, for cleaner input)
3. Runs pyannote speaker diarization (MPS-accelerated)
4. Extracts concatenated per-speaker WAV files

**Output:**
- `<prefix>_speaker1.wav`, `<prefix>_speaker2.wav`, etc. (one per detected speaker)
- `diarization.rttm` (time-stamped speaker segments)
- `segments.jsonl` (JSON segments metadata)
- `meta.json` (pipeline info and speaker index)

**Important:**
- **Always pass HF token via `HF_TOKEN` env var**, never as CLI arg
- **MPS first, CPU fallback** - Script prefers Metal GPU, falls back to CPU if unavailable
- Default output: `./separated/`

### 2. Voice Comparison: `compare_voices.py`

Measure similarity between two voice samples using Resemblyzer:

```bash
# Basic comparison
python scripts/compare_voices.py \
  --audio1 sample1.wav \
  --audio2 sample2.wav

# JSON output
python scripts/compare_voices.py \
  --audio1 reference.wav \
  --audio2 clone.wav \
  --threshold 0.85 \
  --json

# Exit code = 0 if pass, 1 if fail
```

**Scores:**
- `< 0.75` = Different speakers
- `0.75-0.84` = Likely same speaker
- `0.85+` = Excellent match (ideal for voice cloning validation)

**Use cases:**
- Voice clone quality assessment (compare clone vs. original)
- Speaker verification (authenticate speaker identity)
- Validate speaker separation (confirm separated speakers are distinct)

**See:** `references/scoring-guide.md` for detailed interpretation

### 3. Audio Trimming

Use `ffmpeg` directly for segment extraction:

```bash
# Extract 10-second segment starting at 5 seconds
ffmpeg -i input.mp3 -ss 5 -t 10 -c copy output.mp3

# Extract vocals only with Demucs (before diarization)
demucs --two-stems vocals --out ./separated input.mp3
```

## Workflows

### Workflow 1: Extract Clean Voice Sample for Cloning

**Goal:** Get a clean, single-speaker sample for ElevenLabs voice cloning

```bash
# 1. Separate speakers
HF_TOKEN=<your-hf-token> python scripts/diarize_and_slice_mps.py \
  --input podcast.mp3 --outdir ./out --prefix Podcast

# 2. Review speaker files (out/Podcast_speaker1.wav, etc.)

# 3. Select best sample (5-30s, clean speech)
ffmpeg -i out/Podcast_speaker2.wav -ss 10 -t 20 -c copy sample.wav

# 4. Upload to ElevenLabs as instant voice clone
```

**See:** `references/elevenlabs-cloning.md` for best practices

### Workflow 2: Validate Voice Clone Quality

**Goal:** Measure how well a cloned voice matches the original

```bash
# 1. Generate test audio with ElevenLabs clone
# (done via ElevenLabs web UI or API)

# 2. Compare clone vs. reference
python scripts/compare_voices.py \
  --audio1 original_sample.wav \
  --audio2 elevenlabs_clone.wav \
  --threshold 0.85 \
  --json

# 3. Interpret score:
#    0.85+ = excellent, publish-ready
#    0.80-0.84 = acceptable, may need tweaking
#    < 0.80 = poor, try different sample or settings
```

**See:** `references/scoring-guide.md` for troubleshooting low scores

### Workflow 3: Multi-Speaker Conversation Analysis

**Goal:** Separate and identify speakers in a conversation

```bash
# 1. Run diarization
HF_TOKEN=$TOKEN python scripts/diarize_and_slice_mps.py \
  --input meeting.mp3 --outdir ./out --prefix Meeting

# 2. Check detected speakers (meta.json)
cat out/meta.json

# 3. Compare speaker pairs to confirm separation
python scripts/compare_voices.py \
  --audio1 out/Meeting_speaker1.wav \
  --audio2 out/Meeting_speaker2.wav

# Expected: < 0.75 if separation worked correctly
```

## Technical Notes

### Device Acceleration
- **pyannote diarization:** MPS (Metal) by default, CPU fallback
- **Resemblyzer:** CPU only (no GPU acceleration)
- **Demucs:** MPS by default when available

To force CPU for diarization: `--device cpu`

### Audio Formats
- **Input:** Any format supported by ffmpeg (wav, mp3, flac, m4a, etc.)
- **Processing:** Internally converted to 16kHz mono WAV for diarization
- **Output:** WAV format (44.1kHz stereo preserved from source)

### HuggingFace Token
- **Required for:** pyannote speaker diarization
- **Access:** Must accept gated repo `pyannote/speaker-diarization-3.1` on HF
- **Storage:** Any secure secrets manager
- **Usage:** Always pass via `HF_TOKEN` env var, never CLI arg

### Sample Quality Tips
- **Shorter is better:** 5-30s clean samples often score higher than 60+ second samples
- **Clean audio:** Remove background noise with Demucs `--two-stems vocals`
- **Single speaker:** Ensure isolated voice, not mixed conversation
- **Good recording:** Studio mic > phone mic for voice comparison accuracy

## References

- **elevenlabs-cloning.md** - Best practices for ElevenLabs instant voice cloning (model settings, sample selection, proven configurations)
- **scoring-guide.md** - How to interpret Resemblyzer similarity scores (thresholds, use cases, troubleshooting)

## Common Issues

### "Missing HF token" error
- Export token before running: `export HF_TOKEN=<your-token>`
- Or pass inline: `HF_TOKEN=<your-token> python script.py ...`

### Low voice comparison scores for same speaker
- Try shorter, cleaner samples (5-30s)
- Use Demucs to isolate vocals: `demucs --two-stems vocals input.mp3`
- Ensure consistent recording quality (same mic, environment)
- See `references/scoring-guide.md` troubleshooting section

### Diarization not detecting all speakers
- Adjust `--min-speakers` and `--max-speakers` flags
- Check audio quality (clear speech, minimal overlap)
- Try longer audio (30+ seconds) for better speaker modeling

### MPS/Metal acceleration not working
- Ensure PyTorch with MPS support: `python -c "import torch; print(torch.backends.mps.is_available())"`
- Fallback to CPU: `--device cpu`
- Re-run `setup_venv.sh` to reinstall PyTorch
