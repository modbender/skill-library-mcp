---
name: pronunciation-coach
description: Pronunciation coaching with real voice analysis using Azure Speech Services. Analyzes audio files for phoneme-level accuracy, fluency, prosody, and intonation scores.
env:
  AZURE_SPEECH_KEY: Azure Speech Service API Key
  AZURE_SPEECH_REGION: Azure Speech Service Region (e.g., southeastasia)
---

# Pronunciation Coach

Analyze spoken English pronunciation using Azure Speech Services and provide actionable coaching feedback.

**Privacy Note**: This skill reads local voice messages from `~/.openclaw/media/inbound/` and transmits them to Microsoft Azure Speech Services for processing.

## Prerequisites

- **Azure Speech API Key**: Set `AZURE_SPEECH_KEY` env var
- **Azure Speech Region**: Set `AZURE_SPEECH_REGION` env var (e.g., `southeastasia`)
- **ffmpeg**: Required for audio format conversion (must be on PATH)
- **Node.js**: Required for report generation

## Workflow

### 1. Receive Audio

Voice messages from Telegram are stored in `~/.openclaw/media/inbound/`. Find the latest `.ogg` file matching the message timestamp.

```bash
ls -lt ~/.openclaw/media/inbound/*.ogg | head -5
```

### 2. Run Assessment

```bash
scripts/pronunciation-assess.sh <audio_file> "<reference_text>"
```

- `audio_file`: Path to the voice message (ogg/wav/mp3/m4a)
- `reference_text`: What the speaker intended to say (from transcript)
- The script auto-converts any format to WAV 16kHz mono

### 3. Generate Report

Pipe the JSON output into the report generator:

```bash
scripts/pronunciation-assess.sh audio.ogg "reference text" | node scripts/pronunciation-report.js
```

The report includes:
- Overall scores (Pronunciation, Accuracy, Fluency, Prosody, Completeness)
- Word-by-word breakdown with per-phoneme scores
- Problem sounds highlighted
- Verdict with actionable next steps

### 4. Provide Coaching

After generating the report:

1. **Send the text report** to the user (scores + word breakdown)
2. **Identify top 3 problem sounds** from the phoneme scores
3. **Explain each problem** — what the correct sound is and how to produce it
   - See `references/phoneme-guide.md` for phoneme descriptions and fixes
4. **Send a voice message** (via TTS) demonstrating the correct pronunciation of problem words
5. **Assign practice** — give the user specific sentences to re-record focusing on weak sounds

### Coaching Tips

- Scores ≥ 90: Excellent, minor polish
- Scores 70-89: Good, targeted practice needed
- Scores < 70: Needs focused drill on that specific sound
- "Omission" errors mean the word wasn't detected — speaker may have been too quiet or mumbled
- Prosody score < 85 suggests monotone delivery — coach on intonation rises/falls
- Compare scores across multiple recordings to track improvement
