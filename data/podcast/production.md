# Production — Audio and Video

## Audio Production

### Recording Setup
- **Microphone:** USB condenser or dynamic (SM7B, Shure MV7, Blue Yeti)
- **Environment:** Room echo ruins podcasts more than mic quality — blankets, carpets, small rooms over expensive mics
- **Separate tracks:** Record each speaker on separate tracks — can't fix crosstalk after
- **Levels:** 48kHz/24-bit for recording, export 44.1kHz/16-bit MP3
- **Loudness:** Normalize to -16 LUFS (stereo) or -19 LUFS (mono) for platform consistency
- **Backup:** ALWAYS record locally AND cloud — Riverside, Zoom both

### Remote Recording
- Each person records locally (Riverside, Squadcast, Zencastr)
- Backup: Zoom recording as fallback
- Sync with clap at start for alignment

### Audio Editing Workflow
```bash
# Normalize audio levels
ffmpeg -i input.mp3 -af "loudnorm=I=-16:TP=-1.5:LRA=11" output.mp3

# Remove silence/dead air
ffmpeg -i input.mp3 -af "silenceremove=1:0:-50dB" trimmed.mp3

# Noise reduction (requires profile)
# Use Audacity, Adobe Podcast Enhance, or Descript
```

### Standard Podcast Structure
```
[Intro music] 3-5 seconds
[Hook] 15-30 seconds
[Full intro + episode preview] 30-60 seconds
[Content] Variable
[Outro + CTA] 30-60 seconds
[Outro music] 3-5 seconds
```

### Audio Quality Checklist
- [ ] No clipping or distortion
- [ ] Consistent volume between speakers (-16 LUFS)
- [ ] No background noise/hum
- [ ] Breaths reduced (not eliminated)
- [ ] Filler words trimmed where distracting
- [ ] Music fades smooth
- [ ] Long silences removed but natural pauses kept
- [ ] Over-editing avoided — should sound natural

---

## Video Production

### Studio Setup
- **Lighting:** Key light, fill light, backlight (three-point)
- **Camera:** Eye level, slightly above, centered
- **Background:** Depth, not flat wall (shelves, plants, artwork)
- **Framing:** Rule of thirds, headroom consistent

### Multi-Camera Switching
**When to cut:**
- Speaker changes → cut to speaker
- Reaction moment → cut to listener
- Emphasis → push in
- Topic change → wide shot

### Video Editing
```bash
# Extract clips for social
ffmpeg -i full_ep.mp4 -ss 00:15:30 -t 00:00:45 clip.mp4

# Convert to vertical (9:16)
ffmpeg -i clip.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" vertical.mp4

# Add captions (burn SRT)
ffmpeg -i clip.mp4 -vf "subtitles=captions.srt:force_style='FontSize=24'" captioned.mp4
```

### YouTube Optimization
- **Thumbnail:** Expressive face + 3 words max
- **Chapters:** Add timestamps in description
- **Cards/End screens:** Link to related episodes
- **Premiere:** Schedule for community engagement

---

## Clip Creation Strategy

Every episode should generate:
- **1 trailer clip** (30-60s, best moment, hooks for full ep)
- **2-3 insight clips** (15-30s, quotable moments)
- **1 controversial/opinion clip** (drives engagement)
- **1 emotional moment** (if available)

### Clip Selection Criteria
| High value | Low value |
|------------|-----------|
| Strong opinion | Generic advice |
| Unexpected insight | Obvious statement |
| Emotional moment | Monotone delivery |
| Clear point in <30s | Needs context |
| Standalone watchable | Confusing without full ep |

### Platform Optimization
| Platform | Format | Length | Style |
|----------|--------|--------|-------|
| TikTok/Reels | 9:16 | 15-60s | Captions, hooks |
| YouTube Shorts | 9:16 | 30-60s | Captions, hooks |
| LinkedIn | 16:9 or 1:1 | 30-90s | Professional, insight |
| Twitter/X | 16:9 | 30-60s | Provocative, thread bait |

---

## Audio vs Video Decision

| Go audio-only if... | Add video if... |
|---------------------|-----------------|
| Solo format, personal brand | Interview/panel format |
| Low production capacity | YouTube strategy important |
| Intimate, commute listening | Visual demonstrations help |
| Quick turnaround needed | Clips for social are priority |
