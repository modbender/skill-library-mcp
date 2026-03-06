# Video Quality Guide

## CRF (Constant Rate Factor) — H.264

| CRF | Quality | Use Case |
|-----|---------|----------|
| 18 | Visually lossless | Archive, master copies |
| 20 | Excellent | YouTube uploads |
| 23 | Good (default) | General purpose |
| 26 | Acceptable | Smaller files needed |
| 28 | Noticeable degradation | WhatsApp, aggressive compression |
| 30+ | Poor | Only if desperate for size |

**Rule:** Lower CRF = better quality, larger file

---

## Preset Speed vs Quality

| Preset | Encoding Speed | File Size | Quality |
|--------|---------------|-----------|---------|
| ultrafast | Fastest | Largest | Lowest |
| fast | Fast | Large | Lower |
| medium | Balanced | Medium | Medium |
| slow | Slow | Smaller | Higher |
| veryslow | Very slow | Smallest | Highest |

**Recommendation:** Use `slow` for final exports, `fast` for tests/drafts

---

## Audio Quality

| Bitrate | Quality | Use Case |
|---------|---------|----------|
| 64 kbps | Low | Voice only, heavy compression |
| 96 kbps | Acceptable | Mobile, small files |
| 128 kbps | Good | Standard distribution |
| 192 kbps | High | YouTube, podcasts |
| 256+ kbps | Excellent | Music, professional |

**Always use AAC** for maximum compatibility

---

## Resolution vs Bitrate Guidelines

| Resolution | Minimum Bitrate | Recommended |
|------------|-----------------|-------------|
| 720p | 1.5 Mbps | 3-5 Mbps |
| 1080p | 3 Mbps | 5-10 Mbps |
| 1440p (2K) | 6 Mbps | 10-15 Mbps |
| 2160p (4K) | 13 Mbps | 20-35 Mbps |

---

## File Size Estimation

Rough formula: `File Size (MB) ≈ (Video Bitrate + Audio Bitrate) × Duration (seconds) / 8 / 1000`

**Quick targets:**
- 60 sec × 5 Mbps ≈ 37 MB
- 60 sec × 2 Mbps ≈ 15 MB
- 60 sec × 1 Mbps ≈ 7.5 MB

---

## When to Use Two-Pass Encoding

Use for **target bitrate/file size** requirements:

```bash
# Pass 1 (analysis)
ffmpeg -i input.mp4 -c:v libx264 -b:v 1M -pass 1 -f null /dev/null

# Pass 2 (encode)
ffmpeg -i input.mp4 -c:v libx264 -b:v 1M -pass 2 output.mp4
```

**When:**
- Strict file size limits (WhatsApp, email)
- Broadcast/platform specs require exact bitrate

---

## Essential Flags

| Flag | Purpose |
|------|---------|
| `-movflags +faststart` | Web playback (move moov atom to start) |
| `-pix_fmt yuv420p` | Maximum compatibility |
| `-profile:v main` or `baseline` | Older device support |
| `-level 4.0` | Broad compatibility (up to 1080p) |

---

## Quality Checklist Before Delivery

- [ ] File plays in VLC and QuickTime
- [ ] Duration matches expected
- [ ] File size under platform limit
- [ ] Audio audible and synced
- [ ] No artifacts or corruption at start/end
- [ ] Correct aspect ratio displays

---

## Common Problems and Fixes

**File too large:**
- Increase CRF (23 → 26)
- Reduce resolution (1080p → 720p)
- Use two-pass with target bitrate

**Won't play on some devices:**
- Add `-pix_fmt yuv420p`
- Use `-profile:v baseline -level 3.0`

**Audio out of sync:**
- Re-encode both streams (don't copy)
- Use `-async 1` or `-af aresample=async=1`

**Playback starts slow:**
- Add `-movflags +faststart`
