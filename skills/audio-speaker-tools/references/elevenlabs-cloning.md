# ElevenLabs Instant Voice Cloning (IVC) Best Practices

## Quick Reference

**Best settings for different voice types:**

- **Theatrical/dynamic voices**: `stability=85, similarity_boost=5`
- **Standard voices**: `stability=83, similarity_boost=10`

**Model versions:**
- **v2 (Multilingual)** > v3 for voice cloning quality
- v3 is newer but v2 produces better clones for most voices

**Sample quality:**
- **Clean, short samples** (5-30 seconds) often score better than longer ones
- Remove background noise, music, and other speakers
- Single-speaker, clear speech preferred

## Model Settings

### Stability (0-100)

Controls consistency vs. expressiveness:

- **Low (0-40)**: More variable, expressive, emotional (can drift from voice)
- **Medium (40-70)**: Balanced
- **High (70-100)**: Very consistent, less expressive (safer for cloning)

**For voice cloning:** Use high stability (80-85) to stay close to the reference voice.

### Similarity Boost (0-100)

Controls how closely the output matches the reference voice:

- **Low (0-30)**: More creative interpretation, may drift
- **Medium (40-70)**: Balanced
- **High (70-100)**: Strict adherence to reference voice

**For voice cloning:** Use moderate-to-low similarity boost (5-15) to avoid over-fitting.

### Style Exaggeration (v2 only, 0-100)

Amplifies the speaking style from the reference:

- **Low (0-30)**: Subtle style matching
- **Medium (40-70)**: Balanced
- **High (70-100)**: Exaggerated style (can sound unnatural)

**For most clones:** Use low style exaggeration (5-10) to avoid over-dramatization.

## Proven Settings

### Theatrical/Dynamic Voice
```
model: eleven_multilingual_v2
stability: 85
similarity_boost: 5
style_exaggeration: 5
```

### Standard Professional Voice
```
model: eleven_multilingual_v2
stability: 83
similarity_boost: 10
style_exaggeration: 5
```

## Sample Selection

**What makes a good voice sample:**

1. **Clean audio** - No background noise, music, or other speakers
2. **Short duration** - 5-30 seconds is often better than 60+ seconds
3. **Single speaker** - Isolated voice, not from a conversation
4. **Natural speech** - Not singing, shouting, or whispered
5. **Good recording quality** - Clear, well-recorded audio

**Pro tip:** Use `compare_voices.py` to score cloned voice against the original reference. Scores of 0.85+ indicate excellent cloning quality.

## Voice Comparison Workflow

1. **Separate speakers** from source audio using `diarize_and_slice_mps.py`
2. **Select best sample** (clean, short, single-speaker segments)
3. **Upload to ElevenLabs** as instant voice clone
4. **Generate test audio** with the clone
5. **Compare** clone vs. original using `compare_voices.py`
6. **Iterate** sample selection or settings if score < 0.85

## Model Version Comparison

| Feature | v2 (Multilingual) | v3 |
|---------|-------------------|-----|
| Clone quality | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐ Good |
| Style matching | ⭐⭐⭐⭐ Very good | ⭐⭐⭐⭐ Very good |
| Consistency | ⭐⭐⭐⭐ Reliable | ⭐⭐⭐⭐⭐ Excellent |
| Multilingual | ✓ 29 languages | ✓ 32 languages |
| Best for | Voice cloning, character voices | Consistency, production |

**Bottom line:** Use v2 for voice cloning tasks.

## Common Issues

### Clone sounds generic/flat
- **Cause:** Similarity boost too high, or stability too low
- **Fix:** Lower similarity boost to 5-10, raise stability to 80-85

### Clone drifts from reference
- **Cause:** Stability too low
- **Fix:** Raise stability to 80+

### Clone sounds over-dramatic
- **Cause:** Style exaggeration too high
- **Fix:** Lower style exaggeration to 5-10

### Clone sounds robotic
- **Cause:** Stability too high
- **Fix:** Lower stability to 75-80 for more natural variation

## Related Tools

- **compare_voices.py** - Score clone quality vs. reference (Resemblyzer)
- **diarize_and_slice_mps.py** - Extract per-speaker samples from multi-speaker audio
