# Video Workflows by Use Case

## Content Creator (YouTube → Shorts/TikTok)

### Full Workflow
1. **Analyze** long-form video with ffprobe
2. **Identify** best moments (user provides timestamps OR analyze audio peaks)
3. **Extract** clips: `ffmpeg -ss START -t DURATION`
4. **Reframe** to 9:16 with smart crop or blur background
5. **Add captions** via Whisper → burn-in with styling
6. **Optimize** for platform (see `platforms.md`)
7. **Batch export** all clips in one operation

### Quick Commands
```bash
# Extract vertical clip with captions
ffmpeg -i long_video.mp4 -ss 00:05:30 -t 60 \
  -vf "crop=ih*9/16:ih,subtitles=captions.srt:force_style='FontSize=28'" \
  -c:v libx264 -crf 23 -c:a aac short.mp4
```

---

## Social Media Manager (Multi-Platform Distribution)

### Batch Process for All Platforms
1. Start with master video (highest quality, 16:9)
2. Export variants in parallel:
   - YouTube: Keep 16:9, add `-movflags +faststart`
   - Instagram Reels: 9:16 reframe, ≤90 sec, ≤250MB
   - LinkedIn: 16:9 or 1:1, ≤200MB recommended
   - TikTok: 9:16, ≤3 min, ≤287MB
3. Generate captions file once, apply to all
4. Add watermark to all versions

### Batch Script Pattern
```bash
for format in "youtube:1920:1080" "tiktok:1080:1920" "instagram:1080:1080"; do
  IFS=: read name w h <<< "$format"
  ffmpeg -i master.mp4 -vf "scale=$w:$h:force_original_aspect_ratio=decrease,pad=$w:$h:(ow-iw)/2:(oh-ih)/2" \
    -c:v libx264 -crf 23 output_$name.mp4
done
```

---

## Educator (Screen Recordings → Course Content)

### Processing Pipeline
1. **Capture** screen recording (OBS, QuickTime)
2. **Enhance audio**: Normalize, remove background noise
3. **Generate transcript**: Whisper → clean up → SRT
4. **Add chapters**: Split by topic or auto-detect silence gaps
5. **Optimize for LMS**: Check platform requirements (Udemy, Teachable)
6. **Compress for mobile**: 720p version for bandwidth-limited students

### Key Commands
```bash
# Normalize audio
ffmpeg -i lecture.mp4 -af "loudnorm=I=-16:TP=-1.5:LRA=11" -c:v copy normalized.mp4

# Remove silence >2 seconds
# (Requires silenceremove filter or external tool)

# Split at chapter marks
ffmpeg -i lecture.mp4 -ss 00:00:00 -t 00:15:00 -c copy chapter1.mp4
```

---

## Marketer (Ad Variants)

### A/B Testing Workflow
1. Create master ad (30-60 sec)
2. Generate variants:
   - **Length**: 6s, 15s, 30s, 60s versions
   - **Hooks**: Different first 3 seconds
   - **CTAs**: Different end cards
3. Export for each platform with correct specs
4. Create GIFs for email campaigns

### Multi-Length Export
```bash
# Extract key durations
for dur in 6 15 30; do
  ffmpeg -i master_ad.mp4 -t $dur -c:v libx264 -crf 23 ad_${dur}s.mp4
done
```

---

## Personal Use (Quick Fixes)

### Compress for Sharing
```bash
# WhatsApp (under 64MB)
ffmpeg -i video.mp4 -vf "scale=720:-2" -c:v libx264 -crf 28 -c:a aac -b:a 96k whatsapp.mp4
```

### Fix Orientation
```bash
# If video plays sideways
ffmpeg -i wrong.mp4 -vf "transpose=1" fixed.mp4
```

### Trim Quickly
```bash
# Remove first 5 sec and last 10 sec
duration=$(ffprobe -v error -show_entries format=duration -of csv=p=0 input.mp4)
end=$(echo "$duration - 10" | bc)
ffmpeg -i input.mp4 -ss 5 -t $end -c copy trimmed.mp4
```

---

## Filmmaker (Professional Workflow)

### Proxy Workflow
1. Ingest raw footage
2. Generate proxies: `scale=1280:-2 -c:v libx264 -crf 23`
3. Edit with proxies
4. Conform to original for final export

### Batch LUT Application
```bash
# Apply LUT to all clips
for f in *.mp4; do
  ffmpeg -i "$f" -vf "lut3d=my_look.cube" -c:a copy "graded_$f"
done
```

### Upscale Archive Footage
```bash
# Using Real-ESRGAN (external tool)
realesrgan-ncnn-vulkan -i old_footage.mp4 -o upscaled.mp4 -s 2
```

---

## Captioning Workflow (Universal)

### Full Pipeline
```bash
# 1. Extract audio
ffmpeg -i video.mp4 -vn -acodec pcm_s16le -ar 16000 audio.wav

# 2. Transcribe with Whisper
whisper audio.wav --model medium --output_format srt

# 3. Burn subtitles into video
ffmpeg -i video.mp4 -vf "subtitles=audio.srt" captioned.mp4

# 4. Or deliver SRT separately for platform upload
```

### Styled Captions (TikTok/Reels style)
```bash
ffmpeg -i video.mp4 -vf "subtitles=captions.srt:force_style='FontName=Arial Bold,FontSize=32,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Alignment=2'" output.mp4
```
