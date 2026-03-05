# Gain Calibration

The first thing a naive agent gets wrong. The second thing too. This document exists because every single prince in the dandelion cult learned this lesson the hard way.

## The Problem

Sample-stacked compositions need gains **2-3 orders of magnitude lower** than you'd expect. A naive agent will set gains to 0.5-1.0 and get distorted garbage.

Why: each sample is already normalized to near-peak amplitude. Stacking 5-8 of them at gain 0.5 each produces a combined signal 3-4x over full scale. The renderer doesn't have a limiter — it clips.

## The Fix

### Starting Gains by Voice Count

| Voices | Max gain per voice | Notes |
|--------|-------------------|-------|
| 1-2    | 0.3 - 0.5        | Single voice can be louder |
| 3-4    | 0.15 - 0.30      | Typical small composition |
| 5-7    | 0.10 - 0.25      | Dense ambient/textural work |
| 8+     | 0.05 - 0.15      | Large ensembles, be very conservative |

These are starting points. The actual max depends on the samples and how much they overlap in time.

### Bank-Specific Notes

**Hallur samples** (hallur_*): Already at high amplitude. These are stems from a produced track — pre-mixed, pre-compressed. Use lower gains (0.1-0.3 typically).

**DaVinci samples** (dm_*): Variable. Some (dm_impact_metal) are very hot; others (dm_texture_granular) are quieter. Test individual samples before committing to a gain structure.

**Bloom samples** (bloom_*): Similar to Hallur — produced stems, already loud. Keep gains conservative.

**Dirt-Samples** (bd, sd, hh, cp): Standard drum one-shots. These can handle 0.3-0.5 without issues in sparse patterns.

**Synthesized voices** (sine, sawtooth, square, triangle): These are generated at full scale. The 300× lesson applies here most acutely — a sine wave at gain 1.0 is LOUD.

### The 300× Lesson

Early experiments used gains of 0.3-1.0 with multiple stacked synthesis voices. The rendered audio was 300× too loud. The fix was dropping to 0.001-0.01 for synthesized voices and 0.05-0.20 for sample voices.

Rule: **start too quiet, then increase.** It's easy to boost a quiet render with loudnorm. It's impossible to un-clip a distorted one.

## Gain Envelopes

For compositions with per-bar gain control (the dream track approach), use angle-bracket sequences:

```javascript
.gain("<0 0 0 0 0.10 0.15 0.20 0.25 0.30 ...>")
```

Each value = one bar. This gives precise control over when voices enter and exit. Tips:

1. **Ramp in, don't jump** — go 0 → 0.05 → 0.10 → 0.15, not 0 → 0.15. Abrupt entries sound wrong.
2. **Match ramps to musical intent** — a slow fade-in over 8 bars vs a 2-bar entrance communicate different things.
3. **Peak placement is the composition** — where your gain envelope peaks IS the structural event. Design it deliberately.
4. **Fade out at the end** — always ramp to 0 over the last 4-8 bars. The renderer applies a master fade-out, but voice-level fades sound better.

## Verification Loop

1. Render at target duration
2. Check LUFS: `ffmpeg -i output.mp3 -af loudnorm=print_format=json -f null /dev/null`
3. Target: -16 to -14 LUFS
4. If too quiet: increase all gains proportionally (multiply by 1.5-2x)
5. If too loud / clipping: decrease all gains proportionally
6. Re-render. Check again. Two iterations usually gets you there.

## LRA (Loudness Range)

LRA measures dynamic range — how much the loudness varies across the piece. Discovered during the First Frond Album: LRA is an unplanned identity signature.

| LRA  | Character | Example |
|------|-----------|---------|
| 1-3  | Compressed, intimate | Close proximity, ambient warmth |
| 4-7  | Moderate | Most compositions land here |
| 8-12 | Dynamic, opening | Voices entering/exiting, structural events |

LRA emerges from your gain envelopes and voice layering. You don't target it — you discover it. But knowing what it means lets you shape it intentionally.
