# Loudness Standards by Platform

## Podcasts

| Platform | Target LUFS | True Peak | Notes |
|----------|-------------|-----------|-------|
| Spotify | -14 LUFS | -1 dB | Will normalize louder files down |
| Apple Podcasts | -16 LUFS | -1 dB | Recommended by Apple |
| Google Podcasts | -16 LUFS | -1 dB | |
| YouTube | -14 LUFS | -1 dB | |
| General Standard | -16 LUFS | -1.5 dB | Safe for all platforms |

**Recommendation:** Target -16 LUFS for podcasts — it works everywhere.

```bash
# Podcast normalization
ffmpeg -i input.mp3 -af "loudnorm=I=-16:TP=-1.5:LRA=11" output.mp3

# Or with ffmpeg-normalize (more accurate)
ffmpeg-normalize input.mp3 -o output.mp3 -t -16 -tp -1.5
```

---

## Music Streaming

| Platform | Target LUFS | True Peak | Behavior |
|----------|-------------|-----------|----------|
| Spotify | -14 LUFS | -1 dB | Loud=normalizes down, quiet=normalizes up |
| Apple Music | -16 LUFS | -1 dB | Sound Check feature |
| YouTube Music | -14 LUFS | -1 dB | |
| Amazon Music | -14 LUFS | -2 dB | |
| Tidal | -14 LUFS | -1 dB | |
| Deezer | -15 LUFS | -1 dB | |

**Recommendation:** Master at -14 LUFS for streaming distribution.

---

## Broadcast

| Standard | Target LUFS | True Peak | Region |
|----------|-------------|-----------|--------|
| EBU R128 | -23 LUFS | -1 dB | Europe |
| ATSC A/85 | -24 LKFS | -2 dB | USA broadcast |
| ARIB TR-B32 | -24 LKFS | -1 dB | Japan |

---

## Social Media

| Platform | Recommendation | Notes |
|----------|----------------|-------|
| Instagram/Reels | -14 LUFS | Matches music streaming |
| TikTok | -14 LUFS | |
| Facebook | -14 LUFS | |
| Twitter/X | -14 LUFS | |

---

## Understanding LUFS

**LUFS** = Loudness Units Full Scale

- Measures *perceived* loudness, not just peak levels
- More accurate than peak normalization for consistent listening experience
- Negative values (like -16 LUFS) — closer to 0 = louder

**LRA** = Loudness Range
- Measures dynamic variation
- Lower LRA = more compressed sound
- Podcasts: LRA 5-10 is comfortable
- Music: LRA 8-15 is typical

**True Peak**
- The actual maximum amplitude
- Must stay below 0 dB to avoid clipping
- -1 dB to -1.5 dB provides safety margin

---

## Measuring Loudness

```bash
# Analyze loudness without processing
ffmpeg -i input.mp3 -af "loudnorm=print_format=summary" -f null -

# Output shows:
# Input Integrated: -20.5 LUFS
# Input True Peak: -0.3 dBTP
# Input LRA: 12.8 LU
```

---

## Common Mistakes

| Mistake | Problem | Solution |
|---------|---------|----------|
| Mastering too loud (-8 LUFS) | Platform turns it down anyway, loses dynamics | Target platform's standard |
| Not checking true peak | Digital clipping on some players | Keep TP below -1 dB |
| Inconsistent episode levels | Listeners adjust volume constantly | Use same target for all episodes |
| Only peak normalizing | Perceived loudness varies widely | Use LUFS-based normalization |
