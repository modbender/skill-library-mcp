# Rendering Guide

How to turn Strudel compositions into audio files. This is the first thing you'll do and the first thing you'll get wrong.

## The Renderer

One renderer: `offline-render-v2.mjs`. This is the only path that works reliably for headless/agent use.

```bash
node src/runtime/offline-render-v2.mjs <composition.js> <output.wav> <cycles> <bpm>
```

**Parameters:**
- `composition.js` — path to a Strudel composition file
- `output.wav` — output WAV path (44.1kHz, 16-bit stereo)
- `cycles` — number of Strudel cycles to render (see "Cycles vs Bars" below)
- `bpm` — beats per minute

**Then convert to MP3:**
```bash
ffmpeg -i output.wav -codec:a libmp3lame -b:a 192k output.mp3
```

## Cycles vs Bars

A Strudel cycle = 1 bar in most compositions. If your composition is 64 bars at 60 BPM:

```
CPS = BPM / 60 / 4 = 0.25 cycles per second
Duration = cycles / CPS = 64 / 0.25 = 256 seconds = 4:16
```

Set cycles equal to the number of bars your composition expects. If your gain arrays have 64 entries (one per bar), use 64 cycles.

## Duration Targets

Radio edit length = 2:30 – 4:30. Work backwards:

| BPM | Bars for ~3:00 | Bars for ~4:00 |
|-----|----------------|----------------|
| 60  | 45             | 60             |
| 90  | 68             | 90             |
| 120 | 90             | 120            |
| 128 | 96             | 128            |

## LUFS Targets

Target: **-16 to -14 LUFS** for streaming-ready audio.

Check with:
```bash
ffmpeg -i output.mp3 -af loudnorm=print_format=json -f null /dev/null 2>&1 | grep "input_i"
```

If too quiet (below -20 LUFS), you have two options:
1. **Increase gains in the composition** — the right fix
2. **Post-render loudnorm** — the quick fix:
```bash
ffmpeg -i output.wav -af loudnorm=I=-16:TP=-1.5:LRA=11 -codec:a libmp3lame -b:a 192k output-norm.mp3
```

Option 2 works but collapses dynamic range. Fix the gains when you can.

## Common Rendering Issues

### Low hap count ("Scheduled 41/448 haps")

This happens with ambient compositions using high `.slow()` values (4, 8, 16). Each hap has a very long duration, so fewer are scheduled per cycle boundary. This is **normal for ambient work** — a `.slow(16)` voice only triggers once every 16 cycles.

Check: if your composition uses `.slow(8)` or higher, a low scheduled/total ratio is expected. Listen to the output before assuming it's broken.

### Silent output

Usually means:
1. **Sample not found** — check that the sample directory exists in `samples/` and matches the `s("name")` in the composition
2. **Gains too low** — see GAIN-CALIBRATION.md
3. **Wrong cycle count** — too few cycles means voices with late entries (bar 45 of 64) never trigger

### Clipping / distortion

True peak above -1.0 dBFS. Reduce gains or add a limiter:
```bash
ffmpeg -i output.wav -af "alimiter=limit=0.9:attack=5:release=50" output-limited.wav
```

## The Legacy Codepath

`render.mjs` → `synth.mjs` is the older path. It exists in the repo but `offline-render-v2.mjs` supersedes it for all composition rendering. The legacy path has known issues with slice boundary seams. Use `offline-render-v2.mjs`.

## Quick Reference

```bash
# Compose, render, convert, check
node src/runtime/offline-render-v2.mjs src/compositions/my-track.js output/my-track.wav 64 120
ffmpeg -y -i output/my-track.wav -codec:a libmp3lame -b:a 192k output/my-track.mp3
ffmpeg -i output/my-track.mp3 -af loudnorm=print_format=json -f null /dev/null 2>&1 | grep -E "input_i|input_tp|input_lra"
```
