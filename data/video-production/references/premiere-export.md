# Premiere Pro Export Settings

## Why Raw/Ungraded?

Export from assembly scripts should be **completely raw**:
- ❌ No color grading
- ❌ No VFX or transitions
- ❌ No compression artifacts
- ✅ Full quality, full color depth
- ✅ Preservation of all data for pro editing

This gives you maximum flexibility in Premiere Pro.

## Export Format for Premiere

### ProRes 422 HQ (Recommended - Master)

**Best for:**
- Professional color grading
- Multi-layer VFX work
- Long-term archival

**Settings:**
```
Container: MOV
Video Codec: ProRes 422 HQ (profile 3)
Resolution: 1080p (1920x1080) or 4K (3840x2160)
Frame Rate: 24fps (cinema) or 30fps (broadcast)
Pixel Format: YUV 4:2:2 (10-bit if available)
Quality: Maximum
Audio: PCM 16-bit, 48kHz, stereo
```

**ffmpeg command:**
```bash
ffmpeg -i input.mp4 \
  -c:v prores_ks -profile:v 3 \
  -c:a pcm_s16le \
  -ar 48000 \
  -q:v 7 \
  output_MASTER.mov
```

**File size:**
- 1 minute 1080p: ~2.5 GB
- 1 minute 4K: ~10 GB

### DNxHR (Alternative - Windows-Friendly)

**Best for:**
- Windows-based editing (Avid, Premiere on Windows)
- Slightly smaller file sizes
- Professional delivery

**ffmpeg command:**
```bash
ffmpeg -i input.mp4 \
  -c:v dnxhd -profile:v dnxhr_hqx \
  -c:a pcm_s16le \
  -ar 48000 \
  output_MASTER.mov
```

**Variants:**
- `dnxhr_hqx` — Master quality (highest bitrate)
- `dnxhr_hq` — High quality (balanced)
- `dnxhr_sq` — Standard quality (smaller)

### H.265 (Efficient - Preview/Archive)

**Best for:**
- Smaller file sizes
- Preview/proxy editing
- Cloud storage

**ffmpeg command:**
```bash
ffmpeg -i input.mp4 \
  -c:v libx265 -preset slow -crf 18 \
  -c:a aac -b:a 192k \
  -ar 48000 \
  output_PROXY.mp4
```

**Quality settings:**
- `crf 18` = High quality (larger file)
- `crf 22` = Balanced (smaller file)
- `crf 28` = Preview quality (smallest)

## Resolution Options

### 1080p (Full HD)
- Resolution: 1920 × 1080
- Aspect Ratio: 16:9
- Size (1 min ProRes): ~2.5 GB
- **Use when:** YouTube, broadcast, standard viewing

### 4K (UHD)
- Resolution: 3840 × 2160
- Aspect Ratio: 16:9
- Size (1 min ProRes): ~10 GB
- **Use when:** Premium clients, cinema, future-proofing

### Vertical (Social Media)
- Resolution: 1080 × 1920 (or 2160 × 3840 for 4K vertical)
- Aspect Ratio: 9:16
- **Use when:** Instagram Stories, TikTok, Reels

## Frame Rate Options

- **24fps** — Cinema standard, artistic feel
- **25fps** — European broadcast
- **30fps** — NTSC broadcast, American standard
- **60fps** — High frame rate, smooth motion

**Recommendation:** Stay at 24fps (cinema standard) unless client specifies otherwise.

## In Premiere Pro Workflow

### 1. Create New Sequence
```
File → New → Sequence
Resolution: Match your export (1920×1080 or 3840×2160)
Frame Rate: 24fps
Audio Format: 48kHz, 16-bit stereo
```

### 2. Import Raw Video
```
File → Import → output_MASTER.mov
Drag into Timeline
```

### 3. Color Grading
```
Lumetri Panel (or third-party plugins)
├─ Basic Correction (exposure, contrast, saturation)
├─ Curves (tone curves per color channel)
├─ HSL (hue, saturation, lightness per color)
└─ LUTs (color lookup tables for specific looks)
```

**Recommended LUTs:**
- Kodachrome (warm, vintage look)
- Agfa (cool, film-like)
- Fujicolor (saturated, cinematic)
- Custom LUTs from online libraries

### 4. Add VFX/Transitions
```
Effects Panel
├─ Transitions (dissolves, wipes, etc)
├─ Effects (color, distortion, blur)
└─ Adjustment Layers (apply effects to multiple clips)
```

### 5. Audio Mixing
```
Audio Track Mixer
├─ Balance VO vs. Music levels
├─ Add compression/EQ if needed
└─ Export with audio

Recommended levels:
VO: -3.0 dB (slightly above music)
Music: -6.0 dB
Combined: Peak at -1.0 dB (headroom)
```

### 6. Export Final Deliverable

**YouTube/Web:**
```
Format: H.264 (MP4)
Bitrate: 15-25 Mbps (1080p) or 50-100 Mbps (4K)
Audio: AAC, 192 kbps, 48kHz
```

**Cinema/Archival:**
```
Format: ProRes 422 HQ
Quality: Maximum
Audio: PCM 16-bit
```

**Social Media (Instagram/TikTok):**
```
Resolution: 1080×1920 (vertical)
Format: H.264 (MP4)
Bitrate: 10-15 Mbps
Audio: AAC, 128 kbps
```

## Common Premiere Settings by Use Case

### Professional Cinema
- Video: ProRes 422 HQ, 1080p or 4K, 24fps
- Audio: PCM 16-bit, 48kHz
- Format: MOV
- Color Space: Rec.709 (for HDR: Rec.2020)

### YouTube/Streaming
- Video: H.265, 1080p/4K, 24fps
- Audio: AAC, 192-256 kbps
- Format: MP4
- Bitrate: 15-25 Mbps (1080p), 50-100 Mbps (4K)

### Instagram/Social
- Video: H.264, 1080×1920, 30fps
- Audio: AAC, 128 kbps
- Format: MP4
- Bitrate: 10 Mbps

### Archive/Distribution
- Video: ProRes or DNxHR, 1080p/4K, 24fps
- Audio: PCM 16-bit, 48kHz
- Format: MOV
- Storage: External SSD or cloud (ProRes = 2-10 GB/min)

## File Organization

```
PROJECT/
├── RAW/
│   └── output_MASTER.mov          ← Import this to Premiere
├── EXPORTS/
│   ├── final_cinema.mov           ← ProRes (archive)
│   ├── final_youtube_4k.mp4       ← H.265 4K
│   ├── final_youtube_1080.mp4     ← H.265 1080p
│   └── final_instagram.mp4        ← H.264 vertical
└── PREMIERE_PROJECT/
    ├── project.prproj
    └── Media Cache/
```

## Troubleshooting

**File too large after color grading**
- Check export settings, ensure H.265 or ProRes (not uncompressed)
- Reduce resolution if needed

**Color changes between Premiere and export**
- Ensure output color space matches project (Rec.709)
- Check "Export colorspace" in Premiere export dialog

**Audio out of sync after export**
- Verify timeline audio sample rate = 48kHz
- Re-sync in Premiere before final export

**Premiere crashes on import**
- Try ProRes Proxy instead of HQ (Premiere → File → Create Proxy)
- Reduce timeline resolution temporarily
