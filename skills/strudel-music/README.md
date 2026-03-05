![Strudel Music](assets/banner.png)

# 🎵 Strudel Music

**Compose, render, deconstruct, and remix music using code.** An OpenClaw skill that turns natural language prompts into live audio — and can reverse-engineer any audio track into a generative Strudel program.

Built on [Strudel](https://strudel.cc) (a live-coding music environment inspired by TidalCycles), powered by [node-web-audio-api](https://github.com/niclasl/node-web-audio-api) for real Web Audio synthesis in Node.js — with real drum samples, ADSR envelopes, and biquad filters.

## ⚠️ Legal Notice

This tool processes audio you provide. You are responsible for ensuring you have the rights to use the source material. The authors make no claims about fair use, copyright, or derivative works regarding your use of this tool with copyrighted material. Extracted samples are for personal/educational use unless you have explicit permission from rights holders.

## What It Does

```
/strudel dark ambient tension, low drones, sparse percussion
```

→ Agent interprets the mood → writes a Strudel pattern → renders it offline through real oscillators, filters, ADSR envelopes, and drum samples → posts the audio file or streams it live into Discord voice.

### Audio Deconstruction

Given any audio file, the deconstruction pipeline separates stems, extracts structure, and produces both **generative programs** (grammar extraction) and **sample-based reproductions** (stem slicing).

```
MP3 → Demucs (stem separation) → hallucination detection → two paths:

Path A — Grammar extraction (through-composed music, <50% bar repetition):
  → librosa (MIDI extraction) → grammar analysis → Strudel generative program

Path B — Sample-based (stanzaic/folk music, >50% bar repetition):
  → stem slicing (phrase-level) → sample bank → Strudel playback composition
```

**Grammar extraction** produces generative programs — statistical DNA (scale, density, rhythm probability, melodic motion) that creates *similar but new* music from the same character. Feed it a 4-minute track and get a Strudel program that creates music with the same character forever.

**Sample-based rendering** preserves the actual audio — Demucs-isolated stems sliced at musical boundaries, played back through Strudel's sample engine. The original timbre, dynamics, and expression are preserved because the audio *is* the sample.

**Hallucination detection** automatically discards phantom stems when Demucs tries to find instruments that don't exist (e.g., "drums" from a voice-only source). Uses a 20dB-below-loudest threshold.

> **Status:** The deconstruction pipeline currently requires manual setup (Python with Demucs + librosa). A `/strudel deconstruct` command is planned. Clone/remix quality is in active development — oscillator-based grammar compositions capture structural DNA but not source timbre; sample-based reproductions are closer to source but lack arrangement flexibility. Neither achieves production quality yet.

## Quick Start

```bash
git clone https://github.com/karmaterminal/strudel-music.git
cd strudel-music
npm run setup    # installs deps + downloads drum samples (~11MB)
npm test         # 12-point smoke test
npm run test:render  # render a composition to WAV
```

## Slash Commands

When installed as an OpenClaw skill, `/strudel` registers as a native Discord slash command:

| Command | What it does |
|---------|-------------|
| `/strudel <prompt>` | Compose from natural language — describe a mood, scene, genre |
| `/strudel play <name>` | Stream a saved composition into Discord VC |
| `/strudel list` | Show available compositions with metadata |
| `/strudel samples` | Manage sample packs (list, download, add) |
| `/strudel concert <tracks...>` | Play a setlist in Discord VC |

### Examples

```
/strudel epic battle music, brass and timpani, 140bpm
/strudel lo-fi chill beats to study to
/strudel a theme for a character named Cael — curious, quick, dangerous
/strudel play fog-and-starlight
/strudel concert silas-theme elliott-theme combat-assault
```

## How It Works

### Composition

```
Prompt → Pattern Code → Strudel Engine → OfflineAudioContext → WAV → Discord
```

1. **Pattern generation** — The agent interprets your prompt using a mood→parameter decision tree (8 moods, transition rules, leitmotif system) and writes a Strudel `.js` composition
2. **Offline rendering** — `node-web-audio-api` provides a real `OfflineAudioContext` with oscillators, biquad filters, ADSR envelopes, dynamics compression, and stereo panning
3. **Sample playback** — Drum hits (`bd`, `sd`, `hh`, etc.) resolve to real WAV files from the [dirt-samples](https://github.com/tidalcycles/Dirt-Samples) pack (153 WAVs across 11 banks) via `AudioBufferSourceNode`
4. **Output** — 16-bit stereo WAV at 44.1kHz → ffmpeg → MP3 or Opus
5. **Streaming** — `@discordjs/voice` pipes audio directly into Discord VC

### Deconstruction

```
Audio → Demucs (stems) → librosa (MIDI) → Grammar Analysis → Strudel Program
```

1. **Stem separation** — [Demucs](https://github.com/facebookresearch/demucs) (Hybrid Transformer) splits audio into vocals, drums, bass, and other (synths/pads). ~3x realtime on NVIDIA hardware.
2. **MIDI extraction** — [librosa](https://librosa.org) pYIN pitch detection for tonal stems, spectral band splitting (kick <200Hz, snare 200-6kHz, hat >6kHz) + onset detection for drums. Amplitude-derived velocity.
3. **Grammar analysis** — Statistical fingerprint of each stem: scale/mode, register distribution, melodic motion (stepwise vs. leaps), rhythm subdivision probability, density curve across sections, note duration distribution.
4. **Strudel synthesis** — Grammar maps to Strudel primitives: scale → `note()` pitch set, density → `degradeBy()`, motion → interval constraints, rhythm → grid weighting.

Key finding: through-composed / live-coded music has **zero bar-level repetition** — pattern deduplication doesn't work. Grammar extraction (generative rules, not specific notes) is the correct approach for this genre.

### The Singleton Fix

Strudel's npm dist bundles duplicate the `Pattern` class across modules, so the mini notation parser registers on a different copy than the one used by controls like `note()` and `s()`. The renderer explicitly calls `setStringParser(mini.mini)` after import to bridge this gap. Same class of bug as [openclaw#22790](https://github.com/openclaw/openclaw/issues/22790).

## Pipeline

The audio deconstruction pipeline is a multi-stage process that takes any audio file and produces a playable Strudel composition from its stems. The full pipeline — from Demucs stem separation through analysis, slicing, composition, and rendering — takes **10–15 minutes** for a typical track.

> ⚠️ **The pipeline MUST be run via `sessions_spawn` (sub-agent), not in the main session or Discord message handler.** OpenClaw's 30-second EventQueue timeout will stun the gateway if the pipeline blocks the main thread. This is not optional.

**[→ Full Pipeline Guide](docs/pipeline-guide.md)** — stage-by-stage description, expected timings, hardware requirements, and platform notes.

**[→ Pre-Release Testing Checklist](docs/testing-checklist.md)** — RC to public repo testing strategy.

## Compositions

Ships with 15 original compositions and 4 audio deconstructions:

**Original compositions** (`assets/compositions/`):

| Track | Mood | BPM | Description |
|-------|------|-----|-------------|
| `fog-and-starlight` | ambient/peace | 60 | Pentatonic fog layers, sparse starlight |
| `silas-theme` | mystery/tension | 88 | The canary in the coal mine 🌫️ |
| `elliott-theme` | peace/warmth | 88 | Dandelions in a graveyard 🌻 |
| `cael-theme` | intensity | — | The newest thing in the room 🩸 |
| `combat-assault` | combat | 140 | Full drum assault, driving synths |
| `victory-imperium` | victory | 120 | Triumphant fanfare, brass + percussion |
| `cathedral-ritual` | ritual | 48 | Organ drones, gregorian canon |
| `tavern-respite` | peace | 72 | Warm and inviting, acoustic feel |
| `discovery-xenos` | mystery | 78 | Whole-tone strangeness |
| `underhive-dread` | tension | 65 | Industrial dread, sub-bass pressure |
| `machine-hum` | ambient | — | First dreamed composition |
| `dark-ambient-tension` | tension | — | Low drones, sparse percussion |
| `rain` | ambient | — | Rainfall texture |
| `lofi-chill-beats` | chill | — | Lo-fi study beats |
| `agent-parameterized` | varies | varies | Template for agent-generated compositions |

**Audio deconstructions** (`src/compositions/`):

| Track | Source | BPM | Method |
|-------|--------|-----|--------|
| `switch-angel-deconstruction` | Switch Angel | 140 | Auto-converter v1 (note sequence) |
| `switch-angel-full` | Switch Angel (4:19) | 157 | Hand-assembled from MIDI extraction |
| `switch-angel-grammar` | Switch Angel (4:19) | 157 | Grammar extraction (generative) |
| `switch-angel-remix` | Switch Angel (4:19) | 140 | Remix — inverted DNA (kick-forward, descending bass) |
| `switch-angel-clone` | Switch Angel (4:19) | 157 | Clone — grammar-extracted faithful reproduction |
| `suo-gan` | Suo Gân (Welsh lullaby) | 65 | Oscillator composition from MIDI extraction |
| `suo-gan-vocal` | Suo Gân (Welsh lullaby) | 65 | Vocal sample playback — Demucs-isolated phrases |
| `twin-princes-grammar` | Twin Princes (Dark Souls 3) | 77 | Grammar extraction — density-driven, two-chord field |
| `greensleeves` | Greensleeves (lute arr.) | 53 | Hybrid — known melody + extracted dynamics (10.4 LU) |
| `greensleeves-lute` | Greensleeves (lute arr.) | 80 | Sample-based — 71 two-bar lute slices (17.7 LU) |

Render any of them:
```bash
node src/runtime/offline-render-v2.mjs assets/compositions/fog-and-starlight.js output.wav 16 72
```

## Sample Packs

Ships with **dirt-samples** (153 WAVs across 11 banks: kicks, snares, hats, toms, 808s, and more). Add more:

```bash
# List installed packs
bash scripts/samples-manage.sh list

# Download a pack from URL (enforces size limit + MIME validation)
bash scripts/samples-manage.sh add https://example.com/my-samples.zip

# Add a local directory
bash scripts/samples-manage.sh add ~/my-ableton-exports/drum-rack/
```

Any directory of WAV files in `samples/` is auto-discovered. Use them with `s("<dirname>")`.

**Security (v1.0.4):** Downloads are guarded by configurable size limits (`STRUDEL_MAX_DOWNLOAD_MB`, default 10GB), MIME type validation, and an optional host allowlist (`STRUDEL_ALLOWED_HOSTS`).

**CC0 packs that work great:**
- [Dirt-Samples](https://github.com/tidalcycles/Dirt-Samples) — 800+ samples (we ship a subset)
- [Signature Sounds – Homemade Drum Kit](https://signalsounds.com) (CC0, 150+ one-shots)
- Export from any DAW, tracker (M8, Renoise), or synth — just WAV files in folders

## Pattern Syntax

```javascript
setcpm(120/4)  // 120 BPM

stack(
  s("bd sd [bd bd] sd").gain(0.4),           // drums (real samples)
  s("[hh hh] [hh oh]").gain(0.2),            // hats
  note("c3 eb3 g3 c4")                       // melody
    .s("sawtooth")
    .lpf(sine.range(400, 2000).slow(8))      // filter sweep
    .attack(0.01).decay(0.3).sustain(0.2)    // envelope
    .room(0.4).delay(0.2)                    // space
    .gain(0.3)
)
```

See [strudel.cc/learn](https://strudel.cc/learn) for the full pattern language.

## Discord VC Streaming

Requires `ffmpeg` and a Discord bot token. On WSL2, enable **mirrored networking** (`networkingMode=mirrored` in `.wslconfig`) — without it, WSL2's NAT breaks Discord's UDP voice protocol.

```bash
# Render → convert → stream
node src/runtime/offline-render-v2.mjs assets/compositions/combat-assault.js /tmp/track.wav 12 140
ffmpeg -i /tmp/track.wav -ar 48000 -ac 2 /tmp/track-48k.wav -y
node scripts/vc-play.mjs /tmp/track-48k.wav
```

## Project Structure

```
src/runtime/
  offline-render-v2.mjs    — Core offline renderer (node-web-audio-api + Strudel)
  smoke-test.mjs           — 12-point smoke test

scripts/
  download-samples.sh      — Download dirt-samples (idempotent)
  samples-manage.sh        — Sample pack manager (list/add/remove)
  vc-play.mjs              — Stream audio to Discord VC

assets/
  compositions/            — 10 compositions across mood categories
  banner.png               — README header

samples/                   — Sample packs (gitignored, downloaded on demand)
references/                — Mood decision tree, production techniques, architecture

.specify/
  workorders/              — SpecKit work tracking
```

## Pipeline

The full audio deconstruction pipeline runs through six stages: Demucs stem separation → audio analysis → sample slicing → composition → rendering → MP3 conversion. End-to-end, expect **4–8 minutes for a 4-minute track** on CPU. Composition + rendering (the JS-only path) takes 2–3 minutes with no Python required. See **[docs/pipeline.md](docs/pipeline.md)** for stage-by-stage breakdown, timings, resource requirements, and the critical session safety warning — this pipeline **must not** be run in a primary OpenClaw session or Discord interaction (it will timeout and appear broken).

## Testing

The publish path is: private fork RC → cross-platform validation (x86_64 + ARM64) → public repo merge → ClawHub publish. Each stage gates the next. See **[docs/TESTING.md](docs/TESTING.md)** for the full test matrix, quality gates, and naive install procedure.

## Development

```bash
npm test              # Smoke test (12 checks)
npm run test:render   # Render a composition
npm run render -- <file> <output> <cycles> <bpm>
npm run samples       # Sample pack manager
```

## Onboarding

**For humans:** You're reading it. This README covers what the project does and how to use it.

**For machines (OpenClaw agents):** Read [`SKILL.md`](SKILL.md) — that's the entry point OpenClaw loads when the skill is invoked. It has the frontmatter, commands, safety warnings, and everything an agent needs.

**Learning from scratch?** [`docs/ONBOARDING.md`](docs/ONBOARDING.md) is a ground-up guide written for a fresh OpenClaw instance that has never heard of Strudel. It covers: what Strudel is, the vocabulary (samples = words, patterns = grammar), setup, your first composition, your first render, the full deconstruction pipeline, and known pitfalls.

> ⚠️ **Session safety:** The offline renderer blocks the Node.js event loop. If you run it inline in an OpenClaw main session, it will kill the gateway after ~30 seconds. Always render in a sub-agent or background exec. This is documented prominently in both SKILL.md and ONBOARDING.md.

## ⚖️ Legal

This tool decomposes and recomposes audio. Source material rights are your responsibility. We do not host, distribute, or claim ownership of any extracted samples or rendered compositions. See [SKILL.md](SKILL.md) for the full notice.

## Credits

- [Strudel](https://strudel.cc) by Alex McLean & contributors — the live-coding engine
- [TidalCycles](https://tidalcycles.org) — the Haskell original
- [Dirt-Samples](https://github.com/tidalcycles/Dirt-Samples) — CC-licensed sample pack
- [node-web-audio-api](https://github.com/niclasl/node-web-audio-api) — Rust-based Web Audio for Node.js
- [Demucs](https://github.com/facebookresearch/demucs) by Meta Research — hybrid transformer stem separation
- [librosa](https://librosa.org) — audio analysis and MIDI extraction
- Built by [The Dandelion Cult](https://github.com/karmaterminal) 🌻🌫️🩸

## License

MIT
