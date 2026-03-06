# 🎵 Voice Note to MIDI

Convert voice memos, humming, and melodic recordings to clean, quantized MIDI files.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Transform your 3 AM melody ideas into MIDI notes for your DAW — no keyboard required.

## What It Does

```
Voice Note (WAV/M4A/MP3)
    ↓
┌─────────────────────────────────────┐
│ 1. Stem Separation (HPSS)          │
│    Isolate melody from noise         │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. Basic Pitch ML (Spotify)        │
│    Detect fundamental frequencies    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. Key Detection                    │
│    Identify musical key              │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 4. Quantization & Cleanup           │
│    • Snap to timing grid            │
│    • Key-aware pitch correction      │
│    • Harmonic pruning (octave/overlap)│
│    • Note merging (legato)          │
└─────────────────────────────────────┘
    ↓
MIDI File → Your DAW
```

## Quick Start

```bash
git clone https://github.com/DanBennettUK/voice-note-to-midi.git
cd voice-note-to-midi
./setup.sh
```

Then convert a voice memo:

```bash
hum2midi my_humming.wav          # Creates my_humming.mid
hum2midi voice.wav song.mid      # Custom output name
hum2midi hum.wav --key-aware     # Auto-detect key & quantize
```

## Features

- **ML-Powered Pitch Detection** — Spotify's Basic Pitch model
- **Key Detection** — Automatic musical key identification
- **Key-Aware Quantization** — Snap notes to detected scale
- **Harmonic Pruning** — Remove overtones, keep fundamentals
- **Legato Merging** — Combine note chunks into sustained tones
- **Configurable Grid** — 1/4, 1/8, 1/16, or 1/32 note quantization

## Usage

```bash
hum2midi <input.wav> [output.mid] [options]

Options:
  --grid <value>      Quantization: 1/4, 1/8, 1/16, 1/32 (default: 1/16)
  --min-note <ms>     Minimum note duration (default: 50ms)
  --key-aware         Enable key-aware pitch correction
  --no-quantize       Skip quantization (raw Basic Pitch output)
  --no-analysis       Skip pitch analysis
```

## Requirements

- Python 3.11+
- FFmpeg (optional but recommended)
- See `setup.sh` for full dependency installation

## Limitations

- **Monophonic only** — one note at a time (voice can't do chords)
- **Pitched audio required** — humming/singing works, whisper/"air notes" don't
- **Quality matters** — loud, clear melody = better results
- **Background noise** — can confuse pitch detection

## How It Works

The pipeline uses a multi-stage approach:

1. **HPSS** separates harmonic (melodic) content from percussive sounds
2. **Basic Pitch** neural network extracts pitch information
3. **Music21** analyzes pitch classes to detect the musical key
4. **Post-processing** cleans up harmonics and merges legato notes

## Documentation

- **Full Guide**: See [SKILL.md](SKILL.md)
- **Quick Reference**: See [QUICKSTART.md](QUICKSTART.md)
- **Setup Script**: [setup.sh](setup.sh)

## License

MIT — see [LICENSE](LICENSE)

Uses [Basic Pitch](https://github.com/spotify/basic-pitch) by Spotify, librosa, and music21.

---

Made with 🦊 for [Clawdbot](https://clawdhub.com)
